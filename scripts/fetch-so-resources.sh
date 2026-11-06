#!/bin/sh
set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <data directory>" >&2
    exit 1
fi

DATA_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

python3 -m venv "$WORK_DIR/venv"
"$WORK_DIR/venv/bin/pip" install --quiet --disable-pip-version-check pyyaml==6.0.3
git clone --quiet --depth 1 \
    https://github.com/Security-Onion-Solutions/securityonion-resources-playbooks.git \
    "$WORK_DIR/playbooks"
git clone --quiet --depth 1 --branch generated-summaries-published --single-branch \
    https://github.com/Security-Onion-Solutions/securityonion-resources.git \
    "$WORK_DIR/summaries"
"$WORK_DIR/venv/bin/python" "$SCRIPT_DIR/build_so_resources.py" \
    "$WORK_DIR/playbooks" "$WORK_DIR/summaries" "$DATA_DIR/playbooks" "$DATA_DIR/ai-summaries"
