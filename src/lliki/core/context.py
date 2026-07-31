from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

_ACTIVE = re.compile(r"^- \*\*Active task:\*\*\s*(.*)$", re.MULTILINE)
_LINK = re.compile(r"\[\[([^\]|#]+)")


def context_routes(root: Path) -> Dict[str, Any]:
    index_path = root / "wiki" / "index.md"
    active_target = None
    active_text = None
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        match = _ACTIVE.search(text)
        if match:
            active_text = match.group(1).strip()
            link = _LINK.search(active_text)
            if link:
                target = link.group(1)
                active_path = root / "wiki" / f"{target}.md"
                if active_path.exists():
                    active_target = active_path.relative_to(root).as_posix()
    return {
        "index": "wiki/index.md" if index_path.exists() else None,
        "active_task": active_target,
        "active_task_text": active_text,
        "dashboard": "wiki/tasks/dashboard.md" if (root / "wiki/tasks/dashboard.md").exists() else None,
        "rules": "wiki/wiki-rules.md" if (root / "wiki/wiki-rules.md").exists() else None,
    }
