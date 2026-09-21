#!/usr/bin/env python3
"""Confine the external parser subprocesses SO-CRATES shells out to.

The analyzers (suricata, yara, tshark, tcpdump, file, exiftool, the Zircolite
python) parse attacker-supplied files. On macOS a deny-default sandbox-exec
profile jails each one to just the paths it needs, so a parser 0-day cannot
read the rest of the home directory or open a network connection.

No-op off macOS, when /usr/bin/sandbox-exec is absent, or when
SOCRATES_SANDBOX=0 - confine() then returns the command unchanged, so the
Linux/Docker path is byte-identical and callers need no branching.
"""

import os
import shutil
import sys
import tempfile

SANDBOX_EXEC = '/usr/bin/sandbox-exec'

# Tool install roots and the system paths a parser loads (dylibs, ICU, magic
# db, CA store). Read-only.
_SYSTEM_READ = (
    '/opt/homebrew', '/usr/local', '/usr', '/bin', '/sbin', '/System',
    '/Library', '/private/etc', '/private/var/db', '/dev',
    '/Applications/Wireshark.app',
)
_SYSTEM_EXEC = (
    '/opt/homebrew', '/usr/local', '/usr/bin', '/usr/sbin', '/usr/libexec',
    '/bin', '/sbin', '/Applications/Wireshark.app',
)


def is_active():
    return (sys.platform == 'darwin'
            and os.environ.get('SOCRATES_SANDBOX') != '0'
            and os.path.exists(SANDBOX_EXEC))


def _quote(path):
    return '"' + path.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _ancestors(path):
    out = []
    p = os.path.dirname(path)
    while p and p != '/':
        out.append(p)
        p = os.path.dirname(p)
    return out


def build_profile(read=(), write=()):
    """SBPL for a deny-default jail granting only the given read/write paths.

    Every ancestor of a granted path gets read-metadata so the kernel can
    resolve it; TMPDIR is always granted since Python and the tools stage
    scratch files there.
    """
    tmp = os.path.realpath(tempfile.gettempdir())
    read = sorted({os.path.realpath(p) for p in read} | {tmp})
    write = sorted({os.path.realpath(p) for p in write} | {tmp})
    meta = sorted({a for p in list(read) + list(write) for a in _ancestors(p)}
                  | {'/', '/private', '/private/var', '/Users', '/Applications',
                     '/tmp', '/etc', '/var'})
    def _subpaths(paths):
        return ' '.join(f'(subpath {_quote(p)})' for p in paths)

    exec_paths = _subpaths(_SYSTEM_EXEC + tuple(read))
    read_paths = _subpaths(_SYSTEM_READ + tuple(read) + tuple(write))
    write_paths = _subpaths(write)
    meta_paths = ' '.join(f'(literal {_quote(p)})' for p in meta)
    return '\n'.join((
        '(version 1)',
        '(deny default)',
        '(import "system.sb")',
        '(allow process-fork)',
        f'(allow process-exec* {exec_paths})',
        f'(allow file-read* {read_paths})',
        f'(allow file-read-metadata {meta_paths})',
        f'(allow file-write* {write_paths} (literal "/dev/null"))',
        f'(allow file-ioctl (subpath "/dev") {write_paths})',
    )) + '\n'


def confine(cmd, read=(), write=()):
    """Wrap cmd in sandbox-exec when active, else return it unchanged.

    read/write are the paths the tool legitimately touches. cmd[0] is resolved
    to an absolute path so the jailed process (no inherited PATH search) can
    still exec the tool.
    """
    cmd = list(cmd)
    if not is_active():
        return cmd
    resolved = shutil.which(cmd[0]) or cmd[0]
    cmd[0] = resolved
    profile = build_profile(read=read, write=write)
    return [SANDBOX_EXEC, '-p', profile] + cmd
