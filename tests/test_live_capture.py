#!/usr/bin/env python3
"""Tests for live_capture.py."""

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import config
import live_capture


class TestInterfaceNameValidation(unittest.TestCase):
    def test_accepts_real_interface_names(self):
        for name in ('en0', 'eth0', 'wlan0', 'bond0.100', 'br-abc123'):
            self.assertTrue(live_capture.is_valid_iface_name(name), name)

    def test_rejects_shell_metacharacters(self):
        """The name reaches a tcpdump argv list, but it is still validated:
        a name is never joined into a string, and anything that isn't a
        plain interface token is refused before it can reach a subprocess."""
        for name in ('en0; rm -rf /', 'en0 && id', '../../etc/passwd', 'en0|nc',
                     '$(id)', '`id`', 'en0\nen1', '-i', ''):
            self.assertFalse(live_capture.is_valid_iface_name(name), name)

    def test_rejects_overlong_name(self):
        self.assertFalse(live_capture.is_valid_iface_name('e' * 64))

    def test_permission_probe_refuses_invalid_name_without_running_tcpdump(self):
        with unittest.mock.patch('live_capture.subprocess.Popen') as popen:
            self.assertFalse(live_capture.has_capture_permission('en0; id'))
        popen.assert_not_called()


class TestExcludedInterfaces(unittest.TestCase):
    def test_pseudo_interfaces_are_excluded(self):
        for name in ('lo0', 'utun4', 'awdl0', 'llw0', 'bridge100', 'ap1',
                     'gif0', 'stf0', 'vmenet0', 'anpi0'):
            self.assertFalse(live_capture._is_candidate_iface(name), name)

    def test_real_interfaces_are_candidates(self):
        for name in ('en0', 'eth0', 'wlan0'):
            self.assertTrue(live_capture._is_candidate_iface(name), name)


class TestInterfaceListing(unittest.TestCase):
    def test_addressed_interfaces_sort_first(self):
        with unittest.mock.patch('live_capture._iface_names',
                                 return_value=['lo0', 'en1', 'en0', 'utun0']), \
             unittest.mock.patch('live_capture._iface_address',
                                 side_effect=lambda n: '10.0.0.5' if n == 'en0' else None):
            interfaces = live_capture.list_interfaces()
        self.assertEqual([i['name'] for i in interfaces], ['en0', 'en1'])
        self.assertEqual(live_capture.default_interface(interfaces), 'en0')

    def test_default_interface_falls_back_to_first_when_none_addressed(self):
        interfaces = [{'name': 'en1', 'address': None}, {'name': 'en2', 'address': None}]
        self.assertEqual(live_capture.default_interface(interfaces), 'en1')

    def test_default_interface_is_none_when_nothing_capturable(self):
        self.assertIsNone(live_capture.default_interface([]))


class TestCaptureSupport(unittest.TestCase):
    def test_unsupported_without_tcpdump(self):
        with unittest.mock.patch('live_capture.shutil.which', return_value=None):
            support = live_capture.capture_support()
        self.assertFalse(support['supported'])
        self.assertIn('tcpdump', support['reason'])

    def test_unsupported_without_interfaces(self):
        with unittest.mock.patch('live_capture.shutil.which', return_value='/usr/sbin/tcpdump'), \
             unittest.mock.patch('live_capture.list_interfaces', return_value=[]):
            support = live_capture.capture_support()
        self.assertFalse(support['supported'])
        self.assertIn('No capturable network interfaces', support['reason'])

    def test_unsupported_without_permission_names_the_fix(self):
        with unittest.mock.patch('live_capture.shutil.which', return_value='/usr/sbin/tcpdump'), \
             unittest.mock.patch('live_capture.list_interfaces',
                                 return_value=[{'name': 'en0', 'address': '10.0.0.5'}]), \
             unittest.mock.patch('live_capture.has_capture_permission', return_value=False):
            support = live_capture.capture_support()
        self.assertFalse(support['supported'])
        self.assertIn('access_bpf', support['reason'])
        self.assertEqual(support['default_interface'], 'en0')

    def test_supported_reports_no_reason(self):
        with unittest.mock.patch('live_capture.shutil.which', return_value='/usr/sbin/tcpdump'), \
             unittest.mock.patch('live_capture.list_interfaces',
                                 return_value=[{'name': 'en0', 'address': '10.0.0.5'}]), \
             unittest.mock.patch('live_capture.has_capture_permission', return_value=True):
            support = live_capture.capture_support()
        self.assertTrue(support['supported'])
        self.assertIsNone(support['reason'])
        self.assertEqual(support['max_duration'], config.CAPTURE_MAX_DURATION)
        self.assertEqual(support['default_duration'], config.CAPTURE_DEFAULT_DURATION)


class TestRunCaptureValidation(unittest.TestCase):
    """Duration and interface are re-validated inside run_capture, not only
    at the HTTP handler, so no caller can reach tcpdump with an unchecked
    argument."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.dest = os.path.join(self.tmpdir, 'capture.pcap')

    def test_rejects_invalid_interface(self):
        with unittest.mock.patch('live_capture.subprocess.Popen') as popen:
            with self.assertRaises(ValueError):
                live_capture.run_capture(self.dest, 'en0; id', 5)
        popen.assert_not_called()

    def test_rejects_zero_duration(self):
        with unittest.mock.patch('live_capture.subprocess.Popen') as popen:
            with self.assertRaises(ValueError):
                live_capture.run_capture(self.dest, 'en0', 0)
        popen.assert_not_called()

    def test_rejects_duration_over_ceiling(self):
        with unittest.mock.patch('live_capture.subprocess.Popen') as popen:
            with self.assertRaises(ValueError):
                live_capture.run_capture(self.dest, 'en0', config.CAPTURE_MAX_DURATION + 1)
        popen.assert_not_called()


class TestRunCaptureCommand(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.dest = os.path.join(self.tmpdir, 'capture.pcap')

    def _fake_proc(self, exit_after_polls=0):
        proc = unittest.mock.MagicMock()
        proc.poll.side_effect = [None] * exit_after_polls + [0] * 50
        proc.stderr.read.return_value = ''
        return proc

    def test_capture_is_non_promiscuous_and_unbuffered(self):
        """-p keeps the capture from switching the interface into
        promiscuous mode, and -U flushes each packet so the byte counter the
        UI polls actually moves during the run."""
        with unittest.mock.patch('live_capture.subprocess.Popen',
                                 return_value=self._fake_proc()) as popen, \
             unittest.mock.patch('live_capture._packet_count', return_value=3):
            with open(self.dest, 'wb') as f:
                f.write(b'\xd4\xc3\xb2\xa1' + b'\x00' * 20)
            live_capture.run_capture(self.dest, 'en0', 5, on_progress=lambda m: None)
        cmd = popen.call_args[0][0]
        self.assertEqual(cmd[0], 'tcpdump')
        self.assertIn('-p', cmd)
        self.assertIn('-U', cmd)
        self.assertEqual(cmd[cmd.index('-i') + 1], 'en0')
        self.assertEqual(cmd[cmd.index('-w') + 1], self.dest)
        self.assertNotIn('sudo', cmd)

    def test_missing_output_file_is_a_failure(self):
        with unittest.mock.patch('live_capture.subprocess.Popen',
                                 return_value=self._fake_proc()):
            success, count = live_capture.run_capture(
                self.dest, 'en0', 5, on_progress=lambda m: None)
        self.assertFalse(success)
        self.assertIsNone(count)

    def test_zero_packet_capture_still_succeeds(self):
        """An idle interface is a real answer, not an error."""
        with unittest.mock.patch('live_capture.subprocess.Popen',
                                 return_value=self._fake_proc()), \
             unittest.mock.patch('live_capture._packet_count', return_value=0):
            with open(self.dest, 'wb') as f:
                f.write(b'\xd4\xc3\xb2\xa1' + b'\x00' * 20)
            success, count = live_capture.run_capture(
                self.dest, 'en0', 5, on_progress=lambda m: None)
        self.assertTrue(success)
        self.assertEqual(count, 0)

    def test_tcpdump_that_cannot_start_reports_failure(self):
        with unittest.mock.patch('live_capture.subprocess.Popen',
                                 side_effect=OSError('No such file')):
            messages = []
            success, count = live_capture.run_capture(
                self.dest, 'en0', 5, on_progress=messages.append)
        self.assertFalse(success)
        self.assertIsNone(count)
        self.assertTrue(any('Could not start tcpdump' in m for m in messages), messages)


if __name__ == '__main__':
    unittest.main()
