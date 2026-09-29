from __future__ import annotations

from pathlib import Path

SCRATCHPAD_RELATIVE_PATH = "wiki/tasks/scratchpad.md"
LEGACY_SCRATCHPAD_RELATIVE_PATH = "wiki/scratchpad.md"
WIKI_INDEX_RELATIVE_PATH = "wiki/wiki-index.md"
LEGACY_WIKI_INDEX_RELATIVE_PATH = "wiki/index.md"
TASKS_INDEX_RELATIVE_PATH = "wiki/tasks/tasks-index.md"
LEGACY_RESUME_RELATIVE_PATH = "wiki/tasks/resume.md"
LEGACY_DASHBOARD_RELATIVE_PATH = "wiki/tasks/dashboard.md"
DOCS_INDEX_RELATIVE_PATH = "wiki/docs/docs-index.md"
LEGACY_DOCS_INDEX_RELATIVE_PATH = "wiki/docs/README.md"
EXPLORATORY_INDEX_RELATIVE_PATH = "wiki/exploratory/exploratory-index.md"
LEGACY_EXPLORATORY_INDEX_RELATIVE_PATH = "wiki/exploratory/index.md"
NOTES_INDEX_RELATIVE_PATH = "wiki/notes/notes-index.md"

# Legacy path -> current replacement path (doctor WIKI004, migrations).
LEGACY_PATHS = {
    LEGACY_WIKI_INDEX_RELATIVE_PATH: WIKI_INDEX_RELATIVE_PATH,
    LEGACY_DASHBOARD_RELATIVE_PATH: TASKS_INDEX_RELATIVE_PATH,
    LEGACY_RESUME_RELATIVE_PATH: TASKS_INDEX_RELATIVE_PATH,
    LEGACY_DOCS_INDEX_RELATIVE_PATH: DOCS_INDEX_RELATIVE_PATH,
    LEGACY_EXPLORATORY_INDEX_RELATIVE_PATH: EXPLORATORY_INDEX_RELATIVE_PATH,
}


def scratchpad_path(root: Path) -> Path:
    return root / SCRATCHPAD_RELATIVE_PATH


def legacy_scratchpad_path(root: Path) -> Path:
    return root / LEGACY_SCRATCHPAD_RELATIVE_PATH


def index_name_for(folder: Path) -> str:
    return f"{folder.name}-index.md"


def index_path_for(folder: Path) -> Path:
    return folder / index_name_for(folder)
