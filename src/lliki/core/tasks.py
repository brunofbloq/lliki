from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SUPPORTED_STATUSES = {
    "active",
    "in-progress",
    "in_progress",
    "blocked",
    "planned",
    "todo",
    "backlog",
    "completed",
    "done",
    "cancelled",
    "canceled",
}
# Non-task files that live in wiki/tasks/.
IGNORED_TASK_FILENAMES = {"scratchpad.md", "resume.md", "dashboard.md", "tasks-index.md"}
TASK_BACKUP_DIRNAME = ".backup"

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class TaskRecord:
    path: Path
    task_id: str
    title: str
    status: str
    priority: str
    updated: str

    @property
    def link(self) -> str:
        return f"[[tasks/{self.path.stem}|{self.task_id} - {self.title}]]"


def parse_frontmatter(path: Path) -> Optional[TaskRecord]:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER.match(text)
    if not match:
        return None
    data: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            data[key.strip()] = value.strip().strip('"').strip("'")
    task_id = data.get("id", path.stem)
    title = data.get("title", path.stem.replace("-", " ").title())
    status = data.get("status", "planned").lower()
    return TaskRecord(
        path=path,
        task_id=task_id,
        title=title,
        status=status,
        priority=data.get("priority", "normal").lower(),
        updated=data.get("updated", ""),
    )


def _is_task_candidate(path: Path) -> bool:
    return (
        path.name not in IGNORED_TASK_FILENAMES
        and not path.name.endswith("-index.md")
        and ".backup" not in path.parts
        and ".bak." not in path.name
    )


def load_tasks(root: Path) -> List[TaskRecord]:
    task_dir = root / "wiki" / "tasks"
    if not task_dir.exists():
        return []
    records: List[TaskRecord] = []
    for path in sorted(task_dir.glob("*.md")):
        if not _is_task_candidate(path):
            continue
        record = parse_frontmatter(path)
        if record:
            records.append(record)
    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    return sorted(records, key=lambda r: (priority_order.get(r.priority, 9), r.task_id))


def active_task_record(root: Path) -> Optional[TaskRecord]:
    """The task referenced by the scratchpad, if any. Never inferred from
    priority or filename."""
    from .context import scratchpad_route

    mode, active_target = scratchpad_route(root)
    if mode != "resume" or not active_target:
        return None
    return parse_frontmatter(root / active_target)


def migrate_task_backups(task_dir: Path, *, dry_run: bool = False) -> list[str]:
    moved: list[str] = []
    if not task_dir.exists():
        return moved
    backup_dir = task_dir / TASK_BACKUP_DIRNAME
    for path in sorted(task_dir.glob("*.md.bak.*")):
        destination = backup_dir / path.name
        moved.append(destination.as_posix())
        if dry_run:
            continue
        backup_dir.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if destination.read_bytes() == path.read_bytes():
                path.unlink()
                continue
            raise FileExistsError(f"Refusing to overwrite existing backup: {destination}")
        path.replace(destination)
    return moved
