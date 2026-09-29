"""Notes operations over wiki/notes (list/show/append/search)."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import List, Optional

from .documents import create_document
from .indexing import refresh_folder
from .patching import atomic_write

NOTES_DIR = "wiki/notes"

_TITLE = re.compile(r"^title:\s*\"?(.*?)\"?\s*$", re.MULTILINE)


def notes_dir(root: Path) -> Path:
    path = root / NOTES_DIR
    if not path.is_dir():
        raise FileNotFoundError(f"Missing {NOTES_DIR} (run lliki init/update first)")
    return path


def list_notes(root: Path) -> List[dict]:
    entries = []
    for path in notes_dir(root).glob("*.md"):
        if path.name.endswith("-index.md") or ".bak." in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        match = _TITLE.search(text)
        entries.append({
            "path": path.relative_to(root).as_posix(),
            "name": path.stem,
            "title": match.group(1) if match else path.stem,
            "date": path.stem.split("-")[0] if re.match(r"\d{4}-", path.stem) else "",
        })
    return sorted(entries, key=lambda e: e["name"], reverse=True)


def _find_note(root: Path, query: str) -> Path:
    directory = notes_dir(root)
    exact = directory / f"{query}.md"
    if exact.exists():
        return exact
    matches = sorted(path for path in directory.glob(f"*{query}*.md") if not path.name.endswith("-index.md"))
    if not matches:
        raise FileNotFoundError(f"No note matching: {query}")
    if len(matches) > 1:
        names = ", ".join(path.stem for path in matches)
        raise ValueError(f"Ambiguous note '{query}'; matches: {names}")
    return matches[0]


def show_note(root: Path, query: str) -> str:
    return _find_note(root, query).read_text(encoding="utf-8")


def append_to_note(root: Path, query: str, content: str, *, heading: Optional[str] = None) -> str:
    path = _find_note(root, query)
    content = content.strip()
    existing = path.read_text(encoding="utf-8").rstrip()
    if heading:
        section = f"\n\n## {heading.strip()}\n\n{content}\n"
        if f"## {heading.strip()}" not in existing:
            new_text = existing + section
        else:
            new_text = existing + f"\n\n{content}\n"
    else:
        if content.startswith("#"):
            new_text = existing + "\n\n" + content + "\n"
        else:
            new_text = existing + "\n\n- " + content.replace("\n", "\n- ") + "\n"
    # keep front matter updated date current
    new_text = re.sub(r"^updated: .*$", f'updated: "{date.today().isoformat()}"', new_text, count=1, flags=re.M)
    atomic_write(path, new_text)
    refresh_folder(root, path.parent)
    return path.relative_to(root).as_posix()


def search_notes(root: Path, term: str) -> List[dict]:
    lowered = term.lower()
    results: List[dict] = []
    for path in sorted(notes_dir(root).glob("*.md")):
        if path.name.endswith("-index.md"):
            continue
        name_hit = lowered in path.stem.lower()
        lines = [
            f"{number}: {line.strip()}"
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if lowered in line.lower()
        ]
        if name_hit or lines:
            results.append({"path": path.relative_to(root).as_posix(), "matches": lines[:10]})
    return results


def new_note(root: Path, title: str, tags: Optional[list[str]] = None, dry_run: bool = False) -> dict:
    return create_document(root, "note", title, tags=tags, dry_run=dry_run)
