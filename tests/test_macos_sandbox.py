#!/usr/bin/env python3
"""Tests for macos_sandbox.py — the parser-subprocess confinement layer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import macos_sandbox


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
