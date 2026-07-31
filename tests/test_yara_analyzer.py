#!/usr/bin/env python3
"""Tests for yara_analyzer.py."""

import os
import sys
import tempfile
import shutil
import unittest
import unittest.mock
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import yara_analyzer


class TestSetupYaraRulesForceNoNetwork(unittest.TestCase):
    """REGRESSION: force=True + a cached copy that isn't stale yet +
    network_allowed=False used to silently call on_progress zero times -
    the exact case of a user explicitly clicking "check for updates" while
    offline produced no feedback at all in the Rules modal."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        rules_dir = os.path.join(self.tmpdir, yara_analyzer.YARA_RULES_SUBDIR)
        os.makedirs(rules_dir, exist_ok=True)
        self.rules_file = os.path.join(rules_dir, yara_analyzer.YARA_FORGE_FILENAME)
        with open(self.rules_file, 'w') as f:
            f.write('rule dummy { condition: true }')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_force_with_fresh_cache_and_no_network_reports_progress(self):
        messages = []
        yara_analyzer.setup_yara_rules(
            self.tmpdir, on_progress=messages.append, network_allowed=False, force=True)
        self.assertTrue(messages, 'on_progress must be called even when force=True, cache is fresh, and offline')
        self.assertTrue(any('no internet' in m.lower() for m in messages), messages)


class TestRefreshFallsBackToCacheOnBadDownload(unittest.TestCase):
    """REGRESSION: a refresh's except clause only caught (OSError,
    urllib.error.URLError), but _download_yara_forge_rules can also raise
    zipfile.BadZipFile (a truncated/rate-limited/HTML-error response that
    isn't actually a zip) or KeyError (if the expected member is ever
    renamed upstream) - neither is an OSError subclass, so both escaped
    setup_yara_rules() entirely even with a perfectly good cached copy on
    disk, and propagated up into _analyze_standalone_file()'s single broad
    except Exception as a whole-file-analysis failure instead of silently
    falling back to the cache like the docstring promises."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        rules_dir = os.path.join(self.tmpdir, yara_analyzer.YARA_RULES_SUBDIR)
        os.makedirs(rules_dir, exist_ok=True)
        self.rules_file = os.path.join(rules_dir, yara_analyzer.YARA_FORGE_FILENAME)
        with open(self.rules_file, 'w') as f:
            f.write('rule dummy { condition: true }')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_bad_zip_falls_back_to_cached_copy(self):
        messages = []
        with unittest.mock.patch('yara_analyzer.is_file_stale', return_value=True), \
             unittest.mock.patch('yara_analyzer.is_host_reachable', return_value=True), \
             unittest.mock.patch('yara_analyzer._download_yara_forge_rules',
                                  side_effect=zipfile.BadZipFile('not a zip')):
            result = yara_analyzer.setup_yara_rules(
                self.tmpdir, on_progress=messages.append, network_allowed=True, force=True)

        self.assertEqual(result, self.rules_file, 'must fall back to the cached rules file, not raise')
        self.assertTrue(any('warning' in m.lower() for m in messages), messages)

    def test_missing_zip_member_falls_back_to_cached_copy(self):
        messages = []
        with unittest.mock.patch('yara_analyzer.is_file_stale', return_value=True), \
             unittest.mock.patch('yara_analyzer.is_host_reachable', return_value=True), \
             unittest.mock.patch('yara_analyzer._download_yara_forge_rules',
                                  side_effect=KeyError('packages/full/yara-rules-full.yar')):
            result = yara_analyzer.setup_yara_rules(
                self.tmpdir, on_progress=messages.append, network_allowed=True, force=True)

        self.assertEqual(result, self.rules_file, 'must fall back to the cached rules file, not raise')
        self.assertTrue(any('warning' in m.lower() for m in messages), messages)


if __name__ == '__main__':
    unittest.main()
