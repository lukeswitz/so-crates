#!/usr/bin/env python3
"""Check tshark against Suricata across a corpus of real captures - before
trusting a change to shark_analyzer, a tshark or Suricata upgrade, or a
new protocol in shark_protocols.

The corpus is a directory of capture subdirectories plus Suricata's output
for each in eve/, named <subdir>__<capture>.eve.json - a nested subdir with
+ for / (ics_iti+BACnet__bacnet_test.pcap.eve.json) - (run Suricata in the
SO-CRATES image, so it's the same version and config). For each capture,
this runs tshark and the merge's selection (shark_analyzer.merge_rows),
compares flows with Suricata's (compare_shark_suricata), and prints totals:
flows matched and reoriented, and the rows tshark would add to the
analysis by type.

The captures aren't part of the repository (malware-traffic-analysis.net
infection and training-exercise pcaps, the 4SICS ICS captures and others
- see the docs' testing page).

Usage: python3 scripts/sweep_shark_suricata.py <corpus dir> [<subdir> ...]
"""

import collections
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    if len(argv) < 2 or not os.path.isdir(os.path.join(argv[1], 'eve')):
        print(__doc__)
        return 2
    import db
    import shark_analyzer
    from compare_shark_suricata import compare, _load_eve
    corpus, only = argv[1], set(argv[2:])
    flows, added = collections.Counter(), collections.Counter()
    for name in sorted(os.listdir(os.path.join(corpus, 'eve'))):
        if not name.endswith('.eve.json') or '__' not in name:
            continue
        subdir, pcap = name[:-len('.eve.json')].split('__', 1)
        if only and not (subdir in only or subdir.split('+')[0] in only):
            continue
        eve = os.path.join(corpus, 'eve', name)
        shark = shark_analyzer.run_tshark(os.path.join(corpus, *subdir.split('+'), pcap), timeout=1800)
        r = compare(_load_eve(eve), shark)['flow']
        for k in ('suricata', 'shark', 'matched', 'reoriented', 'named_by_tshark'):
            flows[k] += r[k]
        with tempfile.TemporaryDirectory() as tmp:
            events_db = os.path.join(tmp, 'events.db')
            db.create_sqlite_db(events_db, eve)
            rows = list(shark_analyzer.merge_rows((json.dumps(e) for e in shark), db.suricata_identified_flows(events_db)))
        these = collections.Counter(e['event_type'] for e in rows)
        added.update(these)
        print(f"{subdir}/{pcap[:50]}: flows {r['matched']}/{r['suricata']} matched ({r['named_by_tshark']} named by tshark), "
              f"{r['reoriented']} reoriented; "
              f"adds {dict(these.most_common(6))}", flush=True)
    print(f"\nflows: {flows['matched']} of Suricata's {flows['suricata']} matched (tshark {flows['shark']}; "
          f"{flows['named_by_tshark']} named only by tshark), {flows['reoriented']} reoriented")
    print('rows tshark adds:', dict(added.most_common()))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
