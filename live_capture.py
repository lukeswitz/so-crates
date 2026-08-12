#!/usr/bin/env python3
"""Live packet capture from the machine SO-CRATES is running on.

Capture is always an explicit, user-initiated action (the Capture button on
the Welcome screen) - nothing here ever runs at startup or as a side effect
of an analysis. tcpdump is invoked non-promiscuously (-p) so the capture
never changes the interface's mode, and every argument is validated and
passed as an argv list, never through a shell.

Requires the server's own user to already have packet-capture permission
(membership in access_bpf on macOS, CAP_NET_RAW on Linux). Nothing here
escalates privilege or invokes sudo; if that permission is missing,
capture_support() reports it as unsupported and the UI hides the button.
"""

import os
import re
import shutil
import subprocess
import sys
import time

import config

# Pseudo-interfaces that never carry ordinary host traffic.
_EXCLUDED_IFACE_PREFIXES = (
    'lo', 'utun', 'gif', 'stf', 'awdl', 'llw', 'bridge', 'ap', 'vmenet', 'anpi',
)

_IFACE_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_.-]{0,14}$')

CAPTURE_FILENAME = 'capture.pcap'

# Seconds has_capture_permission() lets its probe sit idle before concluding
# the device opened successfully.
CAPTURE_PROBE_SECONDS = 3


def _is_candidate_iface(name):
    return not name.startswith(_EXCLUDED_IFACE_PREFIXES)


def is_valid_iface_name(name):
    """Whitelist-validate an interface name before it reaches tcpdump argv."""
    return bool(name) and bool(_IFACE_RE.match(name))


def _iface_address(name):
    """Return the IPv4 address assigned to name, or None."""
    if sys.platform == 'darwin':
        try:
            out = subprocess.run(['ipconfig', 'getifaddr', name],
                                 capture_output=True, text=True,
                                 timeout=config.FILE_COMMAND_TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return None
        addr = out.stdout.strip()
        return addr or None
    try:
        out = subprocess.run(['ip', '-4', '-o', 'addr', 'show', 'dev', name],
                             capture_output=True, text=True,
                             timeout=config.FILE_COMMAND_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', out.stdout)
    return match.group(1) if match else None


def _iface_names():
    """Every up interface on the host, in the OS's own ordering."""
    if sys.platform == 'darwin':
        try:
            out = subprocess.run(['ifconfig', '-lu'], capture_output=True, text=True,
                                 timeout=config.FILE_COMMAND_TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return []
        return out.stdout.split()
    try:
        return sorted(os.listdir('/sys/class/net'))
    except OSError:
        return []


def list_interfaces():
    """Return [{'name', 'address'}] for capturable interfaces, the ones
    holding an IPv4 address first - an interface with an address is the one
    actually carrying this machine's traffic, and is what the UI should
    preselect."""
    interfaces = []
    for name in _iface_names():
        if not _is_candidate_iface(name) or not is_valid_iface_name(name):
            continue
        interfaces.append({'name': name, 'address': _iface_address(name)})
    interfaces.sort(key=lambda i: (i['address'] is None,))
    return interfaces


def default_interface(interfaces=None):
    """The first interface holding an IPv4 address, else the first candidate."""
    if interfaces is None:
        interfaces = list_interfaces()
    for iface in interfaces:
        if iface['address']:
            return iface['name']
    return interfaces[0]['name'] if interfaces else None


def has_capture_permission(interface):
    """True if this process can actually open interface for capture.

    Probed by running the real tcpdump rather than inspecting /dev/bpf*
    modes or euid: group membership, SIP, container capabilities and
    Wireshark's ChmodBPF helper all feed into the answer, and the only
    reliable check is whether the device open succeeds.

    The probe uses a filter that matches no real traffic, so tcpdump opens
    the device and then sits idle. Still running when the short probe
    timeout expires (or having printed its "listening on" banner) means the
    open succeeded; exiting immediately instead means it failed.
    """
    if not is_valid_iface_name(interface):
        return False
    try:
        proc = subprocess.Popen(
            ['tcpdump', '-p', '-i', interface, '-c', '1', '-w', os.devnull,
             'ether proto 0x9999'],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    except OSError:
        return False
    try:
        _, stderr = proc.communicate(timeout=CAPTURE_PROBE_SECONDS)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        return True
    return 'listening on' in (stderr or '')


def capture_support():
    """Report whether live capture is available, and why not when it isn't.

    Returns {'supported': bool, 'reason': str|None, 'interfaces': [...],
    'default_interface': str|None, 'max_duration': int,
    'default_duration': int}.
    """
    result = {
        'supported': False,
        'reason': None,
        'interfaces': [],
        'default_interface': None,
        'max_duration': config.CAPTURE_MAX_DURATION,
        'default_duration': config.CAPTURE_DEFAULT_DURATION,
        'host_label': 'this Mac' if sys.platform == 'darwin' else 'this host',
    }
    if shutil.which('tcpdump') is None:
        result['reason'] = 'tcpdump is not installed'
        return result

    interfaces = list_interfaces()
    result['interfaces'] = interfaces
    if not interfaces:
        result['reason'] = 'No capturable network interfaces found'
        return result

    default = default_interface(interfaces)
    result['default_interface'] = default
    if not has_capture_permission(default):
        result['reason'] = (
            'No packet-capture permission. On macOS, install Wireshark (which '
            'installs its ChmodBPF helper) or add your user to the access_bpf '
            'group, then log out and back in.'
        )
        return result

    result['supported'] = True
    return result


def _packet_count(pcap_path):
    """Packets in pcap_path per tcpdump's own reader, or None if unreadable."""
    try:
        proc = subprocess.run(['tcpdump', '-r', pcap_path, '-nn'],
                              capture_output=True, text=True,
                              timeout=config.FILE_COMMAND_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return sum(1 for line in proc.stdout.splitlines() if line.strip())


def run_capture(dest_path, interface, duration, on_progress=print,
                on_tick=None, should_stop=None):
    """Capture live traffic to dest_path, reporting progress once a second.

    on_tick(elapsed, remaining, bytes_captured) fires every second so the
    caller can publish live progress; should_stop() is polled at the same
    rate and ends the capture early while keeping whatever was captured.

    tcpdump runs with -U so each packet is flushed to the file as it
    arrives and the byte counter moves during the capture, not only at the
    end.

    Returns (success, packet_count). A capture that ends early or captures
    zero packets is still a success - an idle interface is a real answer,
    not a failure.
    """
    if not is_valid_iface_name(interface):
        raise ValueError(f'Invalid interface name: {interface}')
    duration = int(duration)
    if duration < 1 or duration > config.CAPTURE_MAX_DURATION:
        raise ValueError(f'Duration must be between 1 and {config.CAPTURE_MAX_DURATION} seconds')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    cmd = ['tcpdump', '-p', '-U', '-i', interface, '-w', dest_path]
    on_progress(f'Capturing on {interface} for {duration} seconds...')

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    except OSError as e:
        on_progress(f'Could not start tcpdump: {e}')
        return False, None

    started = time.monotonic()
    stopped_early = False
    try:
        while True:
            if proc.poll() is not None:
                break
            elapsed = time.monotonic() - started
            if elapsed >= duration:
                break
            if should_stop is not None and should_stop():
                stopped_early = True
                break
            if on_tick is not None:
                try:
                    size = os.path.getsize(dest_path)
                except OSError:
                    size = 0
                on_tick(int(elapsed), max(0, duration - int(elapsed)), size)
            time.sleep(1)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)

    stderr = proc.stderr.read() if proc.stderr else ''
    if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
        message = stderr.strip().splitlines()[-1] if stderr.strip() else 'no data was written'
        on_progress(f'Capture produced no file: {message}')
        return False, None

    if stopped_early:
        on_progress('Capture stopped early — keeping what was captured so far')
    count = _packet_count(dest_path)
    if count is None:
        on_progress('Capture finished, but the file could not be read back')
        return False, None
    on_progress(f'Captured {count} packet{"" if count == 1 else "s"} '
                f'({os.path.getsize(dest_path)} bytes) on {interface}')
    return True, count
