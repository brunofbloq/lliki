from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from .paths import (
    DOCS_INDEX_RELATIVE_PATH,
    EXPLORATORY_INDEX_RELATIVE_PATH,
    NOTES_INDEX_RELATIVE_PATH,
    SCRATCHPAD_RELATIVE_PATH,
    TASKS_INDEX_RELATIVE_PATH,
    WIKI_INDEX_RELATIVE_PATH,
    index_name_for,
    scratchpad_path,
)

_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_TASK_FILE = re.compile(r"^- \*\*File:\*\*\s*`([^`]+)`\s*$", re.MULTILINE)
_NO_ACTIVE = re.compile(r"^\s*No active task\.\s*$", re.MULTILINE | re.IGNORECASE)

_CORE_COLLECTIONS = {
    "tasks": TASKS_INDEX_RELATIVE_PATH,
    "docs": DOCS_INDEX_RELATIVE_PATH,
    "exploratory": EXPLORATORY_INDEX_RELATIVE_PATH,
    "notes": NOTES_INDEX_RELATIVE_PATH,
}


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


def discover_collections(root: Path) -> Dict[str, str]:
    """Named folder indexes under wiki/, recursively. Custom folders appear
    automatically."""
    collections: Dict[str, str] = {}
    wiki = root / "wiki"
    if not wiki.is_dir():
        return collections
    for directory in sorted(path for path in wiki.rglob("*") if path.is_dir() and ".backup" not in path.parts):
        name = "/".join(directory.relative_to(wiki).as_posix().split("/"))
        candidate = directory / index_name_for(directory)
        if candidate.exists():
            collections[name] = candidate.relative_to(root).as_posix()
    return collections


def context_routes(root: Path) -> Dict[str, Any]:
    def exists(relative: str) -> "str | None":
        return relative if (root / relative).exists() else None

    mode, active_target = scratchpad_route(root)
    collections = discover_collections(root)
    routes = {
        "mode": mode,
        "entry": exists(WIKI_INDEX_RELATIVE_PATH),
        "scratchpad": exists(SCRATCHPAD_RELATIVE_PATH),
        "active_task": active_target,
        "decisions": exists("wiki/decisions.md"),
        "lessons": exists("wiki/lessons_learned.md"),
        "collections": collections,
    }
    for key in _CORE_COLLECTIONS:
        routes[key] = collections.get(key) or exists(_CORE_COLLECTIONS[key])
    return routes
