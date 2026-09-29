"""Deterministic folder-index generation.

Every directory under ``wiki/`` owns a named index ``<folder>-index.md``.
Refreshing only rewrites the managed generated region, so manually maintained
content outside the region survives. No LLM is involved.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional

from .patching import atomic_write, backup_file, extract_section, replace_section
from .paths import index_name_for
from .tasks import active_task_record, load_tasks

GENERATED_ID = "folder-index"
TASK_GROUPS = ("Active", "Blocked", "Planned", "Closed")
# Closed tasks remain discoverable by ID, without cluttering the current-work route.
TERMINAL_STATUSES = {"completed", "done", "cancelled", "canceled"}

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def wiki_base(root: Path) -> Path:
    return root / "wiki"


def index_path(folder: Path, wiki: Path) -> Path:
    return folder / ("wiki-index.md" if folder == wiki else index_name_for(folder))


def is_index_file(path: Path) -> bool:
    return path.name.endswith("-index.md")


def iter_wiki_dirs(wiki: Path) -> List[Path]:
    if not wiki.is_dir():
        return []
    sub = [
        path
        for path in wiki.rglob("*")
        if path.is_dir() and ".backup" not in path.parts and not path.name.startswith(".")
    ]
    return [wiki] + sorted(sub)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def frontmatter_value(text: str, key: str) -> Optional[str]:
    match = _FRONTMATTER.match(text)
    if not match:
        return None
    for line in match.group(1).splitlines():
        name, sep, value = line.partition(":")
        if sep and name.strip() == key:
            return value.strip().strip('"').strip("'")
    return None


def _safe_label(text: Optional[str]) -> Optional[str]:
    """Keep aliases from breaking the wikilink syntax."""
    if not text:
        return None
    cleaned = re.sub(r"[\[\]|#]", " ", text).strip()
    return cleaned or None


def document_label(path: Path) -> Optional[str]:
    text = _read_text(path)
    title = frontmatter_value(text, "title")
    if title:
        return _safe_label(title)
    match = _HEADING.search(text)
    return _safe_label(match.group(1) if match else None)


def link_line(target: str, label: Optional[str] = None) -> str:
    if label and label != Path(target).name:
        return f"- [[{target}|{label}]]"
    return f"- [[{target}]]"


def _group_of(status: str) -> str:
    if status in {"active", "in-progress", "in_progress"}:
        return "Active"
    if status == "blocked":
        return "Blocked"
    if status in TERMINAL_STATUSES:
        return "Closed"
    return "Planned"


def _manual_links(existing_text: str) -> set[str]:
    """Wikilink targets present outside the generated region and outside
    fenced code blocks."""
    stripped = re.sub(
        r"<!-- lliki:generated:start id=folder-index -->.*?<!-- lliki:generated:end id=folder-index -->",
        "",
        existing_text,
        flags=re.DOTALL,
    )
    stripped = re.sub(r"^(`{3,}|~{3,}).*?\n.*?\n\1[ \t]*$\n?", "", stripped, flags=re.DOTALL | re.MULTILINE)
    stripped = re.sub(r"`[^`\n]*`", "", stripped)
    return {m.group(1).split("#", 1)[0] for m in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]+)?\]\]", stripped)}


def render_region(root: Path, folder: Path, existing_text: str = "") -> str:
    """Child folder indexes first, then documents. The tasks folder groups task
    documents by status and lists execution state separately. Documents already
    linked manually outside the generated region are not duplicated inside it."""
    wiki = wiki_base(root)
    own = index_path(folder, wiki)
    relative = folder.relative_to(wiki).as_posix()
    prefix = "" if relative == "." else relative + "/"

    lines: List[str] = [f"<!-- lliki:generated:start id={GENERATED_ID} -->", ""]
    children = sorted(
        path
        for path in folder.iterdir()
        if path.is_dir() and ".backup" not in path.parts and not path.name.startswith(".")
    )
    for child in children:
        lines.append(link_line(f"{prefix}{child.name}/{Path(index_name_for(child)).stem}"))
    if children:
        lines.append("")

    if folder == wiki / "tasks":
        tasks = load_tasks(root)
        for group in TASK_GROUPS:
            lines.append(f"## {group}")
            lines.append("")
            grouped = [t for t in tasks if _group_of(t.status) == group]
            if grouped:
                for task in grouped:
                    label = task.task_id if group == "Closed" else f"{task.task_id} - {task.title}"
                    suffix = f" — priority: {task.priority}" if group != "Closed" and task.priority not in {"", "normal"} else ""
                    lines.append(f"{link_line(f'tasks/{task.path.stem}', label)}{suffix}")
            else:
                lines.append("- None.")
            lines.append("")
        lines.append("## Current Task")
        lines.append("")
        task = active_task_record(root)
        lines.append(f"- **Task:** {task.link}" if task else "- None.")
        if (folder / "scratchpad.md").exists():
            lines.append("- **Scratchpad:** [[tasks/scratchpad|Agent Scratchpad]]")
        lines.append("")
    else:
        documents = sorted(
            path for path in folder.glob("*.md") if path != own and ".bak." not in path.name
        )
        already = _manual_links(existing_text)
        for path in documents:
            target_rel = f"{prefix}{path.stem}"
            if target_rel in already or path.stem in already:
                continue  # manually linked already; index stays references-only, no duplicates
            lines.append(link_line(target_rel, document_label(path)))
        if documents:
            lines.append("")

    lines.append(f"<!-- lliki:generated:end id={GENERATED_ID} -->")
    return "\n".join(lines) + "\n"


def region_is_current(root: Path, folder: Path) -> bool:
    target = index_path(folder, wiki_base(root))
    if not target.exists():
        return False
    text = _read_text(target)
    return extract_section(text, GENERATED_ID, kind="generated") == render_region(root, folder, text).strip()


def refresh_folder(root: Path, folder: Path, *, dry_run: bool = False) -> Optional[str]:
    """Ensure and refresh one folder index. Returns 'created'/'refreshed'/None."""
    wiki = wiki_base(root)
    target = index_path(folder, wiki)
    region = render_region(root, folder, _read_text(target))
    if not target.exists():
        if not dry_run:
            name = "Wiki" if folder == wiki else folder.name.replace("-", " ").title()
            atomic_write(target, f"# {name} Index\n\n{region}")
        return "created"
    existing = _read_text(target)
    if extract_section(existing, GENERATED_ID, kind="generated") is None:
        updated = f"{existing.rstrip()}\n\n{region}"
        changed = updated != existing
        if changed and not dry_run:
            # First-time build of the generated region: nothing was replaced,
            # so no backup is warranted.
            atomic_write(target, updated)
        return "refreshed" if changed else None
    updated, changed = replace_section(existing, region, GENERATED_ID, kind="generated")
    if changed:
        if not dry_run:
            backup_dir = target.parent / ".backup" if target.parent.name == "tasks" else None
            backup_file(target, backup_dir)
            atomic_write(target, updated)
        return "refreshed"
    return None


def refresh_indexes(root: Path, folders: Optional[Iterable[str]] = None, *, dry_run: bool = False) -> dict:
    """Refresh named indexes for every wiki folder, or the named folders
    (including their subfolders)."""
    wiki = wiki_base(root)
    if not wiki.is_dir():
        return {"created": [], "refreshed": [], "unchanged": [], "warnings": ["wiki directory not found"]}
    warnings: List[str] = []
    all_dirs = iter_wiki_dirs(wiki)
    if folders:
        selected: List[Path] = []
        for name in folders:
            candidate = wiki if name in {".", "wiki", "wiki-index"} else wiki / name
            if not candidate.is_dir():
                warnings.append(f"Unknown wiki folder: {name}")
                continue
            selected.extend(d for d in all_dirs if d == candidate or candidate in d.parents)
        all_dirs = sorted(set(selected))

    buckets: dict = {"created": [], "refreshed": [], "unchanged": []}
    for directory in all_dirs:
        action = refresh_folder(root, directory, dry_run=dry_run) or "unchanged"
        buckets[action].append(index_path(directory, wiki).relative_to(root).as_posix())
    return {**buckets, "warnings": warnings}
