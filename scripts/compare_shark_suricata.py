#!/usr/bin/env python3
"""Compare tshark's flows for a PCAP (shark_analyzer) with Suricata's
(eve.json) - the one record type both build.

Flows are matched by Community ID - in time order where a reused 5-tuple
gives several flows one ID - and their addresses, ports, protocol, packet
and byte counts and times compared. Prints the counts and each
difference, and exits 1 if there are any.

Differences aren't automatically bugs: the tools draw some connections'
boundaries differently (Suricata ends a flow when it goes idle; tshark
starts a new one on a new SYN), and tshark addresses a flow from whoever
made its first request where Suricata goes by its first packet
('reoriented', compared from Suricata's side). Each should be fixed in
shark_analyzer or understood.

Usage:
    python3 scripts/compare_shark_suricata.py <pcap> <eve.json>
    python3 scripts/compare_shark_suricata.py <analysis dir>   # its pcap, Suricata's events and shark.db

Also importable: compare(suricata_events, shark_events) -> report dict.
"""

import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def _flow_fields(e):
    f = e['flow']
    return {'src': (e.get('src_ip'), e.get('src_port')), 'dest': (e.get('dest_ip'), e.get('dest_port')),
            # Suricata says 'failed' where it found no application protocol
            'proto': e.get('proto'), 'app_proto': None if e.get('app_proto') in (None, '', 'failed') else e['app_proto'],
            **{k: f.get(k) for k in ('pkts_toserver', 'pkts_toclient', 'bytes_toserver', 'bytes_toclient',
                                     'start', 'end')}}


def _reversed_flow(fields):
    """A flow's fields seen from its other side."""
    out = dict(fields, src=fields['dest'], dest=fields['src'])
    for a, b in (('pkts_toserver', 'pkts_toclient'), ('bytes_toserver', 'bytes_toclient')):
        out[a], out[b] = fields[b], fields[a]
    return out


def compare(suricata_events, shark_events):
    """{'flow': {'suricata': n, 'shark': n, 'matched': n, 'reoriented': n,
    'named_by_tshark': n, 'differences': [...]}} - named_by_tshark of the
    matched being flows Suricata gave no protocol and tshark did. A reoriented flow - tshark's client is whoever
    made the first request, or was answered first, where Suricata's is
    whoever sent the first packet (shark_analyzer._Flow.orient) - is
    compared from Suricata's side, so only its other fields can differ."""
    def index(events):
        # Suricata writes a flow out when it ends: order by start
        out, seen = {}, {}
        for e in sorted(events, key=lambda e: (e.get('flow') or {}).get('start') or e.get('timestamp') or ''):
            if e.get('event_type') == 'flow':
                cid = e.get('community_id')
                seen[cid] = seen.get(cid, -1) + 1
                out[(cid, seen[cid])] = e
        return out
    a, b = index(suricata_events), index(shark_events)
    result = {'suricata': len(a), 'shark': len(b), 'matched': 0, 'reoriented': 0, 'named_by_tshark': 0, 'differences': []}
    for key in sorted(set(a) | set(b), key=str):
        if key not in b:
            result['differences'].append({'key': key, 'only': 'suricata', 'record': _flow_fields(a[key])})
            continue
        if key not in a:
            result['differences'].append({'key': key, 'only': 'shark', 'record': _flow_fields(b[key])})
            continue
        fa, fb = _flow_fields(a[key]), _flow_fields(b[key])
        if fa['src'] == fb['dest'] and fa['dest'] == fb['src'] and fa['src'] != fa['dest']:
            fb = _reversed_flow(fb)
            result['reoriented'] += 1
        diff = {k: (fa.get(k), fb.get(k)) for k in fa if fa.get(k) != fb.get(k)}
        if set(diff) == {'app_proto'} and diff['app_proto'][0] is None:
            # a protocol Suricata doesn't parse, which tshark named - what
            # it's there for, not a difference
            result['named_by_tshark'] += 1
            diff = {}
        if diff:
            result['differences'].append({'key': key, 'fields': diff})
        else:
            result['matched'] += 1
    return {'flow': result}


def _load_eve(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _load_suricata_events(path):
    """Suricata's events from an analysis's events.db - its eve.json is
    removed once imported - leaving out the rows tshark's merge added."""
    conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try:
        return [json.loads(row[0]) for row in conn.execute(
            "SELECT json_data FROM events WHERE json_extract(json_data, '$.source') IS NOT 'tshark'")]
    finally:
        conn.close()


def _load_shark_db(path):
    conn = sqlite3.connect(path)
    try:
        return [json.loads(row[0]) for row in conn.execute('SELECT json_data FROM events')]
    finally:
        conn.close()


def main(argv):
    if len(argv) == 2 and os.path.isdir(argv[1]):
        from storage import find_pcap_file
        eve = os.path.join(argv[1], 'eve.json')
        suricata = _load_eve(eve) if os.path.exists(eve) else _load_suricata_events(os.path.join(argv[1], 'events.db'))
        shark_db = os.path.join(argv[1], 'shark.db')
        if os.path.exists(shark_db):
            shark = _load_shark_db(shark_db)
        else:
            pcap = find_pcap_file(argv[1])
            if not pcap:
                print(f'{argv[1]}: no capture and no shark.db', file=sys.stderr)
                return 2
            from shark_analyzer import run_tshark
            shark = run_tshark(os.path.join(argv[1], pcap))
    elif len(argv) == 3:
        from shark_analyzer import run_tshark
        suricata, shark = _load_eve(argv[2]), run_tshark(argv[1])
    else:
        print(__doc__)
        return 2
    r = compare(suricata, shark)['flow']
    print(f"flow  suricata {r['suricata']}  shark {r['shark']}  matched {r['matched']}  "
          f"differences {len(r['differences'])}  reoriented {r['reoriented']}  named by tshark {r['named_by_tshark']}")
    for d in r['differences']:
        print('   ', json.dumps(d, default=str))
    return 1 if r['differences'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
