from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


def marker_pair(section_id: str, kind: str = "managed") -> tuple[str, str]:
    return (
        f"<!-- lliki:{kind}:start id={section_id} -->",
        f"<!-- lliki:{kind}:end id={section_id} -->",
    )


def extract_section(text: str, section_id: str, kind: str = "managed") -> Optional[str]:
    start, end = marker_pair(section_id, kind)
    start_pos = text.find(start)
    end_pos = text.find(end)
    if start_pos < 0 or end_pos < 0 or end_pos < start_pos:
        return None
    return text[start_pos : end_pos + len(end)]


def replace_section(existing: str, replacement: str, section_id: str, kind: str = "managed") -> Tuple[str, bool]:
    start, end = marker_pair(section_id, kind)
    old_start = existing.find(start)
    old_end = existing.find(end)
    new_section = extract_section(replacement, section_id, kind)
    if new_section is None:
        raise ValueError(f"Template does not contain {kind} section {section_id!r}")
    if old_start < 0 or old_end < 0 or old_end < old_start:
        return existing, False
    old_end += len(end)
    updated = existing[:old_start] + new_section + existing[old_end:]
    return updated, updated != existing


def append_section(existing: str, template: str, section_id: str) -> str:
    section = extract_section(template, section_id)
    if section is None:
        raise ValueError(f"Template does not contain managed section {section_id!r}")
    stripped = existing.rstrip()
    return f"{stripped}\n\n{section}\n" if stripped else f"{section}\n"


def backup_file(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = path.with_name(f"{path.name}.bak.{stamp}")
    backup.write_bytes(path.read_bytes())
    return backup


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.lliki.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    tmp.replace(path)
