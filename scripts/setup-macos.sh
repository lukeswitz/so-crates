#!/bin/sh
# SO-CRATES native macOS setup.
#
# Installs the external CLI tools SO-CRATES shells out to (via Homebrew) and,
# optionally, Zircolite for Sigma log analysis. Mirrors the Dockerfile's apt /
# git steps for the macOS (Homebrew) toolchain. Safe to re-run (idempotent).
#
# Usage:
#   sh scripts/setup-macos.sh            # tools + Zircolite (Sigma support)
#   sh scripts/setup-macos.sh --no-sigma # tools only, skip Zircolite
#
# After it completes:  python3 socrates.py
set -e

ZIRCOLITE_VERSION="v3.7.1"
DATA_DIR="${DATA_DIR:-$HOME/socrates-data}"
INSTALL_SIGMA=1
[ "$1" = "--no-sigma" ] && INSTALL_SIGMA=0

if ! command -v brew >/dev/null 2>&1; then
    echo "Error: Homebrew not found. Install it from https://brew.sh and re-run." >&2
    exit 1
fi

echo "==> Installing required tools via Homebrew (suricata, yara)..."
# suricata ships suricata-update and tcpdump is provided by macOS / brew.
brew install suricata yara

# tshark comes from the wireshark formula or the Wireshark.app GUI bundle.
if ! command -v tshark >/dev/null 2>&1 \
   && [ ! -x "/Applications/Wireshark.app/Contents/MacOS/tshark" ]; then
    echo "==> Installing wireshark for tshark..."
    brew install wireshark
fi

echo "==> Verifying tools are on PATH..."
MISSING=""
for t in suricata suricata-update yara tcpdump; do
    command -v "$t" >/dev/null 2>&1 || MISSING="$MISSING $t"
done
if ! command -v tshark >/dev/null 2>&1 \
   && [ ! -x "/Applications/Wireshark.app/Contents/MacOS/tshark" ]; then
    MISSING="$MISSING tshark"
fi
if [ -n "$MISSING" ]; then
    echo "Error: still missing:$MISSING" >&2
    exit 1
fi
echo "    OK: suricata suricata-update yara tcpdump tshark"

if [ "$INSTALL_SIGMA" -eq 1 ]; then
    ZIRCOLITE_DIR="$DATA_DIR/zircolite"
    ZIRCOLITE_VENV="$DATA_DIR/zircolite-venv"
    mkdir -p "$DATA_DIR"

    if [ ! -f "$ZIRCOLITE_DIR/zircolite.py" ]; then
        echo "==> Cloning Zircolite $ZIRCOLITE_VERSION into $ZIRCOLITE_DIR..."
        git clone --depth 1 --branch "$ZIRCOLITE_VERSION" \
            https://github.com/wagga40/Zircolite.git "$ZIRCOLITE_DIR"
        rm -rf "$ZIRCOLITE_DIR/.git"
    else
        echo "==> Zircolite already present at $ZIRCOLITE_DIR — skipping clone"
    fi

    echo "==> Building Zircolite virtualenv at $ZIRCOLITE_VENV..."
    python3 -m venv "$ZIRCOLITE_VENV"
    "$ZIRCOLITE_VENV/bin/pip" install --quiet --disable-pip-version-check \
        -r "$ZIRCOLITE_DIR/requirements.txt"
    echo "    OK: Zircolite ready (Sigma log analysis enabled)"
else
    echo "==> Skipping Zircolite (Sigma log analysis will be unavailable)"
fi

echo ""
echo "Setup complete. Start SO-CRATES with:"
echo "    python3 socrates.py"
echo "Then open http://localhost:8000/socrates.html"
