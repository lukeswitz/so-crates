"""pcap_subset.copy_frames: the packets of chosen frames, copied exactly,
in each format tshark's second passes can be handed."""
import gzip
import os
import shutil
import subprocess
import tempfile
import unittest

import macos_sandbox
import pcap_subset
from tests.pcap_fixtures import write_pcap
from tests.protocol_fixtures import _udp_packet

HAS_TOOLS = bool(shutil.which('tshark') and shutil.which('editcap'))
_PACKETS = 1200


def _frames_by_time(path):
    """Which of the original frames a capture holds - write_pcap stamps
    frame n at 1700000000 + n - 1 seconds."""
    out = subprocess.run(macos_sandbox.confine(['tshark', '-n', '-r', path, '-T', 'fields', '-e', 'frame.time_epoch'],
                                               read=[path]),
                         capture_output=True, text=True, check=True).stdout
    return [int(float(t)) - 1700000000 + 1 for t in out.split()]


@unittest.skipUnless(HAS_TOOLS, 'tshark/editcap not installed')
class TestCopyFrames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.pcap = os.path.join(cls.tmp, 'all.pcap')
        write_pcap(cls.pcap, [_udp_packet('10.0.0.1', '10.0.0.2', 40000, 9, bytes([i % 256]) * 20)
                              for i in range(_PACKETS)])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _copy(self, source, ranges):
        dst = os.path.join(self.tmp, 'copy')
        self.assertTrue(pcap_subset.copy_frames(source, dst, ranges))
        return _frames_by_time(dst)

    def _converted(self, kind):
        path = os.path.join(self.tmp, f'all.{kind}')
        if not os.path.exists(path):
            subprocess.run(['editcap', '-F', kind, self.pcap, path], check=True)
        return path

    def test_the_chosen_frames_from_each_format(self):
        ranges = [(1, 3), (500, 500), (1199, 1200)]
        want = [1, 2, 3, 500, 1199, 1200]
        for source in (self.pcap, self._converted('nsecpcap'), self._converted('pcapng')):
            with self.subTest(source=os.path.basename(source)):
                self.assertEqual(self._copy(source, ranges), want)

    def test_more_ranges_than_editcap_takes(self):
        """REGRESSION: editcap keeps 512 ranges and silently drops the
        rest - the protocol pass lost every S7comm record after one point
        of a long capture that way."""
        ranges = [(n, n) for n in range(1, _PACKETS + 1, 2)]      # 600 single frames
        for source in (self.pcap, self._converted('pcapng')):
            with self.subTest(source=os.path.basename(source)):
                self.assertEqual(self._copy(source, ranges), list(range(1, _PACKETS + 1, 2)))

    def test_a_pcapng_with_records_tshark_numbers_is_left_to_editcap(self):
        """tshark numbers a systemd journal export block (type 9) as a frame
        too - counting packets only, every later frame came out one off."""
        import struct
        with open(self._converted('pcapng'), 'rb') as f:
            data = f.read()
        shb_len = struct.unpack('<I', data[4:8])[0]
        idb_len = struct.unpack('<I', data[shb_len + 4:shb_len + 8])[0]
        entry = b'__REALTIME_TIMESTAMP=1700000000000000\nMESSAGE=x\n'
        entry += bytes(-len(entry) % 4)
        journal = struct.pack('<II', 9, 12 + len(entry)) + entry + struct.pack('<I', 12 + len(entry))
        mixed = os.path.join(self.tmp, 'journal.pcapng')
        with open(mixed, 'wb') as f:
            f.write(data[:shb_len + idb_len] + journal + data[shb_len + idb_len:])
        dst = os.path.join(self.tmp, 'journal-copy')
        self.assertFalse(pcap_subset.copy_frames(mixed, dst, [(3, 3)]))
        self.assertFalse(os.path.exists(dst))

    def test_a_capture_it_cannot_read_is_left_to_editcap(self):
        compressed = os.path.join(self.tmp, 'all.pcap.gz')
        with open(self.pcap, 'rb') as f, gzip.open(compressed, 'wb') as out:
            out.write(f.read())
        dst = os.path.join(self.tmp, 'not-written')
        self.assertFalse(pcap_subset.copy_frames(compressed, dst, [(1, 2)]))
        self.assertFalse(os.path.exists(dst))


if __name__ == '__main__':
    unittest.main()
