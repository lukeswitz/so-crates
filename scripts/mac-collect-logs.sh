#!/bin/sh
# Collect macOS Endpoint Security telemetry for SO-CRATES Sigma analysis.
set -e

ESLOGGER="${SOCRATES_ESLOGGER:-/usr/bin/eslogger}"

# Curated for signal-to-volume: process/file activity plus the security events
# SigmaHQ has no coverage for. Deliberately excludes open/close/stat/lookup/
# access/write/mmap, which flood at thousands of events per second.
DEFAULT_EVENTS="exec create unlink rename mount \
btm_launch_item_add btm_launch_item_remove \
xp_malware_detected xp_malware_remediated gatekeeper_user_override \
tcc_modify kextload kextunload remote_thread_create cs_invalidated \
openssh_login openssh_logout login_login screensharing_attach \
su sudo profile_add profile_remove \
od_create_user od_modify_password od_group_add setuid"

usage() {
    cat <<EOF
Collect macOS Endpoint Security telemetry for SO-CRATES Sigma analysis.

Usage:
    sh scripts/mac-collect-logs.sh [seconds] [output-file]

Defaults: 60 seconds, ./macos-events.ndjson
Set ESLOGGER_EVENTS to change the subscribed events. The default set covers
process execution, file creation, persistence (Background Task Management),
XProtect malware detections, Gatekeeper overrides, TCC changes, kext loads,
remote thread creation, logins and privilege escalation.

Set SOCRATES_KEEP_RAW=1 to also keep eslogger's unconverted output alongside
the result, as <output-file>.raw.ndjson.

$ESLOGGER requires root, so this script prompts for your password once and
elevates that single command. Everything else -- the conversion step, the
output file -- stays unprivileged, and root lasts only as long as the
capture. Nothing is installed and no standing privilege is granted.

SO-CRATES itself never escalates and exposes no endpoint that does: the
server only reads the resulting file, like any uploaded log.

Endpoint Security also requires Full Disk Access for your terminal
(System Settings > Privacy & Security).

When it finishes, drag the .ndjson onto the SO-CRATES welcome screen.
EOF
}

case "${1:-}" in
    -h|--help) usage; exit 0 ;;
esac

DURATION="${1:-60}"
OUTPUT="${2:-macos-events.ndjson}"
EVENTS="${ESLOGGER_EVENTS:-$DEFAULT_EVENTS}"
HERE="$(cd "$(dirname "$0")" && pwd)"

case "$DURATION" in
    ''|*[!0-9]*) echo "Error: duration must be a whole number of seconds" >&2; exit 1 ;;
esac
[ "$DURATION" -lt 1 ] && { echo "Error: duration must be at least 1 second" >&2; exit 1; }

[ -x "$ESLOGGER" ] || {
    echo "Error: $ESLOGGER not found (needs macOS 13 Ventura or later)" >&2
    exit 1
}

AS_ROOT=""
if [ "$(id -u)" -ne 0 ]; then
    command -v sudo >/dev/null 2>&1 || { echo "Error: sudo not found" >&2; exit 1; }
    echo "==> $ESLOGGER requires root. Authenticating once for this capture only."
    sudo -v || { echo "Error: authentication failed; nothing was collected." >&2; exit 1; }
    AS_ROOT="sudo -n"
fi

RAW="$(mktemp -t socrates-eslogger)"
trap 'rm -f "$RAW"' EXIT INT TERM

echo "==> Collecting Endpoint Security events [$EVENTS] for ${DURATION}s..."
echo "    Run the activity you want captured now."

# eslogger is stopped by a timer running on the privileged side: under sudo the
# process is root-owned, so this unprivileged shell could not signal it. The
# redirect stays out here, so RAW is created by the calling user.
# shellcheck disable=SC2086,SC2016
$AS_ROOT /bin/sh -c '
    es=$1; secs=$2; shift 2
    "$es" "$@" &
    espid=$!
    # Forward SIGTERM so an outer-shell trap that kills this wrapper takes
    # the child eslogger down with it; without this the wrapper would exit
    # and leave eslogger orphaned as init.
    trap "kill -TERM $espid 2>/dev/null; wait $espid 2>/dev/null; exit 0" TERM INT
    sleep "$secs" &
    wait $!
    kill -TERM "$espid" 2>/dev/null || true
    wait "$espid" 2>/dev/null || true
' sh "$ESLOGGER" "$DURATION" $EVENTS > "$RAW" 2>/dev/null &
JOBPID=$!

# Retarget the exit trap so Ctrl-C also stops the privileged capture
# instead of leaving it to burn through its remaining seconds.
cleanup() {
    kill -TERM "$JOBPID" 2>/dev/null || true
    wait "$JOBPID" 2>/dev/null || true
    rm -f "$RAW"
}
trap cleanup EXIT INT TERM

ELAPSED=0
while [ "$ELAPSED" -lt "$DURATION" ]; do
    kill -0 "$JOBPID" 2>/dev/null || break
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    LINES=$(wc -l < "$RAW" | tr -d ' ')
    printf '\r    %ss elapsed, %ss left, %s raw events' "$ELAPSED" "$((DURATION - ELAPSED))" "$LINES"
done
printf '\n'

wait "$JOBPID" 2>/dev/null || true

if [ ! -s "$RAW" ]; then
    echo "Error: eslogger produced no events. Grant Full Disk Access to your terminal in" >&2
    echo "       System Settings > Privacy & Security, then re-run." >&2
    exit 1
fi

if [ -n "${SOCRATES_KEEP_RAW:-}" ]; then
    cp "$RAW" "$OUTPUT.raw.ndjson"
    [ -n "${SUDO_USER:-}" ] && chown "$SUDO_USER" "$OUTPUT.raw.ndjson" 2>/dev/null
    echo "==> Kept unconverted eslogger output at $OUTPUT.raw.ndjson"
fi

python3 "$HERE/eslogger_to_sigma.py" < "$RAW" > "$OUTPUT"

if [ -n "${SUDO_USER:-}" ]; then
    chown "$SUDO_USER" "$OUTPUT" 2>/dev/null || true
fi

echo "==> Wrote $OUTPUT ($(wc -l < "$OUTPUT" | tr -d ' ') events)"
echo "    Upload it to SO-CRATES to run the macOS Sigma ruleset against it."
