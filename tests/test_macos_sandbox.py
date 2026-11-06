#!/usr/bin/env python3
"""Tests for macos_sandbox.py — the parser-subprocess confinement layer."""

import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import macos_sandbox
import shark_analyzer
from samples import build_pcap_sample


class TestConfineNoOp(unittest.TestCase):
    def setUp(self):
        self._prev = os.environ.get('SOCRATES_SANDBOX')
        os.environ['SOCRATES_SANDBOX'] = '0'

    def tearDown(self):
        if self._prev is None:
            os.environ.pop('SOCRATES_SANDBOX', None)
        else:
            os.environ['SOCRATES_SANDBOX'] = self._prev

    def test_disabled_is_not_active(self):
        self.assertFalse(macos_sandbox.is_active())

    def test_disabled_returns_command_unchanged(self):
        cmd = ['yara', '-r', '/tmp/x']
        self.assertEqual(macos_sandbox.confine(cmd, read=['/tmp/x']), cmd)

    def test_disabled_does_not_mutate_input(self):
        cmd = ['file', '/tmp/x']
        out = macos_sandbox.confine(cmd, read=['/tmp/x'])
        self.assertIsNot(out, cmd)
        self.assertEqual(cmd, ['file', '/tmp/x'])


class TestBuildProfile(unittest.TestCase):
    """The profile is pure string-building - testable on any platform."""

    def test_deny_default_and_system_import(self):
        p = macos_sandbox.build_profile()
        self.assertIn('(deny default)', p)
        self.assertIn('(import "system.sb")', p)

    def test_exec_and_read_paths_are_subpath_filters(self):
        # REGRESSION: bare quoted paths (no (subpath ...) wrapper) make
        # sandbox-exec reject the profile with "illegal argument", so the
        # tool never runs and its output silently comes back empty.
        p = macos_sandbox.build_profile(read=['/data/in'], write=['/data/out'])
        self.assertIn('(allow process-exec* (subpath "/opt/homebrew")', p)
        self.assertIn('(subpath "/data/in")', p)
        self.assertIn('(subpath "/data/out")', p)
        self.assertNotIn('(allow process-exec* "/opt/homebrew"', p)

    def test_metadata_paths_are_literal_filters(self):
        p = macos_sandbox.build_profile(read=['/a/b/c'])
        self.assertIn('(allow file-read-metadata', p)
        self.assertIn('(literal "/a/b")', p)

    def test_write_grants_dev_null(self):
        p = macos_sandbox.build_profile(write=['/data/out'])
        self.assertIn('(literal "/dev/null")', p)


@unittest.skipUnless(sys.platform == 'darwin' and os.path.exists('/usr/bin/sandbox-exec'),
                     'sandbox-exec is macOS-only')
class TestConfineActiveOnMac(unittest.TestCase):
    def setUp(self):
        self._prev = os.environ.pop('SOCRATES_SANDBOX', None)

    def tearDown(self):
        if self._prev is not None:
            os.environ['SOCRATES_SANDBOX'] = self._prev

    def test_active_wraps_with_sandbox_exec(self):
        out = macos_sandbox.confine(['tcpdump', '-r', '/tmp/x'], read=['/tmp/x'])
        self.assertEqual(out[0], '/usr/bin/sandbox-exec')
        self.assertEqual(out[1], '-p')
        self.assertIn('(deny default)', out[2])

    def test_home_read_is_denied_under_the_jail(self):
        import subprocess
        home_file = os.path.expanduser('~/.zshrc')
        if not os.path.exists(home_file):
            self.skipTest('no ~/.zshrc to probe')
        cmd = macos_sandbox.confine(['/bin/cat', home_file], read=['/tmp'])
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0, 'sandbox must block reading the home directory')


@unittest.skipUnless(sys.platform == 'darwin', 'macOS has no /proc')
class TestSharkMemoryWatchdogOnMac(unittest.TestCase):
    def _hold_memory(self, megabytes):
        proc = subprocess.Popen(
            [sys.executable, '-c',
             f'x = bytearray({megabytes} * 1024 * 1024)\n'
             'x[::4096] = b"a" * len(x[::4096])\n'
             'print("ready", flush=True)\n'
             'import time; time.sleep(60)'],
            stdout=subprocess.PIPE, text=True, start_new_session=True)
        self.addCleanup(proc.wait)
        self.addCleanup(shark_analyzer._kill_group, proc)
        proc.stdout.readline()
        self.addCleanup(proc.stdout.close)
        return proc

    def test_group_memory_counts_the_group(self):
        proc = self._hold_memory(64)
        self.assertGreater(shark_analyzer._group_memory(proc.pid), 64 * 1024 * 1024)

    def test_group_memory_of_no_such_group_is_zero(self):
        proc = subprocess.Popen(['/usr/bin/true'], start_new_session=True)
        proc.wait()
        self.assertEqual(shark_analyzer._group_memory(proc.pid), 0)

    def test_watchdog_stops_a_group_past_the_limit(self):
        proc = self._hold_memory(64)
        too_big = threading.Event()
        with mock.patch.object(config, 'SHARK_MAX_MEMORY_BYTES', 32 * 1024 * 1024), \
                mock.patch.object(config, 'SHARK_MEMORY_CHECK_SECONDS', 0.05):
            shark_analyzer._watch_memory(proc, too_big)
        self.assertTrue(too_big.is_set())
        self.assertEqual(proc.wait(timeout=5), -signal.SIGKILL)


@unittest.skipUnless(macos_sandbox.is_active() and shutil.which('tshark'),
                     'needs sandbox-exec and tshark')
class TestSharkRunsConfined(unittest.TestCase):
    def test_every_tshark_tool_runs_in_the_sandbox_and_still_reads_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            pcap = os.path.join(tmp, 'sample.pcap')
            with open(pcap, 'wb') as f:
                f.write(build_pcap_sample())
            shark_analyzer._PACKET_COUNTS.clear()
            real_popen, argvs = subprocess.Popen, []

            def spy(cmd, *args, **kwargs):
                argvs.append(cmd)
                return real_popen(cmd, *args, **kwargs)

            with mock.patch('subprocess.Popen', spy):
                records = shark_analyzer.run_tshark(pcap)
        self.assertTrue(records)
        tools = [c for c in argvs if any(os.path.basename(a) in ('tshark', 'capinfos', 'editcap') for a in c[:4])]
        self.assertTrue(tools)
        for cmd in tools:
            self.assertEqual(cmd[0], macos_sandbox.SANDBOX_EXEC, cmd[:4])


class TestSoResourceDirFallback(unittest.TestCase):
    def _value(self, module, attr, env):
        code = f'import {module}; print({module}.{attr})'
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean = {k: v for k, v in os.environ.items() if k not in ('PLAYBOOKS_DIR', 'AI_SUMMARIES_DIR', 'DATA_DIR')}
        return subprocess.run([sys.executable, '-c', code], cwd=repo, env={**clean, **env},
                              capture_output=True, text=True, check=True).stdout.strip()

    @unittest.skipIf(os.path.isdir('/usr/share/playbooks'), 'the baked-in folder wins where it exists')
    def test_playbooks_fall_back_to_the_data_dir(self):
        self.assertEqual(self._value('playbook_lookup', 'BAKED_IN_PLAYBOOKS_DIR', {'DATA_DIR': '/data-x'}), '/data-x/playbooks')

    @unittest.skipIf(os.path.isdir('/usr/share/ai-summaries'), 'the baked-in folder wins where it exists')
    def test_ai_summaries_fall_back_to_the_data_dir(self):
        self.assertEqual(self._value('ai_summary_lookup', 'AI_SUMMARIES_DIR', {'DATA_DIR': '/data-x'}), '/data-x/ai-summaries')

    def test_explicit_dirs_win(self):
        self.assertEqual(self._value('playbook_lookup', 'BAKED_IN_PLAYBOOKS_DIR', {'PLAYBOOKS_DIR': '/p-x', 'DATA_DIR': '/data-x'}), '/p-x')
        self.assertEqual(self._value('ai_summary_lookup', 'AI_SUMMARIES_DIR', {'AI_SUMMARIES_DIR': '/a-x', 'DATA_DIR': '/data-x'}), '/a-x')


class TestGeoipDirFallback(unittest.TestCase):
    def _geoip_dir(self, env):
        code = 'import geo_lookup; print(geo_lookup.GEOIP_DIR)'
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean = {k: v for k, v in os.environ.items() if k not in ('GEOIP_DIR', 'DATA_DIR')}
        return subprocess.run([sys.executable, '-c', code], cwd=repo, env={**clean, **env},
                              capture_output=True, text=True, check=True).stdout.strip()

    @unittest.skipIf(os.path.isdir('/usr/share/geoip'), 'the baked-in folder wins where it exists')
    def test_falls_back_to_the_data_dir(self):
        self.assertEqual(self._geoip_dir({'DATA_DIR': '/data-x'}), '/data-x/geoip')

    def test_explicit_dir_wins(self):
        self.assertEqual(self._geoip_dir({'GEOIP_DIR': '/geo-x', 'DATA_DIR': '/data-x'}), '/geo-x')


if __name__ == '__main__':
    unittest.main(verbosity=2)
