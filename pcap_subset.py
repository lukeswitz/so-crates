"""Copying chosen packets out of a capture, for tshark's second passes
(shark_analyzer._subset): the packets of the flows a protocol needs, by
frame number - tshark's numbering, the capture's packets counted from 1.

editcap does this too, but takes at most 512 frame ranges, and a
protocol's packets scattered through a long capture make thousands; this
takes any number, and stops reading once past the last one. It reads
classic pcap (microsecond and nanosecond, either byte order) and pcapng;
for anything else (a compressed capture, or a pcapng with records tshark
numbers as frames that aren't packets) it copies nothing and says so, and
the caller falls back to editcap.
"""
import os
import struct

# Classic pcap's magic numbers, as the file's first four bytes: the byte
# order its headers are written in
_PCAP_MAGICS = {b'\xd4\xc3\xb2\xa1': '<', b'\xa1\xb2\xc3\xd4': '>',      # microsecond timestamps
                b'\x4d\x3c\xb2\xa1': '<', b'\xa1\xb2\x3c\x4d': '>'}      # nanosecond
_PCAP_HEADER, _PCAP_RECORD = 24, 16
_PCAPNG_SECTION = b'\x0a\x0d\x0d\x0a'
_PCAPNG_BYTE_ORDER = 0x1A2B3C4D
# pcapng blocks that are a packet - a frame: enhanced, simple and the
# obsolete packet block.
_PCAPNG_PACKETS = {6, 3, 2}
# Blocks that are no frame, copied as they are: interfaces, names,
# statistics, decryption secrets, custom blocks. tshark numbers some other
# records as frames too (a systemd journal export, sysdig's events), so a
# capture with any block not named here isn't copied - frame numbers
# would come out shifted - and the caller falls back to editcap.
_PCAPNG_NOT_FRAMES = {1, 4, 5, 0x0A, 0x0BAD, 0x40000BAD}


class _Unsupported(Exception):
    pass


class _Selection:
    """Whether each frame, taken in order, falls in the ranges."""

    def __init__(self, ranges):
        self.ranges, self.i = ranges, 0

    def done(self):
        return self.i >= len(self.ranges)

    def wants(self, frame):
        while self.i < len(self.ranges) and frame > self.ranges[self.i][1]:
            self.i += 1
        return self.i < len(self.ranges) and frame >= self.ranges[self.i][0]


def copy_frames(src, dst, ranges):
    """Copy src's packets whose frame numbers fall in ranges (sorted,
    non-overlapping (first, last) pairs) to dst, in src's own format.
    False - and dst not written - if src isn't classic pcap or pcapng."""
    with open(src, 'rb') as f:
        magic = f.read(4)
        if magic in _PCAP_MAGICS:
            copy = _copy_pcap
        elif magic == _PCAPNG_SECTION:
            copy = _copy_pcapng
        else:
            return False
        f.seek(0)
        try:
            with open(dst, 'wb') as out:
                copy(f, out, _Selection(sorted(ranges)))
        except _Unsupported:
            os.unlink(dst)
            return False
    return True


def _copy_pcap(f, out, selection):
    order = _PCAP_MAGICS[f.read(4)]
    f.seek(0)
    out.write(f.read(_PCAP_HEADER))
    record = struct.Struct(order + 'IIII')
    frame = 0
    while not selection.done():
        header = f.read(_PCAP_RECORD)
        if len(header) < _PCAP_RECORD:
            break
        length = record.unpack(header)[2]
        frame += 1
        if selection.wants(frame):
            data = f.read(length)
            out.write(header + data)
            if len(data) < length:
                break
        else:
            f.seek(length, 1)


def _copy_pcapng(f, out, selection):
    order = '<'
    frame = 0
    while not selection.done():
        start = f.read(8)
        if len(start) < 8:
            break
        if start[:4] == _PCAPNG_SECTION:
            # A section header sets the byte order of every block after it
            byte_order = f.read(4)
            if len(byte_order) < 4:
                break
            order = '<' if struct.unpack('<I', byte_order)[0] == _PCAPNG_BYTE_ORDER else '>'
            length = struct.unpack(order + 'I', start[4:])[0]
            if length < 12:
                break
            out.write(start + byte_order + f.read(length - 12))
            continue
        kind, length = struct.unpack(order + 'II', start)
        if length < 12:
            break
        if kind not in _PCAPNG_PACKETS and kind not in _PCAPNG_NOT_FRAMES:
            raise _Unsupported(kind)
        if kind in _PCAPNG_PACKETS:
            frame += 1
            if not selection.wants(frame):
                f.seek(length - 8, 1)
                continue
        out.write(start + f.read(length - 8))
