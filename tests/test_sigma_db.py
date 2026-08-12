#!/usr/bin/env python3
"""Tests for DB sigma alert functions."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import db


class TestSigmaAlertsDB(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.db_fd)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_insert_and_query_sigma_alerts(self):
        alerts = [
            {
                'timestamp': '2024-01-01T00:00:00Z',
                'rule_title': 'Test Rule 1',
                'rule_id': 'abc123',
                'severity': 'high',
                'level': 'high',
                'logsource': 'windows',
                'tags': ['attack.T1059'],
                'mitre_techniques': ['attack.T1059'],
                'original_log': '{"EventID": 1}',
                'json_data': '{"title": "Test Rule 1"}',
            },
            {
                'timestamp': '2024-01-01T01:00:00Z',
                'rule_title': 'Test Rule 2',
                'rule_id': 'def456',
                'severity': 'low',
                'level': 'low',
                'logsource': 'linux',
                'tags': [],
                'mitre_techniques': [],
                'original_log': '{"type": "SYSCALL"}',
                'json_data': '{"title": "Test Rule 2"}',
            },
        ]
        db.insert_sigma_alerts(self.db_path, alerts)

        results = db.query_sigma_alerts_sqlite(self.db_path)
        self.assertEqual(len(results), 2)
        # High severity should come first due to ORDER BY
        self.assertEqual(results[0]['severity'], 'high')
        self.assertEqual(results[0]['rule_title'], 'Test Rule 1')
        self.assertEqual(results[1]['severity'], 'low')

    def test_query_sigma_alerts_by_severity(self):
        alerts = [
            {'timestamp': '', 'rule_title': 'High', 'rule_id': '', 'severity': 'high', 'level': 'high', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
            {'timestamp': '', 'rule_title': 'Low', 'rule_id': '', 'severity': 'low', 'level': 'low', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
        ]
        db.insert_sigma_alerts(self.db_path, alerts)

        high_results = db.query_sigma_alerts_sqlite(self.db_path, severity='high')
        self.assertEqual(len(high_results), 1)
        self.assertEqual(high_results[0]['rule_title'], 'High')

    def test_query_sigma_alerts_with_search(self):
        alerts = [
            {'timestamp': '', 'rule_title': 'Suspicious PowerShell', 'rule_id': 'r1', 'severity': 'high', 'level': 'high', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
            {'timestamp': '', 'rule_title': 'Normal Activity', 'rule_id': 'r2', 'severity': 'low', 'level': 'low', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
        ]
        db.insert_sigma_alerts(self.db_path, alerts)

        results = db.query_sigma_alerts_sqlite(self.db_path, q='PowerShell')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['rule_title'], 'Suspicious PowerShell')

    def test_get_sigma_alert_count(self):
        alerts = [
            {'timestamp': '', 'rule_title': 'A', 'rule_id': '', 'severity': 'critical', 'level': 'critical', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
            {'timestamp': '', 'rule_title': 'B', 'rule_id': '', 'severity': 'high', 'level': 'high', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
        ]
        db.insert_sigma_alerts(self.db_path, alerts)

        total = db.get_sigma_alert_count_sqlite(self.db_path)
        self.assertEqual(total, 2)

        critical = db.get_sigma_alert_count_sqlite(self.db_path, severity='critical')
        self.assertEqual(critical, 1)

    def test_get_sigma_stats(self):
        alerts = [
            {'timestamp': '', 'rule_title': 'A', 'rule_id': '', 'severity': 'critical', 'level': 'critical', 'logsource': '', 'tags': ['attack.T1059'], 'mitre_techniques': ['attack.T1059'], 'original_log': '', 'json_data': ''},
            {'timestamp': '', 'rule_title': 'B', 'rule_id': '', 'severity': 'high', 'level': 'high', 'logsource': '', 'tags': ['attack.T1059'], 'mitre_techniques': ['attack.T1059'], 'original_log': '', 'json_data': ''},
            {'timestamp': '', 'rule_title': 'C', 'rule_id': '', 'severity': 'high', 'level': 'high', 'logsource': '', 'tags': [], 'mitre_techniques': [], 'original_log': '', 'json_data': ''},
        ]
        db.insert_sigma_alerts(self.db_path, alerts)

        stats = db.get_sigma_stats_sqlite(self.db_path)
        self.assertEqual(stats['total'], 3)
        self.assertIn('critical', stats['by_severity'])
        self.assertIn('high', stats['by_severity'])
        self.assertEqual(stats['by_severity']['critical'], 1)
        self.assertEqual(stats['by_severity']['high'], 2)
        self.assertIn('attack.T1059', stats['mitre_techniques'])

    def test_multiple_alerts_same_rule_id(self):
        """Multiple matches from the same rule should each be a distinct DB row."""
        alerts = [
            {
                'timestamp': '2024-01-01T10:00:00Z',
                'rule_title': 'Repeated Rule',
                'rule_id': 'same-rule-123',
                'severity': 'high',
                'level': 'high',
                'logsource': 'Security',
                'tags': [],
                'mitre_techniques': [],
                'original_log': '{"EventID": 4624, "SystemTime": "2024-01-01T10:00:00Z"}',
                'json_data': '{"title": "Repeated Rule"}',
            },
            {
                'timestamp': '2024-01-01T11:00:00Z',
                'rule_title': 'Repeated Rule',
                'rule_id': 'same-rule-123',
                'severity': 'high',
                'level': 'high',
                'logsource': 'Security',
                'tags': [],
                'mitre_techniques': [],
                'original_log': '{"EventID": 4624, "SystemTime": "2024-01-01T11:00:00Z"}',
                'json_data': '{"title": "Repeated Rule"}',
            },
            {
                'timestamp': '2024-01-01T12:00:00Z',
                'rule_title': 'Repeated Rule',
                'rule_id': 'same-rule-123',
                'severity': 'high',
                'level': 'high',
                'logsource': 'Security',
                'tags': [],
                'mitre_techniques': [],
                'original_log': '{"EventID": 4624, "SystemTime": "2024-01-01T12:00:00Z"}',
                'json_data': '{"title": "Repeated Rule"}',
            },
        ]
        db.insert_sigma_alerts(self.db_path, alerts)

        results = db.query_sigma_alerts_sqlite(self.db_path)
        self.assertEqual(len(results), 3)
        # All should have the same rule_id
        for r in results:
            self.assertEqual(r['rule_id'], 'same-rule-123')
        # But different original_log values
        original_logs = [r['original_log'] for r in results]
        self.assertEqual(len(set(original_logs)), 3)

    def test_import_log_events(self):
        events = [
            {
                'event_type': 'log',
                'timestamp': '2024-01-01T12:00:00Z',
                'src_ip': '192.168.1.1',
                'src_port': 12345,
                'dest_ip': '10.0.0.1',
                'dest_port': 80,
                'protocol': 'tcp',
                'app_proto': 'Microsoft-Windows-Sysmon/Operational',
                'json_data': '{"EventID": 3}',
            },
            {
                'event_type': 'log',
                'timestamp': '2024-01-01T12:01:00Z',
                'src_ip': '',
                'src_port': 0,
                'dest_ip': '',
                'dest_port': 0,
                'protocol': '',
                'app_proto': 'Security',
                'json_data': '{"EventID": 4624}',
            },
        ]
        db.import_log_events(self.db_path, events)

        results = db.query_events_sqlite(self.db_path, event_type='log', offset=0, limit=10, q=None)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['event_type'], 'log')
        self.assertEqual(results[0]['src_ip'], '192.168.1.1')
        self.assertEqual(results[1]['app_proto'], 'Security')

        # Check stats
        stats = db.get_event_types_sqlite(self.db_path, q=None)
        self.assertIn('log', stats)
        self.assertEqual(stats['log'], 2)


if __name__ == '__main__':
    unittest.main()
