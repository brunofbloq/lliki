from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .patching import atomic_write


def runtime_dir(root: Path) -> Path:
    return root / ".lliki"


def write_runtime_config(root: Path, mode: str, integrations: list[str], scratchpad: bool, hooks: bool) -> list[str]:
    base = runtime_dir(root)
    base.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    config = {
        "schema_version": 1,
        "runtime_mode": mode,
        "integrations": integrations,
        "scratchpad": scratchpad,
        "automatic_maintenance": hooks,
    }
    config_path = base / "config.json"
    atomic_write(config_path, json.dumps(config, indent=2) + "\n")
    created.append(config_path.relative_to(root).as_posix())
    state_path = base / "state.json"
    if not state_path.exists():
        state = {
            "active_task": None,
            "last_result": None,
            "next_action": None,
            "blockers": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        atomic_write(state_path, json.dumps(state, indent=2) + "\n")
        created.append(state_path.relative_to(root).as_posix())
    if scratchpad:
        scratch = base / "scratchpad.md"
        if not scratch.exists():
            atomic_write(scratch, "# Optional Debug Scratchpad\n\n")
            created.append(scratch.relative_to(root).as_posix())
        logs = base / "logs"
        logs.mkdir(exist_ok=True)
        created.append(logs.relative_to(root).as_posix() + "/")
    return created


def read_runtime_config(root: Path) -> Dict[str, Any]:
    path = runtime_dir(root) / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def update_state(root: Path, **changes: Any) -> None:
    path = runtime_dir(root) / "state.json"
    if not path.exists():
        return
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        state = {}
    state.update(changes)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write(path, json.dumps(state, indent=2) + "\n")


def ensure_gitignore(root: Path) -> bool:
    path = root / ".gitignore"
    entry = "/.lliki/"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if any(line.strip() == entry for line in text.splitlines()):
            return False
        content = text.rstrip() + f"\n\n# Local lliki runtime state\n{entry}\n"
    else:
        content = f"# Local lliki runtime state\n{entry}\n"
    atomic_write(path, content)
    return True


def read_state(root: Path) -> Dict[str, Any]:
    path = runtime_dir(root) / "state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def set_state_fields(
    root: Path,
    active_task: Any = None,
    last_result: Any = None,
    next_action: Any = None,
    blockers: Any = None,
    clear: bool = False,
) -> Dict[str, Any]:
    path = runtime_dir(root) / "state.json"
    if not path.exists():
        raise FileNotFoundError("Runtime state is not enabled for this repository")
    state = {} if clear else read_state(root)
    if active_task is not None:
        state["active_task"] = active_task
    if last_result is not None:
        state["last_result"] = last_result
    if next_action is not None:
        state["next_action"] = next_action
    if blockers is not None:
        state["blockers"] = blockers
    state.setdefault("active_task", None)
    state.setdefault("last_result", None)
    state.setdefault("next_action", None)
    state.setdefault("blockers", [])
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_write(path, json.dumps(state, indent=2) + "\n")
    return state
