#!/usr/bin/env python3
"""Tests for sigma_analyzer.py."""

import json
import os
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import sigma_analyzer
import validators


class TestLogTypeDetection(unittest.TestCase):
    def test_detect_windows_evtx(self):
        with tempfile.NamedTemporaryFile(suffix='.evtx', delete=False) as f:
            f.write(b'ElfFile\x00')
            path = f.name
        try:
            result = sigma_analyzer._detect_log_type(path)
            self.assertEqual(result, 'windows')
        finally:
            os.unlink(path)

    def test_detect_windows_json(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'{"EventID": 4624, "Channel": "Security"}')
            path = f.name
        try:
            result = sigma_analyzer._detect_log_type(path)
            self.assertEqual(result, 'windows')
        finally:
            os.unlink(path)

    def test_detect_linux_json(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            # Raw auditd-style log in JSON-wrapped format
            f.write(b'type=SYSCALL msg=audit(123): auid=1000 uid=0 exe="/bin/bash"')
            path = f.name
        try:
            result = sigma_analyzer._detect_log_type(path)
            self.assertEqual(result, 'linux')
        finally:
            os.unlink(path)

    def test_detect_ambiguous_returns_none(self):
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            f.write(b'generic log line\n')
            path = f.name
        try:
            result = sigma_analyzer._detect_log_type(path)
            self.assertIsNone(result)
        finally:
            os.unlink(path)


class TestZircoliteResultParsing(unittest.TestCase):
    def test_parse_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'[]')
            path = f.name
        try:
            alerts = sigma_analyzer.parse_zircolite_results(path)
            self.assertEqual(alerts, [])
        finally:
            os.unlink(path)

    def test_parse_zircolite_v3_output(self):
        results = [
            {
                'timestamp': '2024-01-01T00:00:00Z',
                'title': 'Suspicious PowerShell',
                'id': 'abc123',
                'rule_level': 'high',
                'logsource': 'windows',
                'tags': ['attack.T1059', 'attack.execution'],
                'event': {'CommandLine': 'powershell -enc abc'}
            }
        ]
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(results).encode())
            path = f.name
        try:
            alerts = sigma_analyzer.parse_zircolite_results(path)
            self.assertEqual(len(alerts), 1)
            alert = alerts[0]
            self.assertEqual(alert['rule_title'], 'Suspicious PowerShell')
            self.assertEqual(alert['rule_id'], 'abc123')
            self.assertEqual(alert['severity'], 'high')
            self.assertEqual(alert['level'], 'high')
            self.assertEqual(alert['mitre_techniques'], ['attack.T1059'])
        finally:
            os.unlink(path)

    def test_parse_dict_wrapper(self):
        results = {
            'detections': [
                {
                    'timestamp': '2024-01-01T00:00:00Z',
                    'title': 'Test Rule',
                    'id': 'def456',
                    'rule_level': 'medium',
                    'logsource': 'linux',
                    'tags': ['attack.T1078'],
                    'event': {'type': 'SYSCALL'}
                }
            ]
        }
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(results).encode())
            path = f.name
        try:
            alerts = sigma_analyzer.parse_zircolite_results(path)
            self.assertEqual(len(alerts), 1)
            self.assertEqual(alerts[0]['rule_title'], 'Test Rule')
            self.assertEqual(alerts[0]['severity'], 'medium')
        finally:
            os.unlink(path)

    def test_parse_multiple_matches(self):
        """A detection with 3 matches should emit 3 alert rows."""
        results = [
            {
                'title': 'Multiple Matches Rule',
                'id': 'multi123',
                'rule_level': 'high',
                'tags': ['attack.T1059'],
                'matches': [
                    {'SystemTime': '2024-01-01T10:00:00Z', 'EventID': 4624, 'Channel': 'Security'},
                    {'SystemTime': '2024-01-01T11:00:00Z', 'EventID': 4624, 'Channel': 'Security'},
                    {'SystemTime': '2024-01-01T12:00:00Z', 'EventID': 4624, 'Channel': 'Security'},
                ]
            }
        ]
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(results).encode())
            path = f.name
        try:
            alerts = sigma_analyzer.parse_zircolite_results(path)
            self.assertEqual(len(alerts), 3)
            for alert in alerts:
                self.assertEqual(alert['rule_title'], 'Multiple Matches Rule')
                self.assertEqual(alert['rule_id'], 'multi123')
                self.assertEqual(alert['severity'], 'high')
            # Each alert should have a distinct timestamp
            timestamps = [a['timestamp'] for a in alerts]
            self.assertEqual(len(set(timestamps)), 3)
            self.assertIn('2024-01-01T10:00:00Z', timestamps)
            self.assertIn('2024-01-01T11:00:00Z', timestamps)
            self.assertIn('2024-01-01T12:00:00Z', timestamps)
            # Log source should be resolved from the match
            self.assertEqual(alerts[0]['logsource'], 'Security')
            # original_log should be the specific match, not the whole detection
            original = json.loads(alerts[0]['original_log'])
            self.assertEqual(original['SystemTime'], '2024-01-01T10:00:00Z')
        finally:
            os.unlink(path)

    def test_parse_logsource_fallback_from_match(self):
        """When detection-level logsource is empty, use match's Channel."""
        results = [
            {
                'title': 'No Logsource Rule',
                'id': 'nols456',
                'rule_level': 'medium',
                'tags': [],
                'matches': [
                    {'SystemTime': '2024-01-01T10:00:00Z', 'Channel': 'Microsoft-Windows-Sysmon/Operational'},
                ]
            }
        ]
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(results).encode())
            path = f.name
        try:
            alerts = sigma_analyzer.parse_zircolite_results(path)
            self.assertEqual(len(alerts), 1)
            self.assertEqual(alerts[0]['logsource'], 'Microsoft-Windows-Sysmon/Operational')
        finally:
            os.unlink(path)

    def test_parse_no_matches_skipped(self):
        """A detection with no matches and no event should be skipped."""
        results = [
            {
                'title': 'Empty Rule',
                'id': 'empty789',
                'rule_level': 'low',
                'tags': [],
                'matches': []
            }
        ]
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(json.dumps(results).encode())
            path = f.name
        try:
            alerts = sigma_analyzer.parse_zircolite_results(path)
            self.assertEqual(len(alerts), 0)
        finally:
            os.unlink(path)


class TestImportZircoliteLogs(unittest.TestCase):
    def test_import_empty_db(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as zdb:
            zdb_path = zdb.name
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as edb:
                edb_path = edb.name
            try:
                count = sigma_analyzer.import_zircolite_logs(zdb_path, edb_path)
                self.assertEqual(count, 0)
            finally:
                os.unlink(edb_path)
        finally:
            os.unlink(zdb_path)

    def test_import_sample_logs(self):
        import sqlite3
        # Create a mock Zircolite unified DB
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as zdb:
            zdb_path = zdb.name
        conn = sqlite3.connect(zdb_path)
        conn.execute('''CREATE TABLE logs (
            row_id INTEGER, Channel TEXT, EventID INTEGER, Computer TEXT,
            CommandLine TEXT, SourceIp TEXT, DestinationIp TEXT,
            SourcePort INTEGER, DestinationPort INTEGER, Protocol TEXT,
            SystemTime TEXT, UtcTime TEXT
        )''')
        conn.execute('''INSERT INTO logs VALUES
            (1, 'Security', 4624, 'PC1', 'cmd.exe /c whoami', NULL, NULL, NULL, NULL, NULL, '2024-01-01T12:00:00Z', NULL),
            (2, 'Microsoft-Windows-Sysmon/Operational', 3, 'PC1', NULL, '192.168.1.1', '10.0.0.1', 12345, 80, 'tcp', '2024-01-01T12:01:00Z', NULL)
        ''')
        conn.commit()
        conn.close()

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as edb:
            edb_path = edb.name
        try:
            count = sigma_analyzer.import_zircolite_logs(zdb_path, edb_path)
            self.assertEqual(count, 2)

            # Verify in DB
            conn2 = sqlite3.connect(edb_path)
            conn2.row_factory = sqlite3.Row
            cur = conn2.execute('SELECT * FROM events WHERE event_type = "log" ORDER BY rowid')
            rows = cur.fetchall()
            self.assertEqual(len(rows), 2)

            # First event
            self.assertEqual(rows[0]['event_type'], 'log')
            self.assertEqual(rows[0]['src_ip'], '')
            self.assertEqual(rows[0]['dest_ip'], '')
            self.assertIn('cmd.exe', rows[0]['json_data'])

            # Second event (network)
            network_row = next((r for r in rows if r['src_ip'] == '192.168.1.1'), None)
            self.assertIsNotNone(network_row)
            self.assertEqual(network_row['dest_ip'], '10.0.0.1')
            self.assertEqual(network_row['src_port'], 12345)
            self.assertEqual(network_row['dest_port'], 80)
            self.assertEqual(network_row['protocol'], 'tcp')
            conn2.close()
        finally:
            os.unlink(zdb_path)
            os.unlink(edb_path)

    @unittest.mock.patch('sqlite3.connect')
    def test_import_handles_corrupt_db(self, mock_connect):
        """If sqlite3.connect fails, import_zircolite_logs must return 0 cleanly."""
        import sqlite3
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as zdb:
            zdb_path = zdb.name
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as edb:
                edb_path = edb.name
            try:
                mock_connect.side_effect = sqlite3.OperationalError('unable to open database file')
                count = sigma_analyzer.import_zircolite_logs(zdb_path, edb_path)
                self.assertEqual(count, 0)
            finally:
                os.unlink(edb_path)
        finally:
            os.unlink(zdb_path)


class TestValidatorsLogDetection(unittest.TestCase):
    def test_is_log_file_evtx(self):
        self.assertTrue(validators.is_log_file(b'ElfFile\x00'))

    def test_is_log_file_json(self):
        self.assertTrue(validators.is_log_file(b'{"EventID": 1}'))

    def test_is_log_file_csv(self):
        self.assertTrue(validators.is_log_file(b'timestamp,message\n2024-01-01,hello'))

    def test_is_log_file_xml(self):
        self.assertTrue(validators.is_log_file(b'<?xml version="1.0"?><root/>'))

    def test_is_log_file_not_html(self):
        self.assertFalse(validators.is_log_file(b'<!DOCTYPE html><html></html>'))

    def test_is_log_file_not_binary(self):
        self.assertFalse(validators.is_log_file(b'\x00\x01\x02\x03'))

    def test_is_log_file_by_extension(self):
        self.assertTrue(validators.is_log_file_by_extension('test.evtx'))
        self.assertTrue(validators.is_log_file_by_extension('test.json'))
        self.assertTrue(validators.is_log_file_by_extension('test.log'))
        self.assertFalse(validators.is_log_file_by_extension('test.exe'))


if __name__ == '__main__':
    unittest.main()
