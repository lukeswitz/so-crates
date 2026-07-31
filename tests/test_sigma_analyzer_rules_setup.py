#!/usr/bin/env python3
"""Tests for sigma_analyzer.py's setup_sigma_rules() (separate from
test_sigma_analyzer.py's log-type-detection/parsing tests)."""

import os
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import config
import sigma_analyzer


class TestSetupSigmaRulesForceNoNetwork(unittest.TestCase):
    """REGRESSION: force=True + a cached ruleset that isn't stale yet +
    network_allowed=False used to silently call on_progress zero times for
    that ruleset - the exact case of a user explicitly clicking "check for
    updates" while offline produced no feedback at all in the Rules modal."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        rules_dir = os.path.join(self.tmpdir, config.SIGMA_RULES_SUBDIR)
        os.makedirs(rules_dir, exist_ok=True)
        for ruleset_name in sigma_analyzer.ZIRCOLITE_RULES_URLS:
            with open(os.path.join(rules_dir, f'{ruleset_name}.json'), 'w') as f:
                f.write('[]')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_force_with_fresh_cache_and_no_network_reports_progress(self):
        """REGRESSION: this message must not claim "no internet access" -
        network_allowed=False means the caller opted out of checking
        (e.g. server startup), not that a reachability check actually
        failed."""
        messages = []
        sigma_analyzer.setup_sigma_rules(
            self.tmpdir, on_progress=messages.append, network_allowed=False, force=True)
        self.assertTrue(messages, 'on_progress must be called even when force=True, cache is fresh, and offline')
        self.assertTrue(any('using cached' in m.lower() for m in messages), messages)
        self.assertFalse(any('no internet' in m.lower() for m in messages), messages)
        # Each ruleset gets its own named message, not a single generic one.
        for ruleset_name in sigma_analyzer.ZIRCOLITE_RULES_URLS:
            self.assertTrue(any(ruleset_name in m for m in messages), (ruleset_name, messages))


if __name__ == '__main__':
    unittest.main()
