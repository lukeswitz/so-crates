#!/usr/bin/env python3
"""One-shot inspector for a raw eslogger dump kept via SOCRATES_KEEP_RAW=1.

Prints the count of each Endpoint Security event type in the file, and a
one-line schema sketch for one sample of each. Reads from argv[1] or the
default path in the current directory.
"""

import collections
import json
import sys


def sketch(obj, depth=0, max_depth=3):
    if depth > max_depth or not isinstance(obj, dict):
        return type(obj).__name__
    return '{' + ', '.join(f'{k}: {sketch(v, depth + 1, max_depth)}' for k, v in obj.items()) + '}'


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'macos-events.ndjson.raw.ndjson'
    counts = collections.Counter()
    sample = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            for name, body in record.get('event', {}).items():
                counts[name] += 1
                sample.setdefault(name, body)
    print(f'{sum(counts.values())} events in {path}')
    print()
    for name, count in counts.most_common():
        print(f'  {count:6d}  {name}')
    print()
    print('=== one sample body per event type ===')
    for name in counts:
        print(f'\n[{name}] {sketch(sample[name])}')


if __name__ == '__main__':
    main()
