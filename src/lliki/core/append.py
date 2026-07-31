from __future__ import annotations

from pathlib import Path

from .patching import atomic_write

TARGETS = {
    "decision": "wiki/decisions.md",
    "lesson": "wiki/lessons_learned.md",
}


def append_entry(root: Path, kind: str, content: str) -> str:
    if kind not in TARGETS:
        raise ValueError(f"Unsupported append kind: {kind}")
    target = root / TARGETS[kind]
    if not target.exists():
        raise FileNotFoundError(f"Missing target file: {TARGETS[kind]}")
    content = content.strip()
    if not content.startswith("## "):
        raise ValueError("Entry must begin with a level-2 Markdown heading ('## ')")
    existing = target.read_text(encoding="utf-8").rstrip()
    atomic_write(target, f"{existing}\n\n{content}\n")
    return TARGETS[kind]
