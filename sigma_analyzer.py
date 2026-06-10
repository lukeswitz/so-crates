#!/usr/bin/env python3
"""Sigma rule analysis integration for SO-CRATES using Zircolite.

Zircolite is optional. If installed, log files (EVTX, JSON, CSV, XML)
are scanned with Sigma rules after upload. Rules are baked into Docker
images; non-Docker deployments download on first run if internet is available.
"""

import json
import os
import shutil
import subprocess
import time
import urllib.request

import config
from validators import is_host_reachable

ZIRCOLITE_RULES_URLS = {
    'windows': 'https://raw.githubusercontent.com/wagga40/Zircolite-Rules-v2/main/rules_windows_merged.json',
    'linux': 'https://raw.githubusercontent.com/wagga40/Zircolite-Rules-v2/main/rules_linux.json',
}
BAKED_IN_SIGMA_DIR = '/usr/share/sigma-rules'
SIGMA_RULES_SUBDIR = config.SIGMA_RULES_SUBDIR


ZIRCOLITE_BUNDLED_PATH = os.path.expanduser('~/socrates-data/zircolite/zircolite.py')
ZIRCOLITE_CONFIG_PATHS = [
    os.path.expanduser('~/socrates-data/zircolite/config/config.yaml'),
    '/usr/local/lib/zircolite/config/config.yaml',
    '/usr/share/zircolite/config/config.yaml',
]
ZIRCOLITE_VENV_PYTHON = '/usr/local/lib/zircolite-venv/bin/python3'
def _resolved_data_dir(data_dir=None):
    """Active data directory: explicit arg, else $DATA_DIR, else the default.

    Resolved at call-time (not frozen at import) so a custom DATA_DIR is honored
    when locating the bundled Zircolite install and its venv.
    """
    if data_dir:
        return data_dir
    return os.environ.get('DATA_DIR', os.path.expanduser('~/socrates-data'))


def _zircolite_python(data_dir=None):
    """Return the first existing Zircolite venv interpreter, else 'python3'.

    The Docker venv is checked first so existing images are unchanged; the
    data-dir venv supports native (non-Docker) installs such as macOS where
    setup-macos.sh builds it under the active DATA_DIR.
    """
    candidates = [
        ZIRCOLITE_VENV_PYTHON,
        os.path.join(_resolved_data_dir(data_dir), 'zircolite-venv', 'bin', 'python3'),
    ]
    for py in candidates:
        if os.path.isfile(py):
            return py
    return 'python3'


def is_zircolite_available(data_dir=None):
    """Return True if the zircolite CLI is available."""
    return (_zircolite_cmd(data_dir) is not None)


def _zircolite_cmd(data_dir=None):
    """Return the best available Zircolite executable path."""
    # Check PATH first
    for cmd in ('zircolite', 'zircolite.py'):
        path = shutil.which(cmd)
        if path:
            return path
    # Check bundled copy in the active data dir. _resolved_data_dir() already
    # falls back to ~/socrates-data when DATA_DIR is unset, so a custom DATA_DIR
    # is honored exactly (not silently satisfied by the default location).
    bundled = os.path.join(_resolved_data_dir(data_dir), 'zircolite', 'zircolite.py')
    if os.path.isfile(bundled):
        return bundled
    return None


def _zircolite_config(data_dir=None):
    """Return the first available Zircolite config file path."""
    candidates = [
        os.path.join(_resolved_data_dir(data_dir), 'zircolite', 'config', 'config.yaml'),
        *ZIRCOLITE_CONFIG_PATHS[1:],
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def setup_sigma_rules(data_dir=None):
    """Ensure Sigma (Zircolite JSON) rules are available.

    Priority:
    1. Cached rules in ~/socrates-data/sigma-rules/
    2. Baked-in rules in /usr/share/sigma-rules (Docker)
    3. Download from Zircolite-Rules-v2 if internet is available

    Returns dict mapping 'windows'/'linux' to file path, or None for each.
    """
    if data_dir is None:
        data_dir = os.path.expanduser('~/socrates-data')
    rules_dir = os.path.join(data_dir, SIGMA_RULES_SUBDIR)
    os.makedirs(rules_dir, exist_ok=True)

    result = {}
    for ruleset_name, url in ZIRCOLITE_RULES_URLS.items():
        rules_file = os.path.join(rules_dir, f'{ruleset_name}.json')

        # Already downloaded/cached — refresh in place if stale and online
        if os.path.isfile(rules_file):
            if _rules_stale(rules_file) and _has_internet_access():
                print(f'Sigma rules ({ruleset_name}) are stale — refreshing...')
                try:
                    _download_rule_file(url, rules_file)
                    print(f'Sigma rules ({ruleset_name}) refreshed')
                except (OSError, urllib.error.URLError) as e:
                    print(f'Warning: could not refresh Sigma rules ({ruleset_name}), using cached: {e}')
            result[ruleset_name] = rules_file
            continue

        # Baked-in rules (Docker image)
        baked_in = os.path.join(BAKED_IN_SIGMA_DIR, f'{ruleset_name}.json')
        if os.path.isfile(baked_in):
            try:
                shutil.copy2(baked_in, rules_file)
                result[ruleset_name] = rules_file
                continue
            except OSError as e:
                print(f'Warning: could not copy baked-in Sigma rules: {e}')

        # Try to download
        if _has_internet_access():
            try:
                _download_rule_file(url, rules_file)
                result[ruleset_name] = rules_file
                continue
            except (OSError, urllib.error.URLError) as e:
                print(f'Warning: could not download Sigma rules ({ruleset_name}): {e}')
        else:
            print('No internet access detected — Sigma rules not available')

    return result


def _has_internet_access():
    return is_host_reachable('github.com', 443, timeout=5)


def _rules_stale(path, max_age_days=None):
    """Return True if path is older than max_age_days (default config.RULE_REFRESH_DAYS)."""
    if max_age_days is None:
        max_age_days = config.RULE_REFRESH_DAYS
    try:
        age_seconds = time.time() - os.path.getmtime(path)
    except OSError:
        return False
    return age_seconds > max_age_days * 86400


def _download_rule_file(url, dest_file):
    """Download a single rule file from URL to dest_file."""
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=config.YARA_DOWNLOAD_TIMEOUT) as resp:
        with open(dest_file, 'wb') as f:
            f.write(resp.read())


def _detect_log_type(log_path):
    """Auto-detect whether a log file is Windows or Linux flavored.

    Returns 'windows', 'linux', or None.
    """
    # Quick filename-based hints
    basename = os.path.basename(log_path).lower()
    if basename.endswith('.evtx'):
        return 'windows'

    # Content-based detection
    try:
        with open(log_path, 'rb') as f:
            # Read up to 64KB for inspection
            sample = f.read(64 * 1024)
    except OSError:
        return None

    text = sample.decode('utf-8', errors='ignore')

    # Windows EVTX XML export or JSON with Windows-specific fields
    win_indicators = [
        'EventID',
        'Channel',
        'ProviderName',
        'ComputerName',
        'Microsoft-Windows-Sysmon',
        'Security',
        'System',
        'EventRecordID',
    ]
    linux_indicators = [
        'auditd',
        'type=SYSCALL',
        'type=EXECVE',
        'auid=',
        'uid=',
        'exe=',
        'sysmon-for-linux',
    ]

    win_score = sum(1 for ind in win_indicators if ind in text)
    linux_score = sum(1 for ind in linux_indicators if ind in text)

    if win_score > linux_score and win_score >= 2:
        return 'windows'
    if linux_score > win_score and linux_score >= 2:
        return 'linux'

    # Fallback: if we see common Windows event IDs (4-digit numbers in JSON),
    # lean toward Windows
    if basename.endswith('.json') or basename.endswith('.jsonl'):
        import re
        if re.search(r'"EventID"\s*:\s*\d{3,5}', text):
            return 'windows'

    return None


def run_zircolite(log_path, rules_file, output_json, output_db=None, data_dir=None):
    """Run Zircolite on a log file and write results to output_json.

    If output_db is provided, also writes a unified SQLite database with
    all parsed events (not just matches).

    Returns (success, db_path) where db_path is output_db if it was created.
    """
    zircolite = _zircolite_cmd(data_dir)
    if not zircolite:
        print('Zircolite not available — skipping Sigma analysis')
        return False, None

    if not os.path.isfile(rules_file):
        print(f'Sigma rules file not found: {rules_file}')
        return False, None

    config_file = _zircolite_config(data_dir)
    if not config_file:
        print('Zircolite config file not found — Sigma analysis cannot run')
        return False, None

    # Zircolite requires --no-parallel when using --dbfile with single file,
    # and --unified-db to write all events into one DB.
    temp_db = output_db or os.path.join(os.path.dirname(output_json), '.zircolite_events.db')

    # Write Zircolite's own log file to the analysis directory, not the project root
    zircolite_log = os.path.join(os.path.dirname(output_json), 'zircolite.log')

    python_cmd = _zircolite_python(data_dir)
    try:
        cmd = [
            python_cmd, zircolite,
            '--events', log_path,
            '--ruleset', rules_file,
            '-o', output_json,
            '-c', config_file,
            '-d', temp_db,
            '-l', zircolite_log,
            '--unified-db',
            '--no-parallel',
            '--no-event-filter',
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=config.SIGMA_RUN_TIMEOUT
        )
        if result.returncode != 0:
            # Zircolite may write warnings to stderr; only treat as error
            # if output file was not produced
            if not os.path.exists(output_json):
                print(f'Zircolite error: {result.stderr}')
                return False, None
        return True, temp_db
    except subprocess.TimeoutExpired:
        print(f'Zircolite timed out after {config.SIGMA_RUN_TIMEOUT}s')
        return False, None
    except (subprocess.CalledProcessError, OSError) as e:
        print(f'Zircolite execution error: {e}')
        return False, None


def import_zircolite_logs(zircolite_db_path, events_db_path):
    """Import all log events from a Zircolite unified DB into SO-CRATES's events table.

    Reads every row from the Zircolite 'logs' table and converts it into an
    event dict suitable for db.import_log_events().

    Returns the number of events imported.
    """
    if not os.path.exists(zircolite_db_path):
        return 0

    import sqlite3

    log_events = []
    try:
        conn = sqlite3.connect(zircolite_db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.execute('SELECT * FROM logs')
        columns = [d[0] for d in cur.description]
        for row in cur.fetchall():
            row_dict = {col: row[idx] for idx, col in enumerate(columns)}

            # Build a JSON-serializable dict for the event
            # Zircolite rows may have None for many columns; keep only non-None
            clean_dict = {k: v for k, v in row_dict.items() if v is not None}

            # Timestamp
            timestamp = (
                clean_dict.get('SystemTime') or
                clean_dict.get('UtcTime') or
                clean_dict.get('timestamp') or
                clean_dict.get('TimeCreated') or
                clean_dict.get('TimeCreated_systemTime') or
                ''
            )

            # Network fields (Sysmon network events have these)
            src_ip = clean_dict.get('SourceIp', '') or ''
            dest_ip = clean_dict.get('DestinationIp', '') or ''
            src_port = clean_dict.get('SourcePort', 0) or 0
            dest_port = clean_dict.get('DestinationPort', 0) or 0

            # Protocol / Channel
            protocol = clean_dict.get('Protocol', '') or ''
            app_proto = clean_dict.get('Channel', '') or clean_dict.get('Provider_Name', '') or ''

            log_events.append({
                'event_type': 'log',
                'timestamp': timestamp,
                'src_ip': src_ip,
                'src_port': int(src_port) if src_port else 0,
                'dest_ip': dest_ip,
                'dest_port': int(dest_port) if dest_port else 0,
                'protocol': protocol,
                'app_proto': app_proto,
                'json_data': clean_dict,
            })
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(f'Warning: could not read Zircolite events DB: {e}')
        return 0
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

    if log_events:
        from db import import_log_events
        import_log_events(events_db_path, log_events)

    return len(log_events)


def parse_zircolite_results(output_json):
    """Parse Zircolite JSON output into a list of alert dicts.

    One alert dict is emitted per matched event (not per rule), so that each
    row in the Sigma Alerts table represents an individual detection.

    Zircolite v3 output format (list of detection objects):
        {
            'title': 'Rule Name',
            'id': 'uuid',
            'rule_level': 'high',
            'tags': ['attack.t1033', 'attack.discovery'],
            'count': 3,
            'matches': [{...event fields...}]
        }

    Each alert dict contains:
        - timestamp (from the specific match)
        - rule_title
        - rule_id
        - severity (from rule_level)
        - level (same as severity)
        - logsource (from detection or match)
        - tags
        - mitre_techniques
        - original_log (the specific matched event)
        - json_data (full Zircolite result entry)
    """
    if not os.path.exists(output_json):
        return []

    try:
        with open(output_json, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    alerts = []
    # Zircolite v3 output format: list of detection objects
    if isinstance(data, list):
        detections = data
    elif isinstance(data, dict):
        detections = data.get('detections', data.get('results', []))
    else:
        detections = []

    for detection in detections:
        if not isinstance(detection, dict):
            continue

        # Extract MITRE technique IDs from tags
        tags = detection.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        mitre_techniques = [t for t in tags if t.startswith('attack.t') or t.startswith('attack.T')]

        # Resolve the list of matched events
        matches = detection.get('matches', [])
        if not matches:
            # Legacy Zircolite output uses 'event' instead of 'matches'
            single_event = detection.get('event', {})
            if single_event:
                matches = [single_event]
            else:
                continue

        # Detection-level logsource
        detection_logsource = detection.get('channel', detection.get('logsource', ''))

        for match in matches:
            # Try to extract timestamp from the match
            timestamp = ''
            for ts_field in ('SystemTime', 'UtcTime', 'timestamp', 'TimeCreated', 'TimeCreated_systemTime'):
                if ts_field in match:
                    timestamp = match[ts_field]
                    break

            # Fallback logsource from the matched event itself
            logsource = detection_logsource
            if not logsource:
                logsource = match.get('Channel') or match.get('Provider_Name', '')

            alert = {
                'timestamp': timestamp,
                'rule_title': detection.get('title', 'Unknown'),
                'rule_id': detection.get('id', ''),
                'severity': detection.get('rule_level', 'low').lower(),
                'level': detection.get('rule_level', 'low').lower(),
                'logsource': logsource,
                'tags': tags,
                'mitre_techniques': mitre_techniques,
                'original_log': json.dumps(match),
                'json_data': json.dumps(detection),
            }
            alerts.append(alert)

    return alerts


def run_sigma_pipeline(dir_path, log_path, data_dir=None):
    """Full Sigma pipeline: detect log type, run Zircolite, write results.

    Returns (success, zircolite_db_path) where zircolite_db_path is the path
    to the unified events DB if it was created, or None on failure.
    """
    if data_dir is None:
        data_dir = os.path.expanduser('~/socrates-data')

    if not is_zircolite_available(data_dir):
        print('Zircolite not available — skipping Sigma analysis')
        return False, None

    rules = setup_sigma_rules(data_dir)
    if not rules:
        print('Sigma rules not available')
        return False, None

    # Auto-detect log type and select ruleset
    detected = _detect_log_type(log_path)
    if detected == 'linux' and rules.get('linux'):
        ruleset = rules['linux']
    elif detected == 'windows' and rules.get('windows'):
        ruleset = rules['windows']
    else:
        # Fallback: use windows rules (largest coverage) if available,
        # otherwise linux
        ruleset = rules.get('windows') or rules.get('linux')

    output_json = os.path.join(dir_path, 'sigma_matches.json')
    temp_db = os.path.join(dir_path, '.zircolite_events.db')
    success, _ = run_zircolite(log_path, ruleset, output_json, output_db=temp_db, data_dir=data_dir)
    if success and os.path.exists(temp_db):
        return True, temp_db
    return success, None
