from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from .resources import load_template_pack

_WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _resolve_wiki_link(root: Path, source: Path, target: str) -> bool:
    target = target.strip()
    if not target:
        return True
    candidates: list[Path] = []
    if target.startswith("wiki/"):
        candidates.append(root / f"{target}.md")
        candidates.append(root / target)
    else:
        candidates.append(source.parent / f"{target}.md")
        candidates.append(source.parent / target)
        candidates.append(root / "wiki" / f"{target}.md")
        candidates.append(root / "wiki" / target)
    return any(candidate.exists() for candidate in candidates)


def run_doctor(root: Path) -> Dict[str, Any]:
    pack = load_template_pack()
    issues: List[Dict[str, str]] = []
    for directory in pack.directories:
        if not (root / directory).is_dir():
            issues.append({"severity": "error", "code": "missing-directory", "path": directory})
    for item in pack.files:
        path = root / item.target
        if not path.exists():
            issues.append({"severity": "error", "code": "missing-file", "path": item.target})
            continue
        if item.needs_context:
            text = path.read_text(encoding="utf-8")
            if "NEEDS_CONTEXT: LLM_OR_HUMAN" in text or "Needs validation" in text:
                issues.append({"severity": "warning", "code": "needs-context", "path": item.target})

    wiki = root / "wiki"
    if wiki.exists():
        for path in wiki.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                issues.append({"severity": "warning", "code": "non-utf8", "path": path.relative_to(root).as_posix()})
                continue
            visible_text = _HTML_COMMENT.sub("", text)
            for match in _WIKI_LINK.finditer(visible_text):
                target = match.group(1)
                if not _resolve_wiki_link(root, path, target):
                    issues.append({
                        "severity": "warning",
                        "code": "broken-wiki-link",
                        "path": path.relative_to(root).as_posix(),
                        "detail": target,
                    })
    return {
        "root": str(root),
        "ok": not any(issue["severity"] == "error" for issue in issues),
        "issues": issues,
        "summary": {
            "errors": sum(1 for issue in issues if issue["severity"] == "error"),
            "warnings": sum(1 for issue in issues if issue["severity"] == "warning"),
        },
    }
