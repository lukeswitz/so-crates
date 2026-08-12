#!/bin/sh
# Generate real self-cleaning macOS activity to exercise the ES-only Sigma rules.
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-trigger-test.ndjson}"
DUR=25

usage() {
    cat <<EOF
Generate real, self-cleaning macOS activity so the ES-only Sigma rules in
rules/macos-endpoint-security.json have something to match. Everything runs
against /tmp scratch paths and reverts itself.

Usage:
    sudo sh scripts/trigger-macos-detections.sh [output-file]

Runs a ${DUR}s eslogger capture while triggering sudo, mount, LaunchAgent add,
osacompile exec, then converts and prints the file you can upload to SO-CRATES.
EOF
}

case "${1:-}" in
    -h|--help) usage; exit 0 ;;
esac

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: eslogger needs root. Re-run:" >&2
    echo "    sudo sh $0 $OUT" >&2
    exit 1
fi

command -v /usr/bin/eslogger >/dev/null 2>&1 || {
    echo "Error: /usr/bin/eslogger not found (needs macOS 13+)" >&2; exit 1;
}

TMP_DMG=/tmp/socrates-trigger.dmg
TMP_LA_LABEL="socrates.trigger.test"
TMP_LA_FILE="/tmp/${TMP_LA_LABEL}.plist"
TMP_MOUNT=/tmp/socrates-trigger-mnt
TARGET_USER="${SUDO_USER:-$USER}"
TARGET_UID="$(id -u "$TARGET_USER")"
cleanup() {
    launchctl bootout "gui/${TARGET_UID}/${TMP_LA_LABEL}" 2>/dev/null || true
    hdiutil detach -force "$TMP_MOUNT" 2>/dev/null || true
    rm -rf "$TMP_MOUNT" 2>/dev/null || true
    rm -f "$TMP_DMG" "$TMP_LA_FILE" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Starting ${DUR}s Endpoint Security capture..."
RAW="$(mktemp -t socrates-trigger)"
/usr/bin/eslogger exec create mount sudo su btm_launch_item_add \
    tcc_modify kextload setuid > "$RAW" 2>/dev/null &
ESPID=$!
START=$(date +%s)
sleep 2

echo "==> Triggering: sudo whoami"
sudo -k
sudo -n whoami >/dev/null 2>&1 || sudo whoami >/dev/null 2>&1 || true

echo "==> Triggering: hdiutil mount + detach"
mkdir -p "$TMP_MOUNT"
hdiutil create -size 10m -fs 'HFS+' -volname socrates-trigger \
    -ov "$TMP_DMG" >/dev/null 2>&1
hdiutil attach "$TMP_DMG" -mountpoint "$TMP_MOUNT" -nobrowse >/dev/null 2>&1 || true
sleep 1
hdiutil detach -force "$TMP_MOUNT" >/dev/null 2>&1 || true

echo "==> Triggering: LaunchAgent write + remove"
mkdir -p "$TMP_LA_DIR"
cat > "$TMP_LA_FILE" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>socrates.trigger.test</string>
<key>ProgramArguments</key><array><string>/usr/bin/true</string></array>
<key>RunAtLoad</key><false/>
</dict></plist>
PLIST
sleep 1
rm -f "$TMP_LA_FILE"

echo "==> Triggering: osacompile (fires an existing high-sev rule)"
/usr/bin/osacompile -x -e 'do shell script "id"' -o /tmp/socrates-trigger.scpt >/dev/null 2>&1 || true
rm -f /tmp/socrates-trigger.scpt

while true; do
    ELAPSED=$(( $(date +%s) - START ))
    [ "$ELAPSED" -ge "$DUR" ] && break
    kill -0 "$ESPID" 2>/dev/null || break
    sleep 1
done
kill -TERM "$ESPID" 2>/dev/null || true
wait "$ESPID" 2>/dev/null || true

RAW_LINES=$(wc -l < "$RAW" | tr -d ' ')
echo "==> Captured $RAW_LINES raw events; converting..."
python3 "$HERE/eslogger_to_sigma.py" < "$RAW" > "$OUT"
[ -n "${SUDO_USER:-}" ] && chown "$SUDO_USER" "$OUT" 2>/dev/null

rm -f "$RAW"
echo ""
echo "==> Wrote $OUT ($(wc -l < "$OUT" | tr -d ' ') events)"
echo "    Upload with: curl -sF file=@$OUT http://127.0.0.1:8899/api/upload"
