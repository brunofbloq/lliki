from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .bootstrap import apply_template_pack
from .doctor import run_doctor
from .gitignore import ensure_scratchpad_ignored
from .inspection import find_legacy_locations, repository_signals
from .paths import LEGACY_SCRATCHPAD_RELATIVE_PATH, SCRATCHPAD_RELATIVE_PATH, legacy_scratchpad_path
from .prompts import format_prompt, load_prompts
from .tasks import refresh_dashboard

_LEGACY_INDEX_SECTIONS = (
    "## Project Snapshot",
    "## Active Route",
    "## Current Priorities",
    "## Project-Level Blockers",
    "## Recent Significant Changes",
)


def _legacy_index_sections(root: Path) -> list[str]:
    path = root / "wiki" / "index.md"
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return [section for section in _LEGACY_INDEX_SECTIONS if section in text]


def run_update(root: Path, *, dry_run: bool = False, max_depth: int = 6) -> Dict[str, Any]:
    root = root.resolve()
    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)

    inspection = find_legacy_locations(root, max_depth=max_depth)
    signals = repository_signals(root)
    legacy_index_sections = _legacy_index_sections(root)

    result = apply_template_pack(
        root,
        interactive=False,
        yes=True,
        dry_run=dry_run,
    )

    gitignore = ensure_scratchpad_ignored(root, dry_run=dry_run)
    if gitignore.status == "created":
        result.created.append(gitignore.path)
    elif gitignore.status == "updated":
        result.updated.append(gitignore.path)
    else:
        result.preserved.append(gitignore.path)

    dashboard = refresh_dashboard(root, update_index=False, dry_run=dry_run)
    doctor = run_doctor(root)

    warnings: list[str] = list(result.warnings)
    if inspection["legacy_dirs"]:
        warnings.append("Legacy local context/state was detected; new Lliki versions do not use .lliki or legacy context directories.")
    if legacy_scratchpad_path(root).exists():
        warnings.append(
            f"Legacy {LEGACY_SCRATCHPAD_RELATIVE_PATH} was detected and left untouched; "
            f"manually migrate useful handover notes into {SCRATCHPAD_RELATIVE_PATH}."
        )
    if legacy_index_sections:
        warnings.append("Legacy mutable wiki/index.md sections were detected and were not rewritten automatically.")
    if any(issue["code"] == "scratchpad-tracked" for issue in doctor["issues"]):
        warnings.append(f"{SCRATCHPAD_RELATIVE_PATH} appears to be tracked; Lliki will not untrack it automatically.")

    semantic_migration_needed = bool(inspection["legacy_dirs"] or legacy_index_sections)
    migration_prompt = format_prompt(load_prompts()["migrate-legacy"]) if semantic_migration_needed else None

    return {
        "root": str(root),
        "dry_run": dry_run,
        "inspection": inspection,
        "signals": signals,
        "actions": {
            "created": result.created,
            "updated": result.updated,
            "preserved": result.preserved,
            "backups": result.backups,
        },
        "dashboard": dashboard,
        "doctor": doctor,
        "warnings": warnings,
        "legacy_index_sections": legacy_index_sections,
        "semantic_migration_needed": semantic_migration_needed,
        "migration_prompt": migration_prompt,
    }
