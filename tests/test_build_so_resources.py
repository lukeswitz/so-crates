#!/usr/bin/env python3
import gzip
import json
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))

try:
    import yaml
except ImportError:
    yaml = None


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        yaml.safe_dump(data, f)


def _read(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


@unittest.skipIf(yaml is None, 'PyYAML is installed only by scripts/fetch-so-resources.sh')
class TestBuildSoResources(unittest.TestCase):
    def setUp(self):
        import build_so_resources
        self.build = build_so_resources
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _path(self, *parts):
        return os.path.join(self.tmp.name, *parts)

    def test_playbooks_keep_only_what_the_lookup_reads_plus_the_engine_default(self):
        entry = {'name': 'n', 'description': 'd', 'detection': {'drop': 'me'},
                 'questions': [{'question': 'q', 'context': 'c', 'query': 'drop me'}]}
        for kind, engine in (('nids', 'engine_nids.yaml'), ('sigma', 'engine_sigma.yaml')):
            _write(self._path('pb', 'public', kind, 'individual', '123.yaml'), entry)
            _write(self._path('pb', 'public', kind, 'engine', engine), {'name': f'{kind} default'})
        self.build.build_playbooks(self._path('pb'), self._path('out'))
        index = _read(self._path('out', 'nids.json.gz'))
        self.assertEqual(index['123'], {'name': 'n', 'description': 'd', 'questions': [{'question': 'q', 'context': 'c'}]})
        self.assertEqual(index['_default']['name'], 'nids default')
        self.assertEqual(index['_default']['questions'], [])

    def test_summaries_keep_only_reviewed_text(self):
        data = {'1': {'Summary': ' kept ', 'Reviewed': True, 'Ruleset': 'x'},
                '2': {'Summary': 'unreviewed', 'Reviewed': False},
                '3': {'Summary': '  ', 'Reviewed': True}}
        for filename in ('suricata_summaries.yaml', 'sigma_summaries.yaml', 'yara_summaries.yaml'):
            _write(self._path('ai', 'detections-ai', filename), data)
        self.build.build_ai_summaries(self._path('ai'), self._path('out'))
        for kind in ('nids', 'sigma', 'yara'):
            self.assertEqual(_read(self._path('out', f'{kind}.json.gz')), {'1': 'kept'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
