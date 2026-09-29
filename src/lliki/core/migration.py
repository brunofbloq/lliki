"""Deterministic 0.3 -> 0.4+ layout migration.

Renames legacy index files to their named-index equivalents. The old generated
task dashboard and the standalone resume file are superseded by ``tasks-index.md``
(collection + generated Current Task route), so they are preserved in the
ignored ``.backup`` directory instead of rewritten.
Idempotent: running it twice is a no-op.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from .paths import (
    DOCS_INDEX_RELATIVE_PATH,
    EXPLORATORY_INDEX_RELATIVE_PATH,
    LEGACY_DOCS_INDEX_RELATIVE_PATH,
    LEGACY_EXPLORATORY_INDEX_RELATIVE_PATH,
    LEGACY_WIKI_INDEX_RELATIVE_PATH,
    WIKI_INDEX_RELATIVE_PATH,
)
from .tasks import migrate_task_backups


def _rename(root: Path, old: str, new: str, actions: List[str], *, dry_run: bool) -> None:
    old_path = root / old
    new_path = root / new
    if not old_path.exists() or new_path.exists():
        return
    if not dry_run:
        old_path.replace(new_path)
    actions.append(f"migrated {old} -> {new}")


def _retire(root: Path, path: Path, actions: List[str], *, dry_run: bool) -> None:
    if not path.exists():
        return
    backup = root / "wiki" / "tasks" / ".backup" / path.name
    if not dry_run:
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            path.unlink()
        else:
            path.replace(backup)
    actions.append(f"moved {path.relative_to(root).as_posix()} to wiki/tasks/.backup/ (superseded by tasks-index.md)")


def migrate_legacy_layout(root: Path, *, dry_run: bool = False) -> List[str]:
    actions: List[str] = []
    _rename(root, LEGACY_WIKI_INDEX_RELATIVE_PATH, WIKI_INDEX_RELATIVE_PATH, actions, dry_run=dry_run)
    _rename(root, LEGACY_DOCS_INDEX_RELATIVE_PATH, DOCS_INDEX_RELATIVE_PATH, actions, dry_run=dry_run)
    _rename(root, LEGACY_EXPLORATORY_INDEX_RELATIVE_PATH, EXPLORATORY_INDEX_RELATIVE_PATH, actions, dry_run=dry_run)

    tasks = root / "wiki" / "tasks"
    _retire(root, tasks / "dashboard.md", actions, dry_run=dry_run)
    _retire(root, tasks / "resume.md", actions, dry_run=dry_run)
    moved_backups = migrate_task_backups(tasks, dry_run=dry_run)
    actions.extend(f"moved stray backup {path}" for path in moved_backups)
    return actions
