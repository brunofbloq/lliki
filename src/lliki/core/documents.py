"""Shared document factory for lliki task/notes/explore creation commands.

Deterministic: slug, dates, front matter, template rendering, safe creation,
parent folder index refresh. No LLM.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Optional

from .indexing import refresh_folder
from .patching import atomic_write
from .resources import read_template
from .tasks import load_tasks

KINDS = {
    "task": {"folder": "tasks", "template": "content/task.md"},
    "note": {"folder": "notes", "template": "content/note.md"},
    "exploratory": {"folder": "exploratory", "template": "content/exploratory.md"},
}

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    slug = _SLUG_STRIP.sub("-", title.lower()).strip("-")
    if not slug:
        raise ValueError(f"Title produces an empty slug: {title!r}")
    return slug


def next_task_id(root: Path, prefix: str = "LLIKI") -> str:
    numbers = []
    for task in load_tasks(root):
        match = re.match(rf"{prefix}-(\d+)", task.task_id)
        if match:
            numbers.append(int(match.group(1)))
    return f"{prefix}-{(max(numbers) + 1) if numbers else 1:03d}"


def create_document(
    root: Path,
    kind: str,
    title: str,
    *,
    tags: Optional[list[str]] = None,
    doc_id: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    if kind not in KINDS:
        raise ValueError(f"Unknown document kind: {kind}")
    spec = KINDS[kind]
    folder = root / "wiki" / spec["folder"]
    if not folder.is_dir():
        raise FileNotFoundError(f"Missing wiki folder: wiki/{spec['folder']} (run lliki init/update first)")
    today = date.today().isoformat()
    if kind == "note":
        stem = f"{today}-{slugify(title)}"
    elif kind == "task":
        stem = f"{doc_id or next_task_id(root)}-{slugify(title)}"
        doc_id = doc_id or next_task_id(root)
    else:
        stem = slugify(title)
    target = folder / f"{stem}.md"
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing document: {target.relative_to(root)}")

    template = read_template(spec["template"])
    content = template.format(
        id=doc_id or stem,
        kind=kind,
        title=title.replace('"', "'"),
        created=today,
        updated=today,
        tags=", ".join(f'"{tag}"' for tag in (tags or [])),
    )
    if not dry_run:
        atomic_write(target, content)
        refresh_folder(root, folder)
    return {
        "path": target.relative_to(root).as_posix(),
        "id": doc_id or stem,
        "index_refreshed": spec["folder"],
        "dry_run": dry_run,
    }
