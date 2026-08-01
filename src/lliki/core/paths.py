from __future__ import annotations

from pathlib import Path

SCRATCHPAD_RELATIVE_PATH = "wiki/tasks/scratchpad.md"
LEGACY_SCRATCHPAD_RELATIVE_PATH = "wiki/scratchpad.md"


def scratchpad_path(root: Path) -> Path:
    return root / SCRATCHPAD_RELATIVE_PATH


def legacy_scratchpad_path(root: Path) -> Path:
    return root / LEGACY_SCRATCHPAD_RELATIVE_PATH
