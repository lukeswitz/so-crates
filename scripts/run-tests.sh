#!/bin/sh
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$REPO_DIR/.venv"

if ! "$VENV/bin/python" -c "import playwright" >/dev/null 2>&1; then
    echo "==> Installing test dependencies into $VENV..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet --disable-pip-version-check \
        -r "$REPO_DIR/requirements-screenshots.txt"
fi

cd "$REPO_DIR"
exec "$VENV/bin/python" -m unittest discover "$@"
