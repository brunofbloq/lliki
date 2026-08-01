from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .core.context import scratchpad_route
from .core.doctor import run_doctor
from .core.paths import scratchpad_path
from .core.tasks import refresh_dashboard


def _read_input() -> Dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _session_context(root: Path) -> Optional[str]:
    mode, active_task = scratchpad_route(root)
    path = scratchpad_path(root)
    if mode != "resume" or not active_task or not path.exists():
        return None
    try:
        scratchpad = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    return (
        "Lliki scratchpad handover (local, non-authoritative):\n"
        f"- Active task: {active_task}\n\n"
        + scratchpad.strip()
    )


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
            refresh_dashboard(root, update_index=False, dry_run=False)
            run_doctor(root)
        else:
            raise ValueError(f"Unknown hook event: {event}")
    except Exception as exc:  # Hooks must not break the coding session.
        print(f"lliki hook warning: {exc}", file=sys.stderr)
    return 0
