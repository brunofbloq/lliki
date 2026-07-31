#!/usr/bin/env sh
set -eu

SOURCE=${1:-.}
PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.9 or newer is required." >&2
  exit 1
fi

if ! "$PYTHON" -m pipx --version >/dev/null 2>&1; then
  "$PYTHON" -m pip install --user pipx
  "$PYTHON" -m pipx ensurepath
fi

"$PYTHON" -m pipx install "$SOURCE"
echo "Installed. Restart your shell if 'lliki' is not yet on PATH."
