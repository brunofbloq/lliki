from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .core.doctor import run_doctor
from .core.runtime import update_state
from .core.tasks import load_tasks, refresh_dashboard


def _read_input() -> Dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _session_context(root: Path) -> Optional[str]:
    state_path = root / ".lliki" / "state.json"
    if not state_path.exists():
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    parts = []
    if state.get("active_task"):
        parts.append(f"Active task: {state['active_task']}")
    if state.get("last_result"):
        parts.append(f"Last result: {state['last_result']}")
    if state.get("next_action"):
        parts.append(f"Next action: {state['next_action']}")
    blockers = state.get("blockers") or []
    if blockers:
        parts.append("Blockers: " + "; ".join(map(str, blockers)))
    if not parts:
        return None
    return "Lliki resume state (non-authoritative):\n" + "\n".join(f"- {p}" for p in parts)


def run_hook(event: str, root: Optional[Path] = None) -> int:
    root = (root or Path.cwd()).resolve()
    _read_input()  # Consume Claude hook input even when no fields are needed.
    try:
        if event == "claude-session-start":
            context = _session_context(root)
            if context:
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": context[:2000],
                    },
                    "suppressOutput": True,
                }))
        elif event in {"claude-task-completed", "claude-stop"}:
            refresh_dashboard(root, update_index=True, dry_run=False)
            active = [t for t in load_tasks(root) if t.status in {"active", "in-progress", "in_progress"}]
            if len(active) == 1:
                update_state(root, active_task=active[0].task_id)
            run_doctor(root)
        else:
            raise ValueError(f"Unknown hook event: {event}")
    except Exception as exc:  # Hooks must not break the coding session.
        print(f"lliki hook warning: {exc}", file=sys.stderr)
    return 0
