#!/usr/bin/env python3
import gzip
import json
import os
import sys
import tempfile
import shutil
import unittest
import unittest.mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import ai_summary_lookup


def _write_index(base_dir, detection_type, index):
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, f'{detection_type}.json.gz')
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump(index, f)
    return path


class TestGetAiSummary(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # get_ai_summary caches per (base_dir, detection_type) - a fresh
        # tmpdir per test would normally be enough to avoid cross-test
        # cache pollution on its own, but the cache is also cleared
        # explicitly so a test that intentionally reuses the same tmpdir
        # path (unlikely, but tempfile could theoretically reuse a path
        # across a long run) can't silently see a stale cached index.
        ai_summary_lookup._ai_summary_index_cache.clear()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        ai_summary_lookup._ai_summary_index_cache.clear()

    def test_exact_id_match(self):
        _write_index(self.tmpdir, 'nids', {'2000005': 'This rule detects X.'})
        result = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
        self.assertEqual(result, 'This rule detects X.')

    def test_none_when_no_exact_match(self):
        """Unlike playbook_lookup.get_playbook, there is no engine-wide
        '_default' fallback entry - an unrelated rule's summary would be
        actively misleading, so a miss is just a miss."""
        _write_index(self.tmpdir, 'nids', {'2000005': 'This rule detects X.'})
        result = ai_summary_lookup.get_ai_summary('nids', '9999999999', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_file_missing(self):
        result = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_file_corrupt(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        path = os.path.join(self.tmpdir, 'nids.json.gz')
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            f.write('not valid json{{{')
        result = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_file_is_not_gzip(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        path = os.path.join(self.tmpdir, 'nids.json.gz')
        with open(path, 'w') as f:
            f.write('{"2000005": "not actually gzipped"}')
        result = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_is_not_a_dict(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        path = os.path.join(self.tmpdir, 'nids.json.gz')
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            json.dump(['not', 'a', 'dict'], f)
        result = ai_summary_lookup.get_ai_summary('nids', '0', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_summary_is_empty_string(self):
        _write_index(self.tmpdir, 'nids', {'2000005': ''})
        result = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_nids_sigma_yara_indexes_are_independent(self):
        _write_index(self.tmpdir, 'nids', {'2000005': 'NIDS summary'})
        _write_index(self.tmpdir, 'sigma', {'2000005': 'Sigma summary'})
        _write_index(self.tmpdir, 'yara', {'2000005': 'YARA summary'})
        nids_result = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
        sigma_result = ai_summary_lookup.get_ai_summary('sigma', '2000005', base_dir=self.tmpdir)
        yara_result = ai_summary_lookup.get_ai_summary('yara', '2000005', base_dir=self.tmpdir)
        self.assertEqual(nids_result, 'NIDS summary')
        self.assertEqual(sigma_result, 'Sigma summary')
        self.assertEqual(yara_result, 'YARA summary')

    def test_yara_lookup_by_rule_name(self):
        _write_index(self.tmpdir, 'yara', {'ALFA_SHELL': 'Detects a web shell.'})
        result = ai_summary_lookup.get_ai_summary('yara', 'ALFA_SHELL', base_dir=self.tmpdir)
        self.assertEqual(result, 'Detects a web shell.')

    def test_repeated_lookups_do_not_reread_the_file(self):
        """The whole index is loaded and cached on first access - a second
        lookup for a *different* rule_id under the same detection_type
        must be a plain dict access, not another gzip.open() call."""
        _write_index(self.tmpdir, 'nids', {'2000005': 'A', '2000006': 'B'})
        real_gzip_open = gzip.open
        with unittest.mock.patch('ai_summary_lookup.gzip.open', side_effect=real_gzip_open) as mock_open:
            first = ai_summary_lookup.get_ai_summary('nids', '2000005', base_dir=self.tmpdir)
            second = ai_summary_lookup.get_ai_summary('nids', '2000006', base_dir=self.tmpdir)
        self.assertEqual(first, 'A')
        self.assertEqual(second, 'B')
        self.assertEqual(mock_open.call_count, 1, 'the index file must only be opened once across both lookups')

    def test_default_base_dir_is_baked_in_dir(self):
        with unittest.mock.patch('ai_summary_lookup._load_ai_summary_index', return_value={}) as mock_load:
            ai_summary_lookup.get_ai_summary('nids', '2000005')
        mock_load.assert_called_once_with('nids', ai_summary_lookup.AI_SUMMARIES_DIR)

    def test_rule_id_is_stringified_before_lookup(self):
        """A caller could plausibly pass an int - keys in the loaded JSON
        index are always strings (JSON object keys can't be anything
        else), so get_ai_summary must coerce rule_id before indexing."""
        _write_index(self.tmpdir, 'nids', {'2000005': 'A'})
        result = ai_summary_lookup.get_ai_summary('nids', 2000005, base_dir=self.tmpdir)
        self.assertEqual(result, 'A')


if __name__ == '__main__':
    unittest.main()
