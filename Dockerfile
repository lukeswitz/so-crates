FROM debian:13-slim AS zircolite-builder

ENV DEBIAN_FRONTEND=noninteractive

# Build-only stage: compiles the Zircolite venv (evtx/orjson have Rust
# extensions, lxml has a C extension) so the Rust toolchain, build-essential,
# dev headers, and git never need to exist in the final runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-venv \
    python3-dev \
    build-essential \
    rustc \
    cargo \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch v3.7.1 \
    https://github.com/wagga40/Zircolite.git /usr/local/lib/zircolite && \
    rm -rf /usr/local/lib/zircolite/.git && \
    python3 -m venv /usr/local/lib/zircolite-venv && \
    /usr/local/lib/zircolite-venv/bin/pip install --no-cache-dir \
    -r /usr/local/lib/zircolite/requirements.txt && \
    rm -rf /usr/local/lib/zircolite/rules /usr/local/lib/zircolite/gui \
    /usr/local/lib/zircolite/pics /usr/local/lib/zircolite/tests \
    /usr/local/lib/zircolite/docs /usr/local/lib/zircolite/templates \
    /usr/local/lib/zircolite/tools /usr/local/lib/zircolite/README.md \
    /usr/local/lib/zircolite/LICENSE /usr/local/lib/zircolite/CODE_OF_CONDUCT.md \
    /usr/local/lib/zircolite/SECURITY.md /usr/local/lib/zircolite/Zircolite.spec \
    /usr/local/lib/zircolite/Taskfile.yml /usr/local/lib/zircolite/Dockerfile \
    /usr/local/lib/zircolite/pytest.ini /usr/local/lib/zircolite/requirements.txt


FROM debian:13-slim AS playbooks-builder

ENV DEBIAN_FRONTEND=noninteractive

# Build-only stage: converts Security Onion's Playbooks repo (~125MB of
# per-rule YAML, most of it Elasticsearch/Sigma-syntax query blocks
# SO-CRATES doesn't use - see playbook_lookup.py) into two small
# gzip-compressed JSON indexes, one per detection type, holding only the
# plain-English investigation guidance. python3-yaml and the raw YAML
# tree never need to exist in the final runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-yaml \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 \
    https://github.com/Security-Onion-Solutions/securityonion-resources-playbooks.git \
    /tmp/playbooks-src

# Consolidates each detection type's individual-rule playbooks plus its
# single engine-wide fallback entry into one {rule_id: {...}, "_default":
# {...}} dict, gzip-compressed - one compressed index per type beats
# baking in ~58k separate small files: that many tiny files round up to
# at least one filesystem block each regardless of content size, and
# gzip compresses far better across many similar records at once than one
# tiny file at a time (see playbook_lookup.py's own comment on this).
# Category-tier playbooks are deliberately not baked in - only 3 files
# exist upstream and their category key doesn't match this app's own
# alert.category field, so the extra matching logic isn't worth it for
# the little it would add on top of the individual+engine tiers.
RUN mkdir -p /tmp/playbooks-out && python3 - <<'PY'
import gzip
import json
import os
import yaml

SRC = '/tmp/playbooks-src/public'
OUT = '/tmp/playbooks-out'


def slim(entry):
    return {
        'name': entry.get('name', ''),
        'description': entry.get('description', ''),
        'questions': [
            {'question': q.get('question', ''), 'context': q.get('context', '')}
            for q in (entry.get('questions') or [])
        ],
    }


for detection_type, engine_file in (('nids', 'engine_nids.yaml'), ('sigma', 'engine_sigma.yaml')):
    index = {}
    individual_dir = os.path.join(SRC, detection_type, 'individual')
    for filename in os.listdir(individual_dir):
        if not filename.endswith('.yaml'):
            continue
        rule_id = filename[:-len('.yaml')]
        with open(os.path.join(individual_dir, filename)) as f:
            entry = yaml.safe_load(f)
        index[rule_id] = slim(entry)
    with open(os.path.join(SRC, detection_type, 'engine', engine_file)) as f:
        index['_default'] = slim(yaml.safe_load(f))
    out_path = os.path.join(OUT, f'{detection_type}.json.gz')
    with gzip.open(out_path, 'wt', encoding='utf-8') as f:
        json.dump(index, f)
    print(f'Baked {len(index)} {detection_type} playbook entries -> {out_path}')
PY


FROM debian:13-slim

ENV DEBIAN_FRONTEND=noninteractive

# debian:13-slim's own repo only has Suricata 7.0.10, which is missing eve
# logging for several protocols this app supports (enip/ntp - no output
# module in 7.0.10 at all; websocket/pop3/mdns/ldap/arp - don't exist in
# 7.0.10's app-layer protocol list at all). Suricata 8 is available via
# Debian's own trixie-backports repo (8.0.6 as of writing, confirmed via
# packages.debian.org) - this mirrors the exact upgrade path validated on a
# real trixie install, rather than pulling in OISF's own third-party repo.
# suricata-update is pulled from backports too (1.3.8 vs. regular trixie's
# 1.3.4) - 1.3.8 fixes a real security issue (arbitrary file write via path
# traversal in rule archive extraction: OISF redmine #8633), not just a
# Suricata-8 compatibility nicety.
RUN echo "deb http://deb.debian.org/debian trixie-backports main" > /etc/apt/sources.list.d/trixie-backports.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    tcpdump \
    tshark \
    yara \
    curl \
    file \
    libimage-exiftool-perl \
    libxml2 \
    libxslt1.1 \
    && apt-get install -y --no-install-recommends -t trixie-backports suricata suricata-update \
    && rm -rf /var/lib/apt/lists/*

COPY --from=zircolite-builder /usr/local/lib/zircolite /usr/local/lib/zircolite
COPY --from=zircolite-builder --chown=1000:1000 /usr/local/lib/zircolite-venv /usr/local/lib/zircolite-venv
RUN ln -s /usr/local/lib/zircolite/zircolite.py /usr/local/bin/zircolite.py

ENV DATA_DIR=/data
ENV BIND_ADDRESS=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY config.py db.py models.py validators.py suricata_analyzer.py suricata_sid_ranges.py yara_analyzer.py sigma_analyzer.py file_analyzer.py exif_analyzer.py ohmydebn_colors.py playbook_lookup.py socrates.py socrates.html ./
COPY static/ static/
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Bake Suricata rules into image for air-gapped deployments
# Enable protocols that are disabled by default so their rules are included.
RUN python3 - <<'PY'
import re
with open('/etc/suricata/suricata.yaml', 'r') as f:
    content = f.read()
for proto in ('pgsql', 'modbus', 'dnp3', 'enip'):
    content = re.sub(
        rf'(?m)^(\s+{proto}:\s*\n(?:\s*#.*\n)*\s+)enabled:\s*no',
        r'\1enabled: yes',
        content
    )
with open('/etc/suricata/suricata.yaml', 'w') as f:
    f.write(content)
PY
# One static rules file per curated source (not a single merged
# suricata.rules) - lets an airgapped user toggle among whatever's baked
# in here entirely offline at runtime (see suricata_analyzer.py's
# rules-available/ library + _reconcile_suricata_sources()), instead of
# depending on suricata-update's own enable-source/disable-source state,
# which lives in a --data-dir with no relationship between this build-time
# image and the runtime /data volume. Reuses today's exact per-source
# merge mechanism (isolated scratch --data-dir with only one source
# enabled), just run once per curated slug instead of once overall.
#
# BAKED_IN_SURICATA_SOURCES (suricata_analyzer.py) deliberately excludes
# ipfire/dbl - measured as the single biggest space cost of the curated
# set (~51 of ~83 MiB, via its dataset:-based domain lists) and, being a
# content-filtering blocklist (ads/dating/gambling/social/streaming/etc.
# categories) rather than threat detection, would mostly just add alert
# noise on ordinary browsing traffic. It stays selectable for online users
# to fetch on demand via the Rules modal.
RUN mkdir -p /usr/share/suricata/rules-available && python3 - <<'PY'
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, '/app')
from suricata_analyzer import BAKED_IN_SURICATA_SOURCES, _source_filename

for slug in BAKED_IN_SURICATA_SOURCES:
    scratch_data = tempfile.mkdtemp()
    scratch_out = tempfile.mkdtemp()
    try:
        subprocess.run(
            ['suricata-update', 'enable-source', slug, '--data-dir', scratch_data],
            check=True,
        )
        # enable-source on a brand-new --data-dir always ALSO silently
        # auto-enables et/open as its own "default source" regardless of
        # what was actually requested - must be explicitly disabled again
        # for every other source, or this isolated single-source fetch
        # isn't actually isolated (verified: an unpatched fetch of
        # oisf/trafficid alone produced a merged file with et/open's full
        # ~52k rules mixed in, not just trafficid's 34).
        if slug != 'et/open':
            subprocess.run(
                ['suricata-update', 'disable-source', 'et/open', '--data-dir', scratch_data],
                check=True,
            )
        subprocess.run(
            ['suricata-update', '--no-test', '--suricata-conf', '/etc/suricata/suricata.yaml',
             '--data-dir', scratch_data, '--output', scratch_out],
            check=True,
        )
        dest = f'/usr/share/suricata/rules-available/{_source_filename(slug)}'
        shutil.move(os.path.join(scratch_out, 'suricata.rules'), dest)
        print(f'Baked in {slug} -> {dest}')
    finally:
        shutil.rmtree(scratch_data, ignore_errors=True)
        shutil.rmtree(scratch_out, ignore_errors=True)
PY

# Bake YARA Forge rules into image for air-gapped deployments
RUN mkdir -p /usr/share/yara-rules && \
    curl -fsSL -o /tmp/yara-forge-full.zip \
    "https://github.com/YARAHQ/yara-forge/releases/latest/download/yara-forge-rules-full.zip" && \
    python3 -c "import zipfile; zipfile.ZipFile('/tmp/yara-forge-full.zip').extract('packages/full/yara-rules-full.yar', '/tmp/yara-forge-extract')" && \
    mv /tmp/yara-forge-extract/packages/full/yara-rules-full.yar /usr/share/yara-rules/yara-rules-full.yar && \
    rm -rf /tmp/yara-forge-full.zip /tmp/yara-forge-extract

# Bake Sigma rules (Zircolite JSON format) into image for air-gapped
# deployments. Destination filenames must be windows.json/linux.json (not
# the upstream rules_*.json names) - sigma_analyzer.py's setup_sigma_rules()
# looks for '<ruleset>.json' under BAKED_IN_SIGMA_DIR, keyed by the
# ZIRCOLITE_RULES_URLS dict keys ('windows'/'linux'), not by the source URL's
# own filename.
RUN mkdir -p /usr/share/sigma-rules && \
    curl -fsSL -o /usr/share/sigma-rules/windows.json \
    "https://raw.githubusercontent.com/wagga40/Zircolite-Rules-v2/main/rules_windows_merged.json" && \
    curl -fsSL -o /usr/share/sigma-rules/linux.json \
    "https://raw.githubusercontent.com/wagga40/Zircolite-Rules-v2/main/rules_linux.json"

# Bake Security Onion Playbooks (investigation guidance) into image for
# air-gapped deployments - see the playbooks-builder stage above for how
# the raw ~125MB upstream YAML repo becomes these two small
# gzip-compressed indexes, and playbook_lookup.py for how they're read.
COPY --from=playbooks-builder /tmp/playbooks-out/ /usr/share/playbooks/

RUN mkdir -p /data && chown -R 1000:1000 /data

USER 1000:1000

VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
