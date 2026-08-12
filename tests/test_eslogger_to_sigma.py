#!/usr/bin/env python3
"""Tests for scripts/eslogger_to_sigma.py."""

import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

import eslogger_to_sigma as mapper


def exec_record(path='/usr/bin/curl', args=None, parent='/bin/zsh', pid=501, euid=501):
    return {
        'time': '2026-08-11T21:00:00Z',
        'event': {'exec': {
            'target': {'executable': {'path': path}},
            'args': args if args is not None else ['curl', '-s', 'https://example.com'],
        }},
        'process': {'executable': {'path': parent},
                    'audit_token': {'pid': pid, 'euid': euid}},
    }


class TestExecMapping(unittest.TestCase):
    def test_maps_the_fields_the_macos_ruleset_queries(self):
        """Image / CommandLine / ParentImage / OriginalFileName are exactly
        the fields rules/macos.json's SQL selects on."""
        out = mapper.convert_record(exec_record())
        self.assertEqual(out['Image'], '/usr/bin/curl')
        self.assertEqual(out['CommandLine'], 'curl -s https://example.com')
        self.assertEqual(out['ParentImage'], '/bin/zsh')
        self.assertEqual(out['OriginalFileName'], 'curl')
        self.assertEqual(out['EventType'], 'exec')
        self.assertEqual(out['ProcessId'], 501)
        self.assertEqual(out['User'], '501')

    def test_arguments_with_spaces_are_quoted(self):
        """A joined command line must not invent token boundaries that
        weren't in the real argv - Sigma rules match on ' -x ' style
        substrings, so an unquoted multi-word argument could fake one."""
        out = mapper.convert_record(exec_record(args=['osascript', '-e', 'do shell script']))
        self.assertEqual(out['CommandLine'], 'osascript -e "do shell script"')

    def test_missing_args_falls_back_to_the_executable_path(self):
        record = exec_record()
        del record['event']['exec']['args']
        out = mapper.convert_record(record)
        self.assertEqual(out['CommandLine'], '/usr/bin/curl')

    def test_non_string_args_are_skipped(self):
        out = mapper.convert_record(exec_record(args=['curl', None, 7, '-s']))
        self.assertEqual(out['CommandLine'], 'curl -s')


class TestFileEventMapping(unittest.TestCase):
    def test_create_with_new_path_builds_target_filename(self):
        record = {
            'time': '1', 'event': {'create': {'destination': {'new_path': {
                'dir': {'path': '/Users/x/Library/LaunchAgents'},
                'filename': 'com.evil.plist'}}}},
            'process': {'executable': {'path': '/usr/bin/tee'}},
        }
        out = mapper.convert_record(record)
        self.assertEqual(out['TargetFilename'], '/Users/x/Library/LaunchAgents/com.evil.plist')
        self.assertEqual(out['Image'], '/usr/bin/tee')

    def test_create_with_existing_file_uses_its_path(self):
        record = {
            'time': '1', 'event': {'create': {'destination': {
                'existing_file': {'path': '/tmp/already-there'}}}},
            'process': {'executable': {'path': '/usr/bin/tee'}},
        }
        self.assertEqual(mapper.convert_record(record)['TargetFilename'], '/tmp/already-there')

    def test_open_unlink_and_rename_shapes(self):
        cases = [
            ({'open': {'file': {'path': '/etc/passwd'}}}, '/etc/passwd'),
            ({'unlink': {'target': {'path': '/tmp/gone'}}}, '/tmp/gone'),
            ({'rename': {'source': {'path': '/tmp/from'}}}, '/tmp/from'),
        ]
        for event, expected in cases:
            record = {'time': '1', 'event': event,
                      'process': {'executable': {'path': '/bin/mv'}}}
            self.assertEqual(mapper.convert_record(record)['TargetFilename'], expected)


class TestDefensiveParsing(unittest.TestCase):
    """Apple documents eslogger's schema as unstable and free to change
    between releases, so an unrecognized or partial record must be dropped,
    never crash the collector."""

    def test_unsupported_event_type_is_dropped(self):
        record = {'time': '1', 'event': {'exit': {'stat': 0}},
                  'process': {'executable': {'path': '/usr/bin/su'}}}
        self.assertIsNone(mapper.convert_record(record))

    def test_record_without_event_is_dropped(self):
        self.assertIsNone(mapper.convert_record({'time': '1'}))

    def test_record_mapping_to_no_useful_field_is_dropped(self):
        self.assertIsNone(mapper.convert_record({'time': '1', 'event': {'exec': {}}}))

    def test_non_dict_record_is_dropped(self):
        for value in ([], 'string', 7, None):
            self.assertIsNone(mapper.convert_record(value))

    def test_deeply_missing_keys_do_not_raise(self):
        record = {'event': {'exec': {'target': None}}, 'process': 'not-a-dict'}
        self.assertIsNone(mapper.convert_record(record))


class TestSetuidHandler(unittest.TestCase):
    def test_setuid_records_target_uid(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'setuid': {'uid': 0}},
            'process': {'executable': {'path': '/usr/bin/su'},
                        'audit_token': {'pid': 42, 'euid': 501}},
        })
        self.assertEqual(out['EventType'], 'setuid')
        self.assertEqual(out['TargetUid'], '0')
        self.assertEqual(out['Image'], '/usr/bin/su')

    def test_setgid_and_setegid_share_the_handler(self):
        for name, field in (('setgid', 'gid'), ('setegid', 'gid'), ('seteuid', 'uid')):
            record = {'time': '1', 'event': {name: {field: 20}},
                      'process': {'executable': {'path': '/bin/sh'}}}
            out = mapper.convert_record(record)
            self.assertEqual(out['TargetUid'], '20', name)


class TestSuAndSudoHandlers(unittest.TestCase):
    def test_su_renders_synthetic_command_line(self):
        """es_event_su_t doesn't carry an Image the way exec does, so the
        handler synthesizes Image=/usr/bin/su and joins argv into a
        CommandLine that existing SigmaHQ Linux su/sudo rules can match."""
        out = mapper.convert_record({
            'time': '1', 'event': {'su': {
                'success': True, 'to_username': 'root',
                'argv': ['-c', 'id'], 'shell': '/bin/zsh',
                'from_uid': 501, 'from_username': 'luke',
            }},
            'process': {'executable': {'path': '/usr/bin/su'}},
        })
        self.assertEqual(out['Image'], '/usr/bin/su')
        self.assertEqual(out['TargetUsername'], 'root')
        self.assertEqual(out['Success'], True)
        self.assertEqual(out['CommandLine'], 'su root -c id')

    def test_sudo_prefixes_command_with_target_user(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'sudo': {
                'success': True, 'to_username': 'root',
                'command': '/usr/bin/whoami',
                'from_uid': 501, 'from_username': 'luke',
            }},
            'process': {'executable': {'path': '/usr/bin/sudo'}},
        })
        self.assertEqual(out['Image'], '/usr/bin/sudo')
        self.assertEqual(out['CommandLine'], 'sudo -u root /usr/bin/whoami')

    def test_sudo_reject_records_reason(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'sudo': {
                'success': False,
                'reject_info': {'plugin_name': 'sudoers_policy'},
            }},
            'process': {'executable': {'path': '/usr/bin/sudo'}},
        })
        self.assertEqual(out['Success'], False)
        self.assertEqual(out['RejectReason'], 'sudoers_policy')


class TestLoginHandlers(unittest.TestCase):
    def test_openssh_login_captures_source_and_user(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'openssh_login': {
                'success': True, 'username': 'luke',
                'source_address': '10.0.0.5', 'source_address_type': 4,
            }},
            'process': {'executable': {'path': '/usr/sbin/sshd'}},
        })
        self.assertEqual(out['LoginUser'], 'luke')
        self.assertEqual(out['SourceIp'], '10.0.0.5')
        self.assertEqual(out['Success'], True)

    def test_openssh_logout_has_no_success_flag(self):
        """es_event_openssh_logout_t documents only source_address, username,
        uid - no success bool, unlike login."""
        out = mapper.convert_record({
            'time': '1', 'event': {'openssh_logout': {
                'username': 'luke', 'source_address': '10.0.0.5', 'uid': 501,
            }},
            'process': {'executable': {'path': '/usr/sbin/sshd'}},
        })
        self.assertEqual(out['LoginUser'], 'luke')
        self.assertNotIn('Success', out)

    def test_login_login_captures_username(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'login_login': {
                'success': True, 'username': 'luke', 'has_uid': True,
            }},
            'process': {'executable': {'path': '/usr/bin/login'}},
        })
        self.assertEqual(out['LoginUser'], 'luke')

    def test_screensharing_captures_viewer_and_session(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'screensharing_attach': {
                'success': True, 'source_address': '192.168.1.10',
                'viewer_appleid': 'a@b.com',
                'authentication_username': 'luke',
                'session_username': 'luke', 'existing_session': False,
            }},
            'process': {'executable': {'path': '/usr/libexec/screensharingd'}},
        })
        self.assertEqual(out['ViewerAppleId'], 'a@b.com')
        self.assertEqual(out['SourceIp'], '192.168.1.10')


class TestSecuritySensitiveHandlers(unittest.TestCase):
    def test_tcc_modify_extracts_service_and_actor(self):
        """es_event_tcc_modify_t's instigator (not the top-level process,
        which is tccd) is what did the modification and should populate Image."""
        out = mapper.convert_record({
            'time': '1', 'event': {'tcc_modify': {
                'service': 'kTCCServiceMicrophone',
                'identity': 'com.evil.app',
                'identity_type': 1, 'update_type': 1,
                'right': 2, 'reason': 3,
                'instigator': {
                    'executable': {'path': '/Applications/Evil.app/Contents/MacOS/Evil'},
                    'audit_token': {'pid': 999, 'euid': 501},
                },
                'responsible': {'executable': {'path': '/usr/sbin/tccd'}},
            }},
            'process': {'executable': {'path': '/usr/sbin/tccd'}},
        })
        self.assertEqual(out['TccService'], 'kTCCServiceMicrophone')
        self.assertEqual(out['TccIdentity'], 'com.evil.app')
        self.assertEqual(out['Image'], '/Applications/Evil.app/Contents/MacOS/Evil')
        self.assertEqual(out['ResponsibleImage'], '/usr/sbin/tccd')

    def test_btm_launch_item_add_captures_persistence_path(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'btm_launch_item_add': {
                'executable_path': '/Users/luke/evil.sh',
                'item': {
                    'item_type': 3, 'item_url': 'file:///Users/luke/Library/LaunchAgents/e.plist',
                    'legacy': False, 'managed': False, 'uid': 501,
                },
                'instigator': {'executable': {'path': '/usr/libexec/backgroundtaskmanagementd'}},
            }},
            'process': {'executable': {'path': '/usr/libexec/backgroundtaskmanagementd'}},
        })
        self.assertEqual(out['LaunchItemPath'], '/Users/luke/evil.sh')
        self.assertEqual(out['LaunchItemUrl'],
                         'file:///Users/luke/Library/LaunchAgents/e.plist')

    def test_xp_malware_detected_captures_identifier_and_path(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'xp_malware_detected': {
                'signature_version': '2189',
                'malware_identifier': 'OSX.Adload.A',
                'incident_identifier': '00000000-0000-0000-0000-000000000000',
                'detected_path': '/Users/luke/Downloads/pwn.dmg',
            }},
            'process': {'executable': {'path': '/usr/libexec/XProtect'}},
        })
        self.assertEqual(out['MalwareIdentifier'], 'OSX.Adload.A')
        self.assertEqual(out['TargetFilename'], '/Users/luke/Downloads/pwn.dmg')

    def test_gatekeeper_override_accepts_path_or_file_shape(self):
        """The `file` field is a union: some eslogger versions serialize it
        as a bare path string, others as an es_file_t dict with a path key."""
        for file_value in ('/tmp/thing', {'path': '/tmp/thing'}):
            out = mapper.convert_record({
                'time': '1', 'event': {'gatekeeper_user_override': {
                    'file_type': 1, 'file': file_value,
                    'sha256': 'a' * 64,
                }},
                'process': {'executable': {'path': '/usr/sbin/syspolicyd'}},
            })
            self.assertEqual(out['TargetFilename'], '/tmp/thing')
            self.assertEqual(out['Sha256'], 'a' * 64)

    def test_kextload_records_identifier(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'kextload': {'identifier': 'com.evil.kext'}},
            'process': {'executable': {'path': '/usr/bin/kmutil'}},
        })
        self.assertEqual(out['KextIdentifier'], 'com.evil.kext')

    def test_remote_thread_create_records_source_and_target(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'remote_thread_create': {
                'target': {
                    'executable': {'path': '/Applications/Victim.app/Contents/MacOS/Victim'},
                    'audit_token': {'pid': 555, 'euid': 501},
                },
            }},
            'process': {'executable': {'path': '/tmp/injector'},
                        'audit_token': {'pid': 777, 'euid': 501}},
        })
        self.assertEqual(out['TargetImage'],
                         '/Applications/Victim.app/Contents/MacOS/Victim')
        self.assertEqual(out['TargetProcessId'], 555)
        self.assertEqual(out['SourceImage'], '/tmp/injector')
        self.assertEqual(out['Image'], '/tmp/injector')

    def test_profile_add_captures_identifier_and_flags(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'profile_add': {
                'is_update': False,
                'profile': {
                    'identifier': 'com.company.mdm', 'display_name': 'MDM',
                    'organization': 'Company', 'scope': 'System',
                },
                'instigator': {'executable': {'path': '/usr/libexec/mdmclient'}},
            }},
            'process': {'executable': {'path': '/usr/libexec/mdmclient'}},
        })
        self.assertEqual(out['ProfileIdentifier'], 'com.company.mdm')
        self.assertEqual(out['ProfileIsUpdate'], False)

    def test_od_create_user_captures_target(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'od_create_user': {
                'user_name': 'backdoor', 'error_code': 0,
                'node_name': '/Local/Default', 'db_path': '',
            }},
            'process': {'executable': {'path': '/usr/bin/dscl'}},
        })
        self.assertEqual(out['TargetUsername'], 'backdoor')

    def test_od_group_add_captures_group_and_member(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'od_group_add': {
                'group_name': 'admin', 'error_code': 0,
                'member': {'member_type': 0, 'member_value': 'backdoor'},
                'node_name': '/Local/Default', 'db_path': '',
            }},
            'process': {'executable': {'path': '/usr/bin/dscl'}},
        })
        self.assertEqual(out['GroupName'], 'admin')
        self.assertEqual(out['TargetUsername'], 'backdoor')

    def test_mount_captures_paths(self):
        out = mapper.convert_record({
            'time': '1', 'event': {'mount': {
                'statfs': {'f_mntonname': '/Volumes/Evil',
                           'f_mntfromname': '/dev/disk4s1',
                           'f_fstypename': 'apfs'},
                'disposition': 1,
            }},
            'process': {'executable': {'path': '/System/Library/CoreServices/DiskMountNotifier'}},
        })
        self.assertEqual(out['MountPath'], '/Volumes/Evil')
        self.assertEqual(out['MountFrom'], '/dev/disk4s1')
        self.assertEqual(out['FilesystemType'], 'apfs')


class TestStreamConversion(unittest.TestCase):
    def test_converts_a_stream_and_skips_unparseable_lines(self):
        lines = [
            json.dumps(exec_record()),
            'this is not json',
            '',
            json.dumps({'time': '1', 'event': {'exit': {'stat': 0}}}),
            json.dumps(exec_record(path='/usr/bin/osacompile',
                                   args=['osacompile', '-x', '-e', 'payload'])),
        ]
        stdin = io.StringIO('\n'.join(lines) + '\n')
        stdout, stderr = io.StringIO(), io.StringIO()
        rc = mapper.main(stdin=stdin, stdout=stdout, stderr=stderr)

        self.assertEqual(rc, 0)
        out = [json.loads(l) for l in stdout.getvalue().splitlines()]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1]['Image'], '/usr/bin/osacompile')
        self.assertIn('unparseable', stderr.getvalue())

    def test_empty_input_produces_empty_output(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        mapper.main(stdin=io.StringIO(''), stdout=stdout, stderr=stderr)
        self.assertEqual(stdout.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
