from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from lliki.core.patching import append_section, atomic_write, backup_file, replace_section
from lliki.core.resources import read_template


def _install_managed_file(root: Path, target: str, template_name: str, section_id: str) -> Tuple[str, Optional[str]]:
    path = root / target
    template = read_template(template_name)
    if not path.exists():
        atomic_write(path, template)
        return "created", None
    existing = path.read_text(encoding="utf-8")
    updated, changed = replace_section(existing, template, section_id)
    if changed:
        backup = backup_file(path)
        atomic_write(path, updated)
        return "updated", str(backup.relative_to(root))
    if f"id={section_id}" not in existing:
        backup = backup_file(path)
        atomic_write(path, append_section(existing, template, section_id))
        return "updated", str(backup.relative_to(root))
    return "preserved", None


def install_generic(root: Path) -> dict:
    status, backup = _install_managed_file(
        root, "AGENTS.md", "integrations/generic/AGENTS.md", "generic-agent-contract"
    )
    return {"integration": "generic", "status": status, "backup": backup, "files": ["AGENTS.md"]}


def _merge_hook(settings: Dict[str, Any], event: str, command: str) -> None:
    hooks = settings.setdefault("hooks", {})
    entries = hooks.setdefault(event, [])
    handler = {"type": "command", "command": command, "timeout": 10}
    group = {"matcher": "", "hooks": [handler]}
    for existing in entries:
        for existing_handler in existing.get("hooks", []):
            if existing_handler.get("type") == "command" and existing_handler.get("command") == command:
                return
    entries.append(group)


def install_claude(root: Path, hooks_enabled: bool = False) -> dict:
    files: List[str] = []
    backups: List[str] = []
    skill_target = ".claude/skills/lliki/SKILL.md"
    status, backup = _install_managed_file(
        root,
        skill_target,
        "integrations/claude/SKILL.md",
        "claude-lliki-skill",
    )
    files.append(skill_target)
    if backup:
        backups.append(backup)

    if hooks_enabled:
        settings_path = root / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        if settings_path.exists():
            try:
                settings = json.loads(settings_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Cannot merge Claude hooks: {settings_path} is invalid JSON: {exc}") from exc
            backup_path = backup_file(settings_path)
            backups.append(str(backup_path.relative_to(root)))
        else:
            settings = {}
        _merge_hook(settings, "SessionStart", "lliki hook claude-session-start")
        _merge_hook(settings, "TaskCompleted", "lliki hook claude-task-completed")
        _merge_hook(settings, "Stop", "lliki hook claude-stop")
        atomic_write(settings_path, json.dumps(settings, indent=2) + "\n")
        files.append(".claude/settings.json")
    return {"integration": "claude", "status": status, "backups": backups, "files": files}


def install_hermes(root: Path) -> dict:
    status, backup = _install_managed_file(
        root, ".hermes.md", "integrations/hermes/HERMES.md", "hermes-agent-contract"
    )
    return {"integration": "hermes", "status": status, "backup": backup, "files": [".hermes.md"]}


def install_selected(root: Path, selected: Iterable[str], claude_hooks: bool = False) -> list[dict]:
    results: list[dict] = []
    for name in selected:
        if name == "generic":
            results.append(install_generic(root))
        elif name == "claude":
            results.append(install_claude(root, hooks_enabled=claude_hooks))
        elif name == "hermes":
            results.append(install_hermes(root))
        else:
            raise ValueError(f"Unknown integration: {name}")
    return results
