#!/usr/bin/env python3
"""Security Onion AI-generated rule summaries lookup for SO-CRATES.

A one-paragraph, plain-English "what this rule detects" summary per
detection rule, baked into the Docker image the same way Playbooks are (see
Dockerfile's resources-builder stage) and for the same reason - see
AGENTS.md's "Detection Rule Freshness" section for why this is static,
baked-in-only content with no runtime refresh.

Each baked-in file is one gzip-compressed JSON dict per detection type:
{"<rule_id>": "<summary text>", ...}. Unlike playbook_lookup.py, there is no
engine-wide "_default" fallback entry - a summary for the wrong rule would be
actively misleading, and upstream doesn't publish one anyway.
"""

import gzip
import json
import os

# Overridable the same way PLAYBOOKS_DIR/DATA_DIR are - lets a local dev
# server point at a real dataset (e.g. one built by hand from the upstream
# repo, for testing without a Docker build) without editing source.
# Production/Docker never sets this, so it defaults to the same path the
# Dockerfile's resources-builder stage bakes into.
AI_SUMMARIES_DIR = os.environ.get('AI_SUMMARIES_DIR', '/usr/share/ai-summaries')

_ai_summary_index_cache = {}  # (base_dir, detection_type) -> index dict


def _load_ai_summary_index(detection_type, base_dir):
    """Loads and decompresses <base_dir>/<detection_type>.json.gz exactly
    once per (base_dir, detection_type), caching the whole parsed dict in
    process memory - every lookup after the first is a plain dict access,
    no further disk I/O or decompression. Returns {} (not None) on a
    missing/corrupt file so callers never need a None-check before
    indexing into it."""
    cache_key = (base_dir, detection_type)
    if cache_key in _ai_summary_index_cache:
        return _ai_summary_index_cache[cache_key]
    index_path = os.path.join(base_dir, f'{detection_type}.json.gz')
    try:
        with gzip.open(index_path, 'rt', encoding='utf-8') as f:
            index = json.load(f)
        if not isinstance(index, dict):
            index = {}
    except (OSError, gzip.BadGzipFile, json.JSONDecodeError):
        index = {}
    _ai_summary_index_cache[cache_key] = index
    return index


def get_ai_summary(detection_type, rule_id, base_dir=None):
    """detection_type is 'nids', 'sigma', or 'yara'. Returns the summary
    text for rule_id if one is baked in, else None (e.g. a local dev run
    with nothing baked in, or a rule with no summary upstream). Never
    raises."""
    index = _load_ai_summary_index(detection_type, base_dir or AI_SUMMARIES_DIR)
    return index.get(str(rule_id)) or None
