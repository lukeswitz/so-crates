#!/usr/bin/env python3
import os
import ipaddress
import socket
from urllib.parse import urlparse
import config

ALLOWED_URL_SCHEMES = ('http', 'https')
BLOCKED_HOSTS = ('localhost', '127.0.0.1', '0.0.0.0', '::1')
BLOCKED_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('::1/128'),
    ipaddress.ip_network('fd00::/8'),
    ipaddress.ip_network('::/96'),  # IPv4-compatible (::127.0.0.1)
]


def validate_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def validate_port(port_str):
    try:
        port = int(port_str)
        return 0 <= port <= 65535
    except (ValueError, TypeError):
        return False


RESERVED_FILENAMES = {
    'events.db', 'eve.json', 'name.txt', '.meta', '.phase', '.error',
}


def sanitize_filename(filename):
    """Return a safe basename, or raise ValueError for unsafe names.

    Unsafe names include:
    - path traversal sequences (. / ..)
    - empty names after stripping
    - names that collide with internal analysis files.
    """
    safe = os.path.basename(filename.replace('\\', '/'))
    if not safe or safe in ('.', '..') or safe.startswith('..'):
        raise ValueError(f'Invalid filename: {filename!r}')
    if safe in RESERVED_FILENAMES:
        raise ValueError(f'Reserved filename not allowed: {safe}')
    return safe


def is_safe_path(base, path):
    real_base = os.path.realpath(base)
    real_path = os.path.realpath(path)
    return real_path.startswith(real_base + os.sep) or real_path == real_base


def _resolve_and_validate_ips(hostname):
    """Resolve hostname to its IP addresses and reject any that are blocked.

    Returns the unique resolved IP address strings in the order getaddrinfo
    returned them (the OS/resolver's preferred order, e.g. IPv6-before-IPv4
    on dual-stack hosts) -- NOT sorted, since a plain alphabetical sort can
    put an unreachable address family first (e.g. "2001:..." sorts before
    "93.1.2.3" but the host may have no IPv6 route).
    Raises ValueError if resolution fails, times out, or any address is blocked.
    """
    try:
        # Set a 5-second timeout to prevent hanging on slow/unresponsive DNS
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(5)
        try:
            addrinfo = socket.getaddrinfo(hostname, None)
        finally:
            socket.setdefaulttimeout(old_timeout)
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {hostname}")
    except socket.timeout:
        raise ValueError(f"DNS resolution timed out for hostname: {hostname}")

    resolved_ips = list(dict.fromkeys(info[4][0] for info in addrinfo))
    for addr in resolved_ips:
        ip = ipaddress.ip_address(addr)
        # Normalize IPv4-mapped IPv6 (::ffff:127.0.0.1) so it is checked against IPv4 blocklists.
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ValueError(f"Access to private/internal addresses is not allowed ({addr})")
    return resolved_ips


def validate_url_safety(url):
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_URL_SCHEMES:
        raise ValueError("Only HTTP/HTTPS URLs are allowed")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: no hostname")

    if hostname.lower() in [h.lower() for h in BLOCKED_HOSTS]:
        raise ValueError("Access to localhost is not allowed")

    _resolve_and_validate_ips(hostname)


def resolve_safe_ips(hostname):
    """Resolve and validate hostname, returning all safe IPs to try.

    Callers that fetch a user-supplied URL must connect directly to one of
    these IPs (trying each in turn, like a normal hostname connect would)
    rather than letting the HTTP client re-resolve the hostname. Otherwise a
    DNS-rebinding attacker can return a public IP for validate_url_safety()'s
    lookup and a private/internal IP for the connection's own lookup moments
    later, bypassing the check entirely (TOCTOU). Returning every validated
    address (not just one) preserves normal multi-address fallback -- e.g. a
    dual-stack host whose IPv6 address isn't reachable but whose IPv4
    address is.
    """
    return _resolve_and_validate_ips(hostname)


def validate_zip_extraction(zip_ref, extract_path, max_size=None):
    """Validate zip-slip safety and decompressed-size limits.

    max_size defaults to config.MAX_UPLOAD_SIZE, but callers should pass the
    caller's actual resolved per-request ceiling (see
    socrates.py's _resolve_upload_size_limit) so a user who hasn't opted
    into a higher personal upload limit doesn't get the full server hard
    ceiling as their zip-bomb decompression budget.
    """
    if max_size is None:
        max_size = config.MAX_UPLOAD_SIZE
    total_uncompressed = 0
    for member in zip_ref.namelist():
        member_path = os.path.realpath(os.path.join(extract_path, member))
        if not member_path.startswith(os.path.realpath(extract_path) + os.sep):
            raise ValueError(f"Zip slip detected: {member}")
        info = zip_ref.getinfo(member)
        total_uncompressed += info.file_size
        if info.file_size > max_size:
            raise ValueError(f"ZIP member too large: {member}")
    if total_uncompressed > max_size:
        raise ValueError("ZIP contents exceed maximum allowed size")


def is_pcap_file(data):
    """Detect if file data is a PCAP or PCAPNG by magic bytes."""
    if len(data) < 4:
        return False
    magic = data[:4]
    # Classic PCAP (microsecond or nanosecond timestamps), either endianness
    if magic in (b'\xd4\xc3\xb2\xa1', b'\xa1\xb2\xc3\xd4',
                 b'\x4d\x3c\xb2\xa1', b'\xa1\xb2\x3c\x4d'):
        return True
    # PCAPNG
    if magic == b'\x0a\x0d\x0d\x0a':
        return True
    return False


def is_host_reachable(host, port, timeout=5):
    """Check if a TCP host:port is reachable.

    Returns True if connection succeeds, False otherwise.
    """
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False


LOG_EXTENSIONS = ('.evtx', '.json', '.jsonl', '.csv', '.xml', '.log')
OFFICE_EXTENSIONS = ('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                     '.docm', '.xlsm', '.pptm', '.odt', '.ods', '.odp')


def is_office_file_by_extension(filename):
    """Check if filename has a known Office document extension."""
    lower = filename.lower()
    return any(lower.endswith(ext) for ext in OFFICE_EXTENSIONS)


def _is_mostly_text(data):
    """Check if data is mostly printable text (not binary)."""
    if len(data) == 0:
        return False
    # Count printable ASCII and common whitespace bytes
    text_chars = set(bytes(range(32, 127)) + b'\t\n\r')
    text_count = sum(1 for b in data if b in text_chars)
    return text_count / len(data) > 0.7


def is_log_file(data):
    """Detect if file data is a log file by magic bytes or extension.

    Returns True if the data appears to be a supported log format.
    """
    if len(data) < 4:
        return False
    # Reject obvious binary formats first
    # OLE Compound File (legacy Office .doc/.xls/.ppt)
    if data[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        return False
    # ZIP / Office Open XML
    if data[:4] == b'PK\x03\x04':
        return False
    # PDF
    if data[:4] == b'%PDF':
        return False
    # ELF
    if data[:4] == b'\x7fELF':
        return False
    # Windows executable / DLL
    if data[:2] == b'MZ':
        return False
    # PNG
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return False
    # JPEG
    if data[:3] == b'\xff\xd8\xff':
        return False
    # GIF
    if data[:4] in (b'GIF87a', b'GIF89a'):
        return False
    # BMP
    if data[:2] == b'BM':
        return False

    # EVTX: 'ElfFile\x00'
    if data[:8] == b'ElfFile\x00':
        return True
    # JSON/JSONL: starts with { or [
    first_char = data[0:1]
    if first_char in (b'{', b'['):
        return True
    # XML: starts with <?xml or < (but not HTML, not Office Open XML)
    if data[:5] == b'<?xml':
        # Reject Office Open XML (DOCX, XLSX, PPTX, etc.)
        sample = data[:4096].decode('utf-8', errors='ignore')
        if 'schemas.openxmlformats.org' in sample:
            return False
        return True
    if data[:1] == b'<':
        # Could be XML or HTML; exclude common HTML doctype declarations
        first_line = data.split(b'\n')[0].decode('utf-8', errors='ignore').strip().lower()
        if first_line.startswith('<!doctype html') or first_line.startswith('<html'):
            return False
        return True
    # CSV: detectable by commas in first line and newline
    first_line = data.split(b'\n')[0]
    if b',' in first_line and len(first_line) < 4096 and _is_mostly_text(first_line):
        return True
    return False


def is_log_file_by_extension(filename):
    """Check if filename has a known log file extension."""
    lower = filename.lower()
    return any(lower.endswith(ext) for ext in LOG_EXTENSIONS)
