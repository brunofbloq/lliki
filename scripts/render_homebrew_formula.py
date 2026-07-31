#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--template", default="packaging/homebrew/Formula/lliki.rb.in")
    parser.add_argument("--output", default="dist/lliki.rb")
    args = parser.parse_args()
    text = Path(args.template).read_text(encoding="utf-8")
    text = text.replace("@URL@", args.url).replace("@SHA256@", args.sha256)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
