from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from .paths import SCRATCHPAD_RELATIVE_PATH, scratchpad_path

_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_TASK_FILE = re.compile(r"^- \*\*File:\*\*\s*`([^`]+)`\s*$", re.MULTILINE)
_NO_ACTIVE = re.compile(r"^\s*No active task\.\s*$", re.MULTILINE | re.IGNORECASE)


def _section_text(text: str, heading: str) -> str | None:
    matches = list(_SECTION.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).strip().lower() != heading.lower():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return None


def scratchpad_route(root: Path) -> tuple[str, str | None]:
    scratchpad = scratchpad_path(root)
    if not scratchpad.exists():
        return "new-work", None
    try:
        text = scratchpad.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return "new-work", None
    task_section = _section_text(text, "Task")
    if not task_section or _NO_ACTIVE.search(task_section):
        return "new-work", None
    match = _TASK_FILE.search(task_section)
    if not match:
        return "new-work", None
    value = match.group(1).strip().replace("\\", "/")
    if not value.startswith("wiki/tasks/") or not value.endswith(".md"):
        return "new-work", None
    task_path = root / value
    if not task_path.exists():
        return "new-work", None
    return "resume", value


def context_routes(root: Path) -> Dict[str, Any]:
    index_path = root / "wiki" / "index.md"
    current_scratchpad_path = scratchpad_path(root)
    mode, active_target = scratchpad_route(root)
    return {
        "mode": mode,
        "scratchpad": SCRATCHPAD_RELATIVE_PATH if current_scratchpad_path.exists() else None,
        "index": "wiki/index.md" if index_path.exists() else None,
        "active_task": active_target,
        "dashboard": "wiki/tasks/dashboard.md" if (root / "wiki/tasks/dashboard.md").exists() else None,
        "rules": "wiki/wiki-rules.md" if (root / "wiki/wiki-rules.md").exists() else None,
    }
