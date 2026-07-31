#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import threading

import config
from db import create_sqlite_db
from validators import is_host_reachable
from yara_analyzer import run_yara_pipeline

REQUIRED_EXECUTABLES = ['tcpdump', 'tshark', 'suricata', 'suricata-update']


def check_executables():
    """Check all required executables exist. Returns list of missing tools."""
    missing = []
    for tool in REQUIRED_EXECUTABLES:
        if shutil.which(tool) is None:
            missing.append(tool)
    return missing


def has_internet_access():
    return is_host_reachable('rules.emergingthreats.net', 80, timeout=5)


def _enable_app_layer_protocols(config_content, protocols=('pgsql', 'modbus', 'dnp3', 'enip')):
    """Enable disabled app-layer protocols in a suricata.yaml string.

    Suricata sometimes places comment lines between the protocol header and
    the `enabled:` key (e.g. modbus), so the regex tolerates intervening
    comments/blank lines.
    """
    for proto in protocols:
        config_content = re.sub(
            rf'(?m)^(\s+{proto}:\s*\n(?:\s*#.*\n)*\s+)enabled:\s*no',
            r'\1enabled: yes',
            config_content
        )
    return config_content


def _enable_eve_log_protocol_types(config_content, protocols=('modbus', 'dnp3', 'enip', 'ntp')):
    """Enable EVE logging for protocols that are supported but not logged by default.

    Suricata supports `event_type: modbus`, `event_type: dnp3`,
    `event_type: enip`, and `event_type: ntp` records, but none of them is
    listed in the default eve-log `types` block - confirmed against the
    shipped /etc/suricata/suricata.yaml (only pgsql is listed there, and it's
    disabled by default). This helper turns on the pgsql logger and adds the
    others just before the `stats` entry so they appear as standalone events.

    'enip'/'ntp' history: this app originally shipped on Suricata 7.0.10,
    where their app-layer parsers detected traffic fine (confirmed: a real
    NTP capture showed 15 flows correctly tagged app_proto=ntp) but neither
    had an eve-log *output module* compiled in at all - `No output module
    named eve-log.ntp`/`eve-log.enip` at startup, zero events regardless of
    config. Checked against Suricata's own source: rust/src/ntp/ had no
    log.rs and rust/src/enip/ didn't exist yet at the `suricata-7.0.10` tag.
    Now that this app runs on Suricata 8.0.6 (enip logging landed in 8.0.0,
    ntp logging in 8.0.5 - confirmed against those release tags), both
    loggers exist and 'enip'/'ntp' are back in the default tuple for real.
    If this ever runs against an older Suricata again, re-check for the
    `No output module` warning before assuming this config change does
    anything.

    REGRESSION (independent of the enip/ntp version history above): this
    used to be one regex requiring `- pgsql:` to be followed only by
    indented property lines up to `- stats:`. That's true only on a pristine
    config - once a previous run had already inserted bare `- modbus:` /
    `- dnp3:` header lines in between (exactly what this function itself
    does), the regex could never match again, so re-running setup on an
    already-provisioned install would silently stop adding any newly-added
    protocol at all (confirmed by reproducing it: re-running against a real
    already-processed suricata.yaml added nothing, while the same code
    worked fine against a pristine /etc/suricata/suricata.yaml). Enabling
    pgsql's logger and inserting the missing bare headers are now two
    independent, idempotent steps instead of one fragile combined regex, so
    this is safe to call repeatedly and safe to extend with new protocols
    whenever that becomes appropriate.
    """
    # Enable the pgsql logger if it is currently disabled - a no-op if it's
    # already enabled or the pgsql block isn't found.
    config_content = re.sub(
        r'(?m)(^        - pgsql:\s*\n            )enabled: no$',
        r'\1enabled: yes',
        config_content
    )

    new_types = [f'        - {p}:\n' for p in protocols
                 if f'        - {p}:' not in config_content]
    if not new_types:
        return config_content

    return re.sub(
        r'(?m)^        - stats:',
        lambda m: ''.join(new_types) + m.group(0),
        config_content,
        count=1
    )


def _enable_eve_log_arp(config_content):
    """Enable the 'arp' eve-log entry, which ships disabled by default.

    New in Suricata 8 (a decode-layer packet logger, not an app-layer
    protocol - src_mac/src_ip/dest_mac/dest_ip/opcode per ARP packet, no
    ports). Suricata's own shipped config comment says why it's off by
    default: "Many events can be logged." Unlike modbus/dnp3/enip/ntp/pgsql
    (which this app always force-enables because they're low-volume and
    clearly valuable), arp's volume/signal tradeoff on a live network is a
    real judgment call - so this is opt-in only, gated behind
    setup_suricata_config()'s enable_arp parameter (set via the
    ENABLE_ARP_LOGGING environment variable - see socrates.py's main()),
    not force-enabled for every install.
    """
    return re.sub(
        r'(?m)(^        - arp:\s*\n            )enabled: no\b',
        r'\1enabled: yes',
        config_content
    )


def _stream_suricata_update(cmd, timeout, on_progress):
    """Run suricata-update, streaming its combined stdout/stderr through
    on_progress() line by line while still enforcing timeout via a watchdog
    thread - mirrors spawn_suricata()'s Popen+watchdog idiom below, adapted
    so the timeout kill (which closes the pipe) is what unblocks the
    otherwise-unbounded `for line in proc.stdout` read loop below, rather
    than needing a separate per-line read timeout.
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    timed_out = threading.Event()

    def _kill_after_deadline():
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out.set()
            proc.kill()

    watchdog = threading.Thread(target=_kill_after_deadline, daemon=True)
    watchdog.start()
    for line in proc.stdout:
        on_progress(line.rstrip())
    proc.stdout.close()
    proc.wait()
    watchdog.join(timeout=1)
    return proc.returncode, timed_out.is_set()


def get_suricata_rules_info(data_dir=None):
    """Return {'count': int|None, 'updated': epoch|None} for the current
    Suricata ruleset. Disabled rules are '#'-commented in suricata.rules, so
    counting non-blank, non-'#' lines gives the real enabled-rule count
    (verified against suricata-update's own reported count). Never raises -
    returns None fields if the rules file doesn't exist yet."""
    if data_dir is None:
        data_dir = os.path.expanduser('~/socrates-data')
    rules_file = os.path.join(data_dir, 'suricata', 'rules', 'suricata.rules')
    if not os.path.isfile(rules_file):
        return {'count': None, 'updated': None}
    try:
        count = 0
        with open(rules_file, 'r', errors='ignore') as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    count += 1
        return {'count': count, 'updated': os.path.getmtime(rules_file)}
    except OSError:
        return {'count': None, 'updated': None}


def setup_suricata_config(data_dir=None, enable_arp=False, on_progress=print, network_allowed=True):
    """Ensure Suricata is configured and has rules available.

    Priority when network_allowed and internet is reachable: run
    suricata-update, falling back to existing on-disk rules or the
    baked-in copy if the update itself fails.

    Priority otherwise (including every server startup, which always
    calls this with network_allowed=False): existing on-disk rules take
    priority over the baked-in copy, since this path runs unconditionally
    on every restart - checking the baked-in copy first would silently
    overwrite a previously-fetched, larger/fresher ruleset every time.
    """
    if data_dir is None:
        data_dir = os.path.expanduser('~/socrates-data')
    suricata_dir = os.path.join(data_dir, 'suricata')
    suricata_rules_dir = os.path.join(suricata_dir, 'rules')

    os.makedirs(suricata_dir, exist_ok=True)
    os.makedirs(suricata_rules_dir, exist_ok=True)

    if os.path.isdir('/etc/suricata'):
        needs_copy = False
        if not os.path.exists(os.path.join(suricata_dir, 'suricata.yaml')):
            needs_copy = True

        if needs_copy:
            for item in os.listdir('/etc/suricata'):
                src = os.path.join('/etc/suricata', item)
                dst = os.path.join(suricata_dir, item)
                if os.path.isfile(src):
                    try:
                        shutil.copy2(src, dst)
                    except OSError as e:
                        on_progress(f'Warning: could not copy {src} to {dst}: {e}')
                elif os.path.isdir(src):
                    try:
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    except OSError as e:
                        on_progress(f'Warning: could not copy directory {src} to {dst}: {e}')

    suricata_config = os.path.join(suricata_dir, 'suricata.yaml')
    if os.path.exists(suricata_config):
        with open(suricata_config, 'r') as f:
            config_content = f.read()
        config_content = config_content.replace('/var/lib/suricata/rules', suricata_rules_dir)
        config_content = _enable_app_layer_protocols(config_content)
        config_content = _enable_eve_log_protocol_types(config_content)
        if enable_arp:
            config_content = _enable_eve_log_arp(config_content)
        # Enable file-store output for extracted file analysis
        config_content = re.sub(
            r'(\s+file-store:\s*\n\s+version:\s*\d+\s*\n\s+)enabled:\s*no',
            r'\1enabled: yes',
            config_content
        )
        # These five rely on Suricata's default-shipped suricata.yaml having
        # this exact commented-out text at this exact 6-space indentation
        # (matching the fragility already called out in
        # _enable_app_layer_protocols/_enable_eve_log_protocol_types/
        # _enable_eve_log_arp above) - if a future Suricata version reflows
        # this block, these become silent no-ops rather than a clean failure.
        config_content = config_content.replace('      #dir: filestore', '      dir: filestore')
        config_content = config_content.replace('      #write-fileinfo: yes', '      write-fileinfo: yes')
        config_content = config_content.replace('      #force-filestore: yes', '      force-filestore: yes')
        config_content = config_content.replace('      #stream-depth: 0', '      stream-depth: 0')
        config_content = config_content.replace('      #force-hash: [sha1, md5]', '      force-hash: [md5, sha1, sha256]')
        with open(suricata_config, 'w') as f:
            f.write(config_content)

    disable_conf = os.path.join(suricata_dir, 'disable.conf')
    # Suppress noisy protocol-command-decode event rules while still leaving
    # the protocol parsers enabled. This keeps the protocol event metadata
    # (e.g. event_type: modbus) without generating an alert for every parser
    # anomaly.
    with open(disable_conf, 'w') as f:
        f.write('re:classtype:protocol-command-decode\n')

    rules_exist = os.path.exists(os.path.join(suricata_rules_dir, 'suricata.rules'))
    baked_in_rules_dir = '/usr/share/suricata/rules'
    baked_in_rules_exist = os.path.isdir(baked_in_rules_dir) and os.path.exists(os.path.join(baked_in_rules_dir, 'suricata.rules'))

    if network_allowed:
        on_progress("Checking for internet access...")
    if network_allowed and has_internet_access():
        on_progress("Internet access detected — updating Suricata rules...")
        update_succeeded = False
        try:
            returncode, timed_out = _stream_suricata_update(
                ['suricata-update', '--no-test', '--suricata-conf', suricata_config, '--data-dir', suricata_dir, '--disable-conf', disable_conf, '--output', suricata_rules_dir],
                config.SURICATA_UPDATE_TIMEOUT,
                on_progress,
            )
            if returncode == 0:
                on_progress("Suricata rules updated successfully")
                update_succeeded = True
            elif timed_out:
                on_progress(f'suricata-update warning: timed out after {config.SURICATA_UPDATE_TIMEOUT}s')
            else:
                on_progress(f'suricata-update warning: exited with code {returncode}')
        except OSError as e:
            on_progress(f'suricata-update warning: {e}')

        if not update_succeeded:
            # The reachability probe passing doesn't guarantee
            # suricata-update itself succeeds (proxy blocking the real rule
            # mirrors, cert error, disk full, bad --data-dir permissions,
            # etc.) - fall back to whatever's already usable instead of
            # silently leaving Suricata with no rules at all, mirroring the
            # same resilience setup_yara_rules/setup_sigma_rules already
            # have. Re-check rules_exist rather than trusting the
            # pre-update value - suricata-update writes its final
            # suricata.rules near the end of a run, so a failed attempt
            # may still have left the prior good copy (or nothing) behind.
            if os.path.exists(os.path.join(suricata_rules_dir, 'suricata.rules')):
                on_progress("Using existing Suricata rules despite the failed update")
            elif baked_in_rules_exist:
                on_progress("Falling back to baked-in Suricata rules after the failed update")
                try:
                    shutil.copytree(baked_in_rules_dir, suricata_rules_dir, dirs_exist_ok=True)
                    on_progress("Baked-in rules copied successfully")
                except OSError as e:
                    on_progress(f'Warning: could not copy baked-in rules: {e}')
            else:
                on_progress("Warning: suricata-update failed and no fallback rules are available")
    elif rules_exist:
        # Rules already on disk (e.g. from a previous run's live update, in a
        # persistent DATA_DIR volume) take priority over the generic
        # baked-in snapshot - this runs unconditionally on every startup
        # (network_allowed=False), so checking baked_in_rules_exist first
        # here would silently overwrite a previously-fetched, larger/fresher
        # ruleset with the baked-in copy on every single restart.
        if network_allowed:
            on_progress("No internet access — using existing Suricata rules from a previous run")
    elif baked_in_rules_exist:
        try:
            shutil.copytree(baked_in_rules_dir, suricata_rules_dir, dirs_exist_ok=True)
        except OSError as e:
            on_progress(f'Warning: could not copy baked-in rules: {e}')
    elif network_allowed:
        on_progress("Warning: no baked-in rules found and no internet access — Suricata may not have rules to use")
    else:
        on_progress("WARNING! No Suricata rules found")


def spawn_suricata(dir_path, pcap_path, suricata_config_path=None, data_dir=None):
    """Spawn Suricata in the background to analyze a PCAP.

    Returns True if a new Suricata process was started.
    Returns False either because analysis is already in progress (a
    .phase lock exists) or because Suricata itself failed to start
    (OSError/PermissionError) - callers that need to tell these apart
    should check for a fresh .error file after a False return (only the
    startup-failure case writes one; the already-in-progress case returns
    early before ever calling _set_error/_clear_error).
    """
    if data_dir is None:
        data_dir = os.path.expanduser('~/socrates-data')
    if suricata_config_path is None:
        suricata_config_path = os.path.join(data_dir, 'suricata', 'suricata.yaml')

    phase_file = os.path.join(dir_path, '.phase')
    if os.path.exists(phase_file):
        return False

    _clear_error(dir_path)
    _set_phase(dir_path, 'network')

    def on_suricata_done():
        # Phase 2: Run YARA scan on extracted files
        _set_phase(dir_path, 'files')
        try:
            run_yara_pipeline(dir_path, data_dir=data_dir)
        except Exception as e:
            _set_error(dir_path, f'YARA scan failed: {e}')
        # Phase 3: Build SQLite database
        _set_phase(dir_path, 'importing')
        eve_file = os.path.join(dir_path, 'eve.json')
        db_file = os.path.join(dir_path, 'events.db')
        if os.path.exists(eve_file) and not os.path.exists(db_file):
            try:
                create_sqlite_db(db_file, eve_file)
            except Exception as e:
                _set_error(dir_path, f'Database creation failed: {e}')
        # Clear phase only after DB (with YARA matches) is ready
        _clear_phase(dir_path)

    try:
        proc = subprocess.Popen(
            ['suricata', '-r', pcap_path, '-c', suricata_config_path,
             '-l', dir_path,
             '-k', 'none', '--runmode', 'single',
             '--set', 'outputs.1.eve-log.types.0.alert.metadata.rule.raw=true'],
            cwd=dir_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        def _suricata_watchdog():
            """Kill Suricata if it runs longer than the configured timeout."""
            try:
                proc.wait(timeout=config.SURICATA_RUN_TIMEOUT)
            except subprocess.TimeoutExpired:
                proc.kill()
                _set_error(dir_path, f'Suricata timed out after {config.SURICATA_RUN_TIMEOUT}s')
                _clear_phase(dir_path)
                return
            on_suricata_done()

        threading.Thread(target=_suricata_watchdog, daemon=True).start()
        return True
    except (OSError, PermissionError) as e:
        _set_error(dir_path, f'Suricata failed to start: {e}')
        _clear_phase(dir_path)
        return False


def _set_phase(dir_path, phase):
    """Write the current analysis phase to the .phase file."""
    phase_file = os.path.join(dir_path, '.phase')
    try:
        with open(phase_file, 'w') as f:
            f.write(phase)
    except OSError:
        pass


def _clear_phase(dir_path):
    """Remove the .phase file to indicate analysis is complete."""
    phase_file = os.path.join(dir_path, '.phase')
    try:
        if os.path.exists(phase_file):
            os.unlink(phase_file)
    except OSError:
        pass


def _set_error(dir_path, message):
    """Write an error message to the .error file."""
    error_file = os.path.join(dir_path, '.error')
    try:
        with open(error_file, 'w') as f:
            f.write(message)
    except OSError:
        pass


def _clear_error(dir_path):
    """Remove the .error file."""
    error_file = os.path.join(dir_path, '.error')
    try:
        if os.path.exists(error_file):
            os.unlink(error_file)
    except OSError:
        pass
