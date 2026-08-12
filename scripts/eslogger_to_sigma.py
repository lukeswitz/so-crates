#!/usr/bin/env python3
"""Convert eslogger(1) JSON Lines into the field shape SO-CRATES's macOS
Sigma ruleset queries.

Each Endpoint Security event dispatches to its own handler; the handler
maps Apple's es_event_*_t struct layout into Sigma field names taken
verbatim from where existing SigmaHQ macOS rules already look
(Image, CommandLine, ParentImage, TargetFilename, User) plus a small set
of namespaced fields for the event types SigmaHQ has no coverage for at
all yet (TccService, LaunchItemPath, KextIdentifier, ...). Every field
comes from a documented struct member; anything not published in Apple's
ESMessage.h is not invented here.

Apple warns eslogger's serialization is unstable across releases, so the
handlers are defensive: a missing hop returns None and the field is
omitted rather than crashing the run, and a record that maps to nothing
useful is dropped entirely.

Reads JSON Lines on stdin, writes JSON Lines on stdout.
"""

import json
import os
import sys


def _dig(obj, *path):
    """Walk a nested dict/list path, returning None if any hop is missing."""
    for key in path:
        if isinstance(obj, dict):
            obj = obj.get(key)
        elif isinstance(obj, list) and isinstance(key, int) and 0 <= key < len(obj):
            obj = obj[key]
        else:
            return None
    return obj


def _actor_process(record, event_body):
    """The process that did the thing.

    Prefer event-scoped `instigator` (BTM / TCC / profile / OD events, where
    the record's top-level process is delivery infrastructure rather than
    the actor); fall back to the top-level `process`.
    """
    instigator = _dig(event_body, 'instigator') if isinstance(event_body, dict) else None
    if isinstance(instigator, dict):
        return instigator
    proc = record.get('process')
    return proc if isinstance(proc, dict) else None


def _process_fields(process):
    """Image / SigningId / ProcessId / User from an es_process_t dict."""
    out = {}
    if not isinstance(process, dict):
        return out
    image = _dig(process, 'executable', 'path')
    if isinstance(image, str):
        out['Image'] = image
    if isinstance(process.get('signing_id'), str):
        out['SigningId'] = process['signing_id']
    pid = _dig(process, 'audit_token', 'pid')
    if isinstance(pid, int):
        out['ProcessId'] = pid
    uid = _dig(process, 'audit_token', 'euid')
    if isinstance(uid, int):
        out['User'] = str(uid)
    return out


def _command_line(exec_body):
    """Sigma's macOS rules match a single CommandLine string, so eslogger's
    argv array is joined and any arg containing whitespace is quoted so a
    joined line cannot fake a token boundary that wasn't in the real argv.
    """
    args = exec_body.get('args') if isinstance(exec_body, dict) else None
    if not isinstance(args, list):
        path = _dig(exec_body, 'target', 'executable', 'path')
        return path if isinstance(path, str) else None
    parts = []
    for arg in args:
        if not isinstance(arg, str):
            continue
        parts.append(f'"{arg}"' if any(c.isspace() for c in arg) else arg)
    return ' '.join(parts) if parts else None


def _handle_exec(body, record):
    """es_event_exec_t: target.executable.path + args + parent from `process`."""
    out = {}
    image = _dig(body, 'target', 'executable', 'path')
    if isinstance(image, str):
        out['Image'] = image
        out['OriginalFileName'] = image.rsplit('/', 1)[-1]
    cmd = _command_line(body)
    if cmd:
        out['CommandLine'] = cmd
    parent = _dig(record, 'process', 'executable', 'path')
    if isinstance(parent, str):
        out['ParentImage'] = parent
    cwd = _dig(body, 'cwd', 'path')
    if isinstance(cwd, str):
        out['CurrentDirectory'] = cwd
    tty = _dig(body, 'target', 'tty', 'path')
    if isinstance(tty, str):
        out['Tty'] = tty
    return out


def _handle_create(body, _record):
    """es_event_create_t: destination is a union (existing_file or new_path)."""
    existing = _dig(body, 'destination', 'existing_file', 'path')
    if isinstance(existing, str):
        return {'TargetFilename': existing}
    new_dir = _dig(body, 'destination', 'new_path', 'dir', 'path')
    new_name = _dig(body, 'destination', 'new_path', 'filename')
    if isinstance(new_dir, str) and isinstance(new_name, str):
        return {'TargetFilename': os.path.join(new_dir, new_name)}
    return {}


def _handle_open(body, _record):
    path = _dig(body, 'file', 'path')
    return {'TargetFilename': path} if isinstance(path, str) else {}


def _handle_unlink(body, _record):
    path = _dig(body, 'target', 'path')
    return {'TargetFilename': path} if isinstance(path, str) else {}


def _handle_rename(body, _record):
    src = _dig(body, 'source', 'path')
    out = {'TargetFilename': src} if isinstance(src, str) else {}
    dst = _dig(body, 'destination', 'existing_file', 'path')
    if not isinstance(dst, str):
        dst_dir = _dig(body, 'destination', 'new_path', 'dir', 'path')
        dst_name = _dig(body, 'destination', 'new_path', 'filename')
        if isinstance(dst_dir, str) and isinstance(dst_name, str):
            dst = os.path.join(dst_dir, dst_name)
    if isinstance(dst, str):
        out['DestinationFilename'] = dst
    return out


def _handle_mount(body, _record):
    """es_event_mount_t.statfs mirrors POSIX struct statfs field names."""
    out = {}
    for src, dst in (('f_mntonname', 'MountPath'),
                     ('f_mntfromname', 'MountFrom'),
                     ('f_fstypename', 'FilesystemType')):
        value = _dig(body, 'statfs', src)
        if isinstance(value, str):
            out[dst] = value
    return out


def _handle_setuid(body, _record):
    """es_event_setuid_t / setgid_t / seteuid_t / setegid_t: {uid} or {gid}."""
    uid = body.get('uid') if isinstance(body, dict) else None
    if uid is None and isinstance(body, dict):
        uid = body.get('gid')
    return {'TargetUid': str(uid)} if uid is not None else {}


def _handle_su(body, _record):
    """es_event_su_t: rendered as Image=/usr/bin/su with a synthetic
    CommandLine so existing su/sudo Sigma rules can match against it."""
    out = {'Image': '/usr/bin/su', 'OriginalFileName': 'su'}
    to = _dig(body, 'to_username')
    if isinstance(to, str):
        out['TargetUsername'] = to
    if isinstance(body.get('success'), bool):
        out['Success'] = body['success']
    args = body.get('argv') if isinstance(body, dict) else None
    parts = ['su']
    if isinstance(to, str):
        parts.append(to)
    if isinstance(args, list):
        for arg in args:
            if isinstance(arg, str):
                parts.append(f'"{arg}"' if any(c.isspace() for c in arg) else arg)
    out['CommandLine'] = ' '.join(parts)
    fail = body.get('failure_message')
    if isinstance(fail, str) and fail:
        out['FailureMessage'] = fail
    return out


def _handle_sudo(body, _record):
    """es_event_sudo_t: {success, from_uid, to_uid, to_username, command, ...}."""
    out = {'Image': '/usr/bin/sudo', 'OriginalFileName': 'sudo'}
    to = _dig(body, 'to_username')
    if isinstance(to, str):
        out['TargetUsername'] = to
    if isinstance(body.get('success'), bool):
        out['Success'] = body['success']
    command = _dig(body, 'command')
    if isinstance(command, str):
        prefix = f'sudo -u {to}' if isinstance(to, str) else 'sudo'
        out['CommandLine'] = f'{prefix} {command}'
    else:
        out['CommandLine'] = 'sudo'
    reject_reason = _dig(body, 'reject_info', 'plugin_name')
    if isinstance(reject_reason, str):
        out['RejectReason'] = reject_reason
    return out


def _handle_login_login(body, _record):
    """es_event_login_login_t (console login): {success, username, ...}."""
    out = {}
    if isinstance(body.get('success'), bool):
        out['Success'] = body['success']
    user = body.get('username')
    if isinstance(user, str):
        out['LoginUser'] = user
    fail = body.get('failure_message')
    if isinstance(fail, str) and fail:
        out['FailureMessage'] = fail
    return out


def _handle_openssh_login(body, _record):
    out = {}
    if isinstance(body.get('success'), bool):
        out['Success'] = body['success']
    user = body.get('username')
    if isinstance(user, str):
        out['LoginUser'] = user
    src = body.get('source_address')
    if isinstance(src, str):
        out['SourceIp'] = src
    result = body.get('result_type')
    if result is not None:
        out['ResultType'] = result
    return out


def _handle_openssh_logout(body, _record):
    """es_event_openssh_logout_t: {source_address, username, uid}. No success flag."""
    out = {}
    user = body.get('username')
    if isinstance(user, str):
        out['LoginUser'] = user
    src = body.get('source_address')
    if isinstance(src, str):
        out['SourceIp'] = src
    uid = body.get('uid')
    if uid is not None:
        out['TargetUid'] = str(uid)
    return out


def _handle_screensharing_attach(body, _record):
    out = {}
    if isinstance(body.get('success'), bool):
        out['Success'] = body['success']
    src = body.get('source_address')
    if isinstance(src, str):
        out['SourceIp'] = src
    for src_key, dst_key in (('viewer_appleid', 'ViewerAppleId'),
                             ('authentication_username', 'LoginUser'),
                             ('session_username', 'SessionUser'),
                             ('authentication_type', 'AuthenticationType')):
        value = body.get(src_key)
        if isinstance(value, str):
            out[dst_key] = value
    if isinstance(body.get('existing_session'), bool):
        out['ExistingSession'] = body['existing_session']
    return out


def _handle_tcc_modify(body, _record):
    """es_event_tcc_modify_t: {service, identity, identity_type, update_type,
    right, reason, instigator, responsible}."""
    out = {}
    for src, dst in (('service', 'TccService'),
                     ('identity', 'TccIdentity'),
                     ('identity_type', 'TccIdentityType'),
                     ('update_type', 'TccUpdateType'),
                     ('right', 'TccRight'),
                     ('reason', 'TccReason')):
        value = body.get(src)
        if value is not None:
            out[dst] = value if isinstance(value, str) else str(value)
    responsible = _dig(body, 'responsible', 'executable', 'path')
    if isinstance(responsible, str):
        out['ResponsibleImage'] = responsible
    return out


def _handle_btm_launch_item(body, _record):
    """es_event_btm_launch_item_add_t / _remove_t: {instigator, app, item,
    executable_path}. item is es_btm_launch_item_t (item_type, legacy,
    managed, uid, item_url, app_url)."""
    out = {}
    exec_path = body.get('executable_path')
    if isinstance(exec_path, str) and exec_path:
        out['LaunchItemPath'] = exec_path
    item_url = _dig(body, 'item', 'item_url')
    if isinstance(item_url, str):
        out.setdefault('LaunchItemPath', item_url)
        out['LaunchItemUrl'] = item_url
    app_url = _dig(body, 'item', 'app_url')
    if isinstance(app_url, str) and app_url:
        out['LaunchItemAppUrl'] = app_url
    item_type = _dig(body, 'item', 'item_type')
    if item_type is not None:
        out['LaunchItemType'] = item_type if isinstance(item_type, str) else str(item_type)
    if isinstance(_dig(body, 'item', 'legacy'), bool):
        out['LaunchItemLegacy'] = _dig(body, 'item', 'legacy')
    if isinstance(_dig(body, 'item', 'managed'), bool):
        out['LaunchItemManaged'] = _dig(body, 'item', 'managed')
    uid = _dig(body, 'item', 'uid')
    if uid is not None:
        out['LaunchItemUid'] = str(uid)
    return out


def _handle_xp_malware_detected(body, _record):
    """es_event_xp_malware_detected_t: signature_version + malware_identifier
    + incident_identifier + detected_path."""
    out = {}
    for src, dst in (('signature_version', 'XProtectSignatureVersion'),
                     ('malware_identifier', 'MalwareIdentifier'),
                     ('incident_identifier', 'IncidentIdentifier'),
                     ('detected_path', 'TargetFilename')):
        value = body.get(src)
        if isinstance(value, str):
            out[dst] = value
    return out


def _handle_xp_malware_remediated(body, _record):
    out = {}
    for src, dst in (('signature_version', 'XProtectSignatureVersion'),
                     ('malware_identifier', 'MalwareIdentifier'),
                     ('incident_identifier', 'IncidentIdentifier'),
                     ('action_type', 'ActionType'),
                     ('result_description', 'ResultDescription'),
                     ('remediated_path', 'TargetFilename')):
        value = body.get(src)
        if isinstance(value, str):
            out[dst] = value
    if isinstance(body.get('success'), bool):
        out['Success'] = body['success']
    return out


def _handle_gatekeeper_override(body, _record):
    """es_event_gatekeeper_user_override_t: file is a union that's either a
    path string or an es_file_t dict; handle both eslogger serializations."""
    out = {}
    file_value = body.get('file')
    if isinstance(file_value, str):
        out['TargetFilename'] = file_value
    elif isinstance(file_value, dict):
        path = file_value.get('path')
        if isinstance(path, str):
            out['TargetFilename'] = path
    sha = body.get('sha256')
    if isinstance(sha, str):
        out['Sha256'] = sha
    team = _dig(body, 'signing_info', 'team_id')
    if isinstance(team, str):
        out['TeamId'] = team
    return out


def _handle_kextload(body, _record):
    ident = body.get('identifier') if isinstance(body, dict) else None
    return {'KextIdentifier': ident} if isinstance(ident, str) else {}


def _handle_remote_thread_create(body, record):
    """es_event_remote_thread_create_t: target is the process being injected."""
    out = {}
    target_image = _dig(body, 'target', 'executable', 'path')
    if isinstance(target_image, str):
        out['TargetImage'] = target_image
    target_pid = _dig(body, 'target', 'audit_token', 'pid')
    if isinstance(target_pid, int):
        out['TargetProcessId'] = target_pid
    src_image = _dig(record, 'process', 'executable', 'path')
    if isinstance(src_image, str):
        out['SourceImage'] = src_image
    return out


def _handle_profile(body, _record):
    out = {}
    ident = _dig(body, 'profile', 'identifier')
    if isinstance(ident, str):
        out['ProfileIdentifier'] = ident
    name = _dig(body, 'profile', 'display_name')
    if isinstance(name, str):
        out['ProfileDisplayName'] = name
    org = _dig(body, 'profile', 'organization')
    if isinstance(org, str):
        out['ProfileOrganization'] = org
    scope = _dig(body, 'profile', 'scope')
    if isinstance(scope, str):
        out['ProfileScope'] = scope
    if isinstance(body.get('is_update'), bool):
        out['ProfileIsUpdate'] = body['is_update']
    return out


def _handle_od_user(body, _record):
    """es_event_od_create_user_t: {user_name, node_name, db_path, error_code}."""
    out = {}
    user = body.get('user_name')
    if isinstance(user, str):
        out['TargetUsername'] = user
    for src, dst in (('node_name', 'DirectoryNode'),
                     ('db_path', 'DirectoryDbPath')):
        value = body.get(src)
        if isinstance(value, str):
            out[dst] = value
    err = body.get('error_code')
    if isinstance(err, int):
        out['ErrorCode'] = err
    return out


def _handle_od_password(body, _record):
    """es_event_od_modify_password_t: {account_type, account_name, ...}."""
    out = {}
    user = body.get('account_name')
    if isinstance(user, str):
        out['TargetUsername'] = user
    acct_type = body.get('account_type')
    if acct_type is not None:
        out['AccountType'] = acct_type if isinstance(acct_type, str) else str(acct_type)
    for src, dst in (('node_name', 'DirectoryNode'),
                     ('db_path', 'DirectoryDbPath')):
        value = body.get(src)
        if isinstance(value, str):
            out[dst] = value
    err = body.get('error_code')
    if isinstance(err, int):
        out['ErrorCode'] = err
    return out


def _handle_od_group_add(body, _record):
    """es_event_od_group_add_t: group_name + member (es_od_member_id_t)."""
    out = {}
    group = body.get('group_name')
    if isinstance(group, str):
        out['GroupName'] = group
    member_name = _dig(body, 'member', 'member_value')
    if isinstance(member_name, str):
        out['TargetUsername'] = member_name
    for src, dst in (('node_name', 'DirectoryNode'),
                     ('db_path', 'DirectoryDbPath')):
        value = body.get(src)
        if isinstance(value, str):
            out[dst] = value
    return out


def _handle_marker(_body, _record):
    """cs_invalidated etc.: process context alone carries the signal."""
    return {}


HANDLERS = {
    'exec': _handle_exec,
    'create': _handle_create,
    'open': _handle_open,
    'unlink': _handle_unlink,
    'rename': _handle_rename,
    'mount': _handle_mount,
    'setuid': _handle_setuid,
    'setgid': _handle_setuid,
    'seteuid': _handle_setuid,
    'setegid': _handle_setuid,
    'setreuid': _handle_setuid,
    'setregid': _handle_setuid,
    'su': _handle_su,
    'sudo': _handle_sudo,
    'login_login': _handle_login_login,
    'openssh_login': _handle_openssh_login,
    'openssh_logout': _handle_openssh_logout,
    'screensharing_attach': _handle_screensharing_attach,
    'tcc_modify': _handle_tcc_modify,
    'btm_launch_item_add': _handle_btm_launch_item,
    'btm_launch_item_remove': _handle_btm_launch_item,
    'xp_malware_detected': _handle_xp_malware_detected,
    'xp_malware_remediated': _handle_xp_malware_remediated,
    'gatekeeper_user_override': _handle_gatekeeper_override,
    'kextload': _handle_kextload,
    'kextunload': _handle_kextload,
    'remote_thread_create': _handle_remote_thread_create,
    'cs_invalidated': _handle_marker,
    'profile_add': _handle_profile,
    'profile_remove': _handle_profile,
    'od_create_user': _handle_od_user,
    'od_delete_user': _handle_od_user,
    'od_disable_user': _handle_od_user,
    'od_enable_user': _handle_od_user,
    'od_modify_password': _handle_od_password,
    'od_group_add': _handle_od_group_add,
    'od_group_remove': _handle_od_group_add,
}


def _event_body(record):
    event = record.get('event')
    if not isinstance(event, dict):
        return None, None
    for name, body in event.items():
        if name in HANDLERS and isinstance(body, dict):
            return name, body
    return None, None


def convert_record(record):
    """Map one eslogger record to a Sigma-shaped event, or None to drop it.

    Actor process fields come from the event's `instigator` if present,
    else the top-level `process`; the handler's own fields overwrite them
    where they conflict (e.g. exec's Image is the target executable, not
    the parent).
    """
    if not isinstance(record, dict):
        return None
    name, body = _event_body(record)
    if name is None:
        return None

    out = {'EventType': name}
    ts = record.get('time') or record.get('mach_time')
    if ts is not None:
        out['UtcTime'] = str(ts)

    actor = _actor_process(record, body)
    actor_fields = _process_fields(actor)
    if name not in ('exec', 'remote_thread_create'):
        out.update(actor_fields)

    handler = HANDLERS[name]
    out.update(handler(body, record))

    if name in ('exec', 'remote_thread_create'):
        for key, value in actor_fields.items():
            out.setdefault(key, value)
        if name == 'exec' and 'ParentImage' not in out and 'Image' in actor_fields:
            out['ParentImage'] = actor_fields['Image']

    interesting = {'Image', 'CommandLine', 'TargetFilename', 'TargetUid',
                   'TargetUsername', 'LoginUser', 'MalwareIdentifier',
                   'LaunchItemPath', 'TccService', 'KextIdentifier',
                   'TargetImage', 'MountPath', 'ProfileIdentifier',
                   'GroupName', 'DestinationFilename'}
    if not (interesting & out.keys()):
        return None
    return out


def main(stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    read = written = malformed = 0
    per_type = {}
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        read += 1
        try:
            record = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        converted = convert_record(record)
        if converted is None:
            continue
        stdout.write(json.dumps(converted) + '\n')
        written += 1
        per_type[converted['EventType']] = per_type.get(converted['EventType'], 0) + 1
    stdout.flush()
    summary = f'[eslogger] {read} events read, {written} converted'
    if malformed:
        summary += f', {malformed} unparseable'
    print(summary, file=stderr)
    if per_type:
        breakdown = ', '.join(f'{k}={v}' for k, v in sorted(per_type.items(),
                                                            key=lambda kv: -kv[1]))
        print(f'[eslogger] by type: {breakdown}', file=stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
