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
COPY config.py db.py models.py validators.py suricata_analyzer.py yara_analyzer.py sigma_analyzer.py file_analyzer.py exif_analyzer.py ohmydebn_colors.py socrates.py socrates.html ./
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
RUN mkdir -p /usr/share/suricata/rules && \
    suricata-update --no-test --suricata-conf /etc/suricata/suricata.yaml --data-dir /usr/share/suricata --output /usr/share/suricata/rules

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

RUN mkdir -p /data && chown -R 1000:1000 /data

USER 1000:1000

VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
