from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .patching import atomic_write
from .paths import SCRATCHPAD_RELATIVE_PATH

SCRATCHPAD_IGNORE_ENTRY = f"/{SCRATCHPAD_RELATIVE_PATH}"
LEGACY_SCRATCHPAD_IGNORE_ENTRY = "/wiki/scratchpad.md"
SCRATCHPAD_IGNORE_COMMENT = "# Lliki local LLM handover state"


@dataclass(frozen=True)
class GitignoreResult:
    status: str
    path: str = ".gitignore"


def _normalized_lines(text: str) -> list[str]:
    lines = text.splitlines()
    cleaned: list[str] = []
    skip_blank_after_comment = False
    for line in lines:
        stripped = line.strip()
        if stripped == SCRATCHPAD_IGNORE_COMMENT:
            skip_blank_after_comment = False
            continue
        if stripped in {SCRATCHPAD_IGNORE_ENTRY, LEGACY_SCRATCHPAD_IGNORE_ENTRY}:
            skip_blank_after_comment = False
            continue
        if skip_blank_after_comment and stripped == "":
            skip_blank_after_comment = False
            continue
        cleaned.append(line.rstrip())
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return cleaned


def ensure_scratchpad_ignored(root: Path, *, dry_run: bool = False) -> GitignoreResult:
    path = root / ".gitignore"
    if path.exists():
        original = path.read_text(encoding="utf-8")
        stripped_lines = [line.strip() for line in original.splitlines()]
        if (
            stripped_lines.count(SCRATCHPAD_IGNORE_ENTRY) == 1
            and stripped_lines.count(LEGACY_SCRATCHPAD_IGNORE_ENTRY) == 0
            and stripped_lines.count(SCRATCHPAD_IGNORE_COMMENT) == 1
        ):
            return GitignoreResult("preserved")
        lines = _normalized_lines(original)
        if lines:
            lines.extend(["", SCRATCHPAD_IGNORE_COMMENT, SCRATCHPAD_IGNORE_ENTRY])
        else:
            lines.extend([SCRATCHPAD_IGNORE_COMMENT, SCRATCHPAD_IGNORE_ENTRY])
        desired = "\n".join(lines) + "\n"
        if desired == original:
            return GitignoreResult("preserved")
        if not dry_run:
            atomic_write(path, desired)
        return GitignoreResult("updated")

    content = f"{SCRATCHPAD_IGNORE_COMMENT}\n{SCRATCHPAD_IGNORE_ENTRY}\n"
    if not dry_run:
        atomic_write(path, content)
    return GitignoreResult("created")


def has_scratchpad_ignore(root: Path) -> bool:
    path = root / ".gitignore"
    if not path.exists():
        return False
    try:
        return any(line.strip() == SCRATCHPAD_IGNORE_ENTRY for line in path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return False
