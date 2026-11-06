#!/bin/sh
set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <output directory>" >&2
    exit 1
fi

OUT_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

mkdir -p "$OUT_DIR"
for month in "$(date -u +%Y-%m)" "$(date -u -v1d -v-1m +%Y-%m)"; do
    if curl -fsSL -o "$WORK_DIR/dbip.csv.gz" "https://download.db-ip.com/free/dbip-country-lite-${month}.csv.gz"; then
        python3 "$SCRIPT_DIR/build_geoip.py" "$WORK_DIR/dbip.csv.gz" "$OUT_DIR/country.bin.gz" "$month" && exit 0
    fi
done

echo "Error: could not download DB-IP's country data." >&2
exit 1
