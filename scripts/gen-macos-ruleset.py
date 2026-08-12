#!/usr/bin/env python3
"""Regenerate rules/macos.json, the Zircolite ruleset SO-CRATES runs against
macOS Endpoint Security telemetry.

Zircolite-Rules-v2 publishes Windows and Linux rulesets only, so this builds
the macOS one the same way upstream builds Linux: pySigma's sqlite backend
with no field-mapping pipeline, so rules keep Sigma's own field names, which
is exactly what scripts/eslogger_to_sigma.py emits.

Sources, in order:
  1. SigmaHQ rules/macos                  - process_creation + file_event
  2. SigmaHQ rules-threat-hunting/macos
  3. SigmaHQ rules-emerging-threats       - entries whose product is macos
  4. SigmaHQ rules/linux/process_creation - only rules whose fields are a
     subset of what eslogger gives us, since generic *nix tradecraft
     (curl|bash, base64 -d, chmod +x, nc shells) runs on macOS unchanged
  5. rules/macos-endpoint-security/       - rules in this repo for the ES
     events SigmaHQ has no coverage for at all (XProtect detections,
     persistence via Background Task Management, Gatekeeper overrides,
     TCC changes, kext loads, remote thread creation, logins)

Usage:
    python3 scripts/gen-macos-ruleset.py --sigma /path/to/SigmaHQ/sigma \\
        [--backend /path/to/pySigma-backend-sqlite] [--out rules/macos.json]

Needs pysigma installed and a checkout of wagga40/pySigma-backend-sqlite.
"""

import argparse
import json
import os
import sys

LEVEL_ORDER = ['informational', 'low', 'medium', 'high', 'critical']

# Fields scripts/eslogger_to_sigma.py can populate. A borrowed Linux rule is
# only included if every field it tests is in here.
ESLOGGER_FIELDS = {
    'Image', 'CommandLine', 'ParentImage', 'ParentCommandLine',
    'OriginalFileName', 'TargetFilename', 'User', 'ProcessId',
}


def _detection_fields(rule):
    """Every field name a Sigma rule tests.

    Walks pySigma's parsed objects (SigmaDetection -> SigmaDetectionItem),
    not the raw YAML: detection items nest, and a keyword-only item carries
    field=None, which is reported as the sentinel '' so callers can tell
    "matches bare keywords" apart from "matches a named field".
    """
    fields = set()

    def walk(node):
        for item in getattr(node, 'detection_items', []) or []:
            field = getattr(item, 'field', None)
            if field is not None:
                fields.add(str(field))
            elif not hasattr(item, 'detection_items'):
                fields.add('')
            walk(item)

    detections = getattr(getattr(rule, 'detection', None), 'detections', {}) or {}
    for detection in detections.values():
        walk(detection)
    return fields


def collect_rule_paths(args):
    """Return (label, [paths]) groups in the order they should be converted."""
    sigma = args.sigma
    groups = []

    def yml_under(*parts):
        root = os.path.join(sigma, *parts)
        found = []
        for dirpath, _dirs, files in os.walk(root):
            found.extend(os.path.join(dirpath, f) for f in files if f.endswith('.yml'))
        return sorted(found)

    groups.append(('sigmahq-macos', yml_under('rules', 'macos')))
    groups.append(('sigmahq-threat-hunting-macos', yml_under('rules-threat-hunting', 'macos')))

    emerging = []
    for path in yml_under('rules-emerging-threats'):
        try:
            with open(path, 'r', errors='ignore') as f:
                if 'product: macos' in f.read():
                    emerging.append(path)
        except OSError:
            continue
    groups.append(('sigmahq-emerging-threats-macos', sorted(emerging)))

    groups.append(('sigmahq-linux-process-creation', yml_under('rules', 'linux', 'process_creation')))

    return groups


PRECONVERTED_RULESETS = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'rules', 'macos-endpoint-security.json'),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sigma', required=True, help='Path to a SigmaHQ/sigma checkout')
    parser.add_argument('--backend', help='Path to a pySigma-backend-sqlite checkout')
    parser.add_argument('--out', default=None, help='Output path (default: rules/macos.json)')
    args = parser.parse_args()

    if args.backend:
        sys.path.insert(0, args.backend)

    from sigma.collection import SigmaCollection
    from sigma.backends.sqlite import sqliteBackend

    backend = sqliteBackend(None)
    out_path = args.out or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rules', 'macos.json')

    ruleset, seen_ids = [], set()
    for label, paths in collect_rule_paths(args):
        if not paths:
            print(f'  {label}: no rules found')
            continue
        collection = SigmaCollection.load_ruleset(paths)
        kept = skipped_fields = skipped_dupe = failed = 0
        for rule in collection:
            if label == 'sigmahq-linux-process-creation':
                if not _detection_fields(rule) <= ESLOGGER_FIELDS:
                    skipped_fields += 1
                    continue
            rule_id = str(getattr(rule, 'id', '') or '')
            if rule_id and rule_id in seen_ids:
                skipped_dupe += 1
                continue
            try:
                converted = backend.convert_rule(rule, 'zircolite')[0]
            except Exception:
                failed += 1
                continue
            if rule_id:
                seen_ids.add(rule_id)
            ruleset.append(converted)
            kept += 1
        summary = f'  {label}: {kept} kept'
        if skipped_fields:
            summary += f', {skipped_fields} skipped (fields eslogger cannot supply)'
        if skipped_dupe:
            summary += f', {skipped_dupe} duplicate ids'
        if failed:
            summary += f', {failed} failed conversion'
        print(summary)

    for path in PRECONVERTED_RULESETS:
        if not os.path.isfile(path):
            print(f'  {os.path.basename(path)}: not present, skipping')
            continue
        with open(path) as f:
            preconverted = json.load(f)
        kept = 0
        for rule in preconverted:
            rid = str(rule.get('id', ''))
            if rid and rid in seen_ids:
                continue
            if rid:
                seen_ids.add(rid)
            ruleset.append(rule)
            kept += 1
        print(f'  {os.path.basename(path)}: {kept} preconverted rules')

    ruleset.sort(key=lambda d: LEVEL_ORDER.index(d.get('level', 'informational')))
    with open(out_path, 'w') as f:
        json.dump(ruleset, f, indent=2)

    levels = {}
    for rule in ruleset:
        levels[rule.get('level')] = levels.get(rule.get('level'), 0) + 1
    print(f'\nWrote {out_path}: {len(ruleset)} rules {levels}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
