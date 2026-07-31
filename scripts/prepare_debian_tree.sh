#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
rm -rf "$ROOT/debian"
cp -R "$ROOT/packaging/debian" "$ROOT/debian"
echo "Prepared $ROOT/debian. Build with: dpkg-buildpackage -us -uc -b"
