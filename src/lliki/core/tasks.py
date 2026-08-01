from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .patching import atomic_write, backup_file, extract_section, replace_section

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
IGNORED_TASK_FILENAMES = {"dashboard.md", "scratchpad.md"}
DASHBOARD_BACKUP_DIRNAME = ".backup"

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


def _section(title: str, tasks: Iterable[TaskRecord], empty: str = "None.") -> list[str]:
    lines = [f"## {title}", ""]
    items = list(tasks)
    if not items:
        lines.extend([f"- {empty}", ""])
    else:
        for task in items:
            suffix = f" - priority: {task.priority}" if task.priority not in {"", "normal"} else ""
            lines.append(f"- {task.link}{suffix}")
        lines.append("")
    return lines


def render_dashboard(tasks: List[TaskRecord]) -> str:
    groups = {
        "Active": [t for t in tasks if t.status in {"active", "in-progress", "in_progress"}],
        "Blocked": [t for t in tasks if t.status == "blocked"],
        "Planned": [t for t in tasks if t.status in {"planned", "todo", "backlog"}],
    }
    lines = [
        "<!-- lliki:generated:start id=task-dashboard -->",
        "# Task Dashboard",
        "",
    ]
    for title, items in groups.items():
        lines.extend(_section(title, items))
    lines.append("<!-- lliki:generated:end id=task-dashboard -->")
    return "\n".join(lines) + "\n"


def _migrate_dashboard_backups(task_dir: Path, *, dry_run: bool = False) -> list[str]:
    moved: list[str] = []
    if not task_dir.exists():
        return moved
    backup_dir = task_dir / DASHBOARD_BACKUP_DIRNAME
    for path in sorted(task_dir.glob("dashboard.md.bak.*")):
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


def refresh_dashboard(root: Path, update_index: bool = False, dry_run: bool = False) -> dict:
    tasks = load_tasks(root)
    task_dir = root / "wiki" / "tasks"
    moved_backups = _migrate_dashboard_backups(task_dir, dry_run=dry_run)
    dashboard_path = task_dir / "dashboard.md"
    rendered = render_dashboard(tasks)
    changed = False
    backup = None
    if dashboard_path.exists():
        existing = dashboard_path.read_text(encoding="utf-8")
        updated, replaced = replace_section(existing, rendered, "task-dashboard", kind="generated")
        if not replaced and extract_section(existing, "task-dashboard", kind="generated") is None:
            updated = rendered
            replaced = updated != existing
        if replaced:
            changed = True
            if not dry_run:
                backup = backup_file(dashboard_path, dashboard_path.parent / DASHBOARD_BACKUP_DIRNAME)
                atomic_write(dashboard_path, updated)
    else:
        changed = True
        if not dry_run:
            atomic_write(dashboard_path, rendered)

    warnings: list[str] = []
    if update_index:
        warnings.append("--update-index is deprecated; wiki/index.md is a stable knowledge map and was not changed.")
    return {
        "task_count": len(tasks),
        "dashboard_changed": changed,
        "index_changed": False,
        "backup": str(backup) if backup else None,
        "moved_backups": moved_backups,
        "warnings": warnings,
    }
