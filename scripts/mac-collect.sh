#!/usr/bin/env bash
set -euo pipefail

STAGE="${STAGE:-$HOME/socrates_stage}"
DURATION="${DURATION:-60}"

physical_iface() {
  local i ip
  for i in $(ifconfig -lu); do
    case "$i" in lo*|utun*|gif*|stf*|awdl*|llw*|bridge*|ap*|vmenet*) continue ;; esac
    ip="$(ipconfig getifaddr "$i" 2>/dev/null || true)"
    [ -n "$ip" ] && { printf '%s\n' "$i"; return 0; }
  done
  printf 'en0\n'
}

prepare() {
  rm -rf "$STAGE"
  mkdir -p "$STAGE"/{pcap,yara}
}

collect_pcap() {
  local iface f count
  iface="${IFACE:-$(physical_iface)}"
  f="$STAGE/pcap/capture.pcap"
  echo "[pcap] ${DURATION}s on ${iface}"
  sudo tcpdump -i "$iface" -G "$DURATION" -W 1 -w "$f" >/dev/null 2>&1 || true
  if [ -s "$f" ]; then
    sudo chown "$(id -un)" "$f"
  fi
  count="$(tcpdump -r "$f" 2>/dev/null | wc -l | tr -d ' ')"
  echo "[pcap] ${count:-0} packets"
  if [ "${count:-0}" -eq 0 ]; then
    echo "[pcap] empty capture; check interface or generate traffic" >&2
  fi
}

stage_yara() {
  local src
  if [ "$#" -eq 0 ]; then
    echo "[yara] no files passed; skipping"
    return 0
  fi
  for src in "$@"; do
    if [ -f "$src" ]; then
      cp "$src" "$STAGE/yara/"
      echo "[yara] staged $(basename "$src")"
    else
      echo "[yara] not a file: $src" >&2
    fi
  done
}

report() {
  echo "staged: $STAGE"
  find "$STAGE" -type f -exec ls -lh {} +
}

main() {
  prepare
  collect_pcap
  stage_yara "$@"
  report
}

main "$@"
