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

import playbook_lookup


def _write_index(base_dir, detection_type, index):
    os.makedirs(base_dir, exist_ok=True)
    path = os.path.join(base_dir, f'{detection_type}.json.gz')
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump(index, f)
    return path


class TestGetPlaybook(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # get_playbook caches per (base_dir, detection_type) - a fresh
        # tmpdir per test would normally be enough to avoid cross-test
        # cache pollution on its own, but the cache is also cleared
        # explicitly so a test that intentionally reuses the same tmpdir
        # path (unlikely, but tempfile could theoretically reuse a path
        # across a long run) can't silently see a stale cached index.
        playbook_lookup._playbook_index_cache.clear()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        playbook_lookup._playbook_index_cache.clear()

    def test_exact_id_match(self):
        _write_index(self.tmpdir, 'nids', {
            '2000005': {'name': 'Specific', 'description': 'd', 'questions': []},
            '_default': {'name': 'Generic', 'description': 'd', 'questions': []},
        })
        result = playbook_lookup.get_playbook('nids', '2000005', base_dir=self.tmpdir)
        self.assertEqual(result['name'], 'Specific')

    def test_falls_back_to_default_when_no_exact_match(self):
        _write_index(self.tmpdir, 'nids', {
            '2000005': {'name': 'Specific', 'description': 'd', 'questions': []},
            '_default': {'name': 'Generic', 'description': 'd', 'questions': []},
        })
        result = playbook_lookup.get_playbook('nids', '9999999999', base_dir=self.tmpdir)
        self.assertEqual(result['name'], 'Generic')

    def test_none_when_no_exact_match_and_no_default(self):
        _write_index(self.tmpdir, 'nids', {
            '2000005': {'name': 'Specific', 'description': 'd', 'questions': []},
        })
        result = playbook_lookup.get_playbook('nids', '9999999999', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_file_missing(self):
        result = playbook_lookup.get_playbook('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_file_corrupt(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        path = os.path.join(self.tmpdir, 'nids.json.gz')
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            f.write('not valid json{{{')
        result = playbook_lookup.get_playbook('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_file_is_not_gzip(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        path = os.path.join(self.tmpdir, 'nids.json.gz')
        with open(path, 'w') as f:
            f.write('{"2000005": {}}')  # plain text, not actually gzipped
        result = playbook_lookup.get_playbook('nids', '2000005', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_none_when_index_is_not_a_dict(self):
        os.makedirs(self.tmpdir, exist_ok=True)
        path = os.path.join(self.tmpdir, 'nids.json.gz')
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            json.dump(['not', 'a', 'dict'], f)
        result = playbook_lookup.get_playbook('nids', '0', base_dir=self.tmpdir)
        self.assertIsNone(result)

    def test_nids_and_sigma_indexes_are_independent(self):
        _write_index(self.tmpdir, 'nids', {'2000005': {'name': 'NIDS entry', 'description': '', 'questions': []}})
        _write_index(self.tmpdir, 'sigma', {'2000005': {'name': 'Sigma entry', 'description': '', 'questions': []}})
        nids_result = playbook_lookup.get_playbook('nids', '2000005', base_dir=self.tmpdir)
        sigma_result = playbook_lookup.get_playbook('sigma', '2000005', base_dir=self.tmpdir)
        self.assertEqual(nids_result['name'], 'NIDS entry')
        self.assertEqual(sigma_result['name'], 'Sigma entry')

    def test_repeated_lookups_do_not_reread_the_file(self):
        """The whole index is loaded and cached on first access - a second
        lookup for a *different* rule_id under the same detection_type
        must be a plain dict access, not another gzip.open() call."""
        _write_index(self.tmpdir, 'nids', {
            '2000005': {'name': 'A', 'description': '', 'questions': []},
            '2000006': {'name': 'B', 'description': '', 'questions': []},
        })
        real_gzip_open = gzip.open
        with unittest.mock.patch('playbook_lookup.gzip.open', side_effect=real_gzip_open) as mock_open:
            first = playbook_lookup.get_playbook('nids', '2000005', base_dir=self.tmpdir)
            second = playbook_lookup.get_playbook('nids', '2000006', base_dir=self.tmpdir)
        self.assertEqual(first['name'], 'A')
        self.assertEqual(second['name'], 'B')
        self.assertEqual(mock_open.call_count, 1, 'the index file must only be opened once across both lookups')

    def test_default_base_dir_is_baked_in_dir(self):
        with unittest.mock.patch('playbook_lookup._load_playbook_index', return_value={}) as mock_load:
            playbook_lookup.get_playbook('nids', '2000005')
        mock_load.assert_called_once_with('nids', playbook_lookup.BAKED_IN_PLAYBOOKS_DIR)

    def test_rule_id_is_stringified_before_lookup(self):
        """A caller could plausibly pass an int - keys in the loaded JSON
        index are always strings (JSON object keys can't be anything
        else), so get_playbook must coerce rule_id before indexing."""
        _write_index(self.tmpdir, 'nids', {'2000005': {'name': 'A', 'description': '', 'questions': []}})
        result = playbook_lookup.get_playbook('nids', 2000005, base_dir=self.tmpdir)
        self.assertEqual(result['name'], 'A')


if __name__ == '__main__':
    unittest.main()
