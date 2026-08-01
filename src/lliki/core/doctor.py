from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .gitignore import has_scratchpad_ignore
from .paths import (
    LEGACY_SCRATCHPAD_RELATIVE_PATH,
    SCRATCHPAD_RELATIVE_PATH,
    legacy_scratchpad_path,
    scratchpad_path,
)
from .resources import load_template_pack
from .tasks import IGNORED_TASK_FILENAMES, SUPPORTED_STATUSES, load_tasks, render_dashboard

_WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_MANAGED_MARKER = re.compile(r"<!--\s*lliki:(?:managed|generated):(?:start|end)\s+id=([^ ]+)\s*-->")
_REQUIRED_SCRATCHPAD_HEADINGS = (
    "## Task",
    "## Current Checkpoint",
    "## Confirmed Outcomes",
    "## Debug Experiments",
    "## Active Blockers",
    "## Focus",
    "## Remaining Validation",
    "## Next Action",
    "## Snapshot",
)
_LEGACY_INDEX_SECTIONS = (
    "## Project Snapshot",
    "## Active Route",
    "## Current Priorities",
    "## Project-Level Blockers",
    "## Recent Significant Changes",
)
_INDEX_LINKS = (
    "docs/project-overview",
    "docs/development-workflow",
    "docs/repository-rules",
    "docs/README",
    "tasks/dashboard",
    "exploratory/index",
    "decisions",
    "lessons_learned",
    "wiki-rules",
)
_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_NO_ACTIVE = re.compile(r"^\s*No active task\.\s*$", re.MULTILINE | re.IGNORECASE)


def _section_text(text: str, heading: str) -> str | None:
    matches = list(_SECTION.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).strip().lower() != heading.lower():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return None


def _scratchpad_is_inactive(text: str) -> bool:
    task_section = _section_text(text, "Task")
    return not task_section or bool(_NO_ACTIVE.search(task_section))


def _bullet_count(section: str | None) -> int:
    if not section:
        return 0
    return sum(1 for line in section.splitlines() if line.strip().startswith("- "))


def _issue(severity: str, code: str, path: str, detail: str | None = None) -> Dict[str, str]:
    item = {"severity": severity, "code": code, "path": path}
    if detail:
        item["detail"] = detail
    return item


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


def _is_tracked(root: Path, relative_path: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative_path],
            cwd=str(root),
            text=True,
            capture_output=True,
            check=False,
        )
    except (OSError, ValueError):
        return False
    return result.returncode == 0


def _frontmatter_data(path: Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER.match(text)
    if not match:
        return None
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def _linked_targets(text: str) -> set[str]:
    return {match.group(1).split("#", 1)[0] for match in _WIKI_LINK.finditer(_HTML_COMMENT.sub("", text))}


def run_doctor(root: Path) -> Dict[str, Any]:
    pack = load_template_pack()
    issues: List[Dict[str, str]] = []
    for directory in pack.directories:
        if not (root / directory).is_dir():
            issues.append(_issue("error", "missing-directory", directory))
    for item in pack.files:
        path = root / item.target
        if not path.exists():
            severity = "warning" if item.target == SCRATCHPAD_RELATIVE_PATH else "error"
            issues.append(_issue(severity, "missing-file", item.target))
            continue
        if item.needs_context:
            text = path.read_text(encoding="utf-8")
            if "NEEDS_CONTEXT: LLM_OR_HUMAN" in text or "Needs validation" in text:
                issues.append(_issue("warning", "needs-context", item.target))

    scratchpad = scratchpad_path(root)
    if not scratchpad.exists():
        issues.append(_issue("warning", "missing-scratchpad", SCRATCHPAD_RELATIVE_PATH))
    else:
        try:
            scratchpad_text = scratchpad.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            issues.append(_issue("warning", "non-utf8", SCRATCHPAD_RELATIVE_PATH))
            scratchpad_text = ""
        for heading in _REQUIRED_SCRATCHPAD_HEADINGS:
            if heading not in scratchpad_text:
                issues.append(_issue("warning", "scratchpad-missing-section", SCRATCHPAD_RELATIVE_PATH, heading))
        if scratchpad.stat().st_size > 8192:
            issues.append(_issue("warning", "scratchpad-oversized", SCRATCHPAD_RELATIVE_PATH, str(scratchpad.stat().st_size)))
        task_refs = sorted({
            ref
            for ref in re.findall(r"wiki/tasks/[A-Za-z0-9_.-]+\.md", scratchpad_text)
            if Path(ref).name not in IGNORED_TASK_FILENAMES
        })
        if len(task_refs) > 1:
            issues.append(_issue("warning", "scratchpad-multiple-tasks", SCRATCHPAD_RELATIVE_PATH, ", ".join(task_refs)))
        inactive = _scratchpad_is_inactive(scratchpad_text)
        if not inactive and not task_refs:
            issues.append(_issue("warning", "scratchpad-missing-task-reference", SCRATCHPAD_RELATIVE_PATH))
        next_action = _section_text(scratchpad_text, "Next Action")
        if not inactive and (not next_action or next_action.strip().lower() in {"none.", "none", "- none.", "- none"}):
            issues.append(_issue("warning", "scratchpad-missing-next-action", SCRATCHPAD_RELATIVE_PATH))
        if _bullet_count(_section_text(scratchpad_text, "Confirmed Outcomes")) > 5:
            issues.append(_issue("warning", "scratchpad-too-many-findings", SCRATCHPAD_RELATIVE_PATH))
        if _bullet_count(_section_text(scratchpad_text, "Active Blockers")) > 3:
            issues.append(_issue("warning", "scratchpad-too-many-blockers", SCRATCHPAD_RELATIVE_PATH))
        if _bullet_count(_section_text(scratchpad_text, "Focus")) > 8:
            issues.append(_issue("warning", "scratchpad-too-many-focus-paths", SCRATCHPAD_RELATIVE_PATH))
        if len(re.findall(r"^###\s+", _section_text(scratchpad_text, "Debug Experiments") or "", re.MULTILINE)) > 5:
            issues.append(_issue("warning", "scratchpad-too-many-experiments", SCRATCHPAD_RELATIVE_PATH))
        if _is_tracked(root, SCRATCHPAD_RELATIVE_PATH):
            issues.append(_issue("warning", "scratchpad-tracked", SCRATCHPAD_RELATIVE_PATH))
    if not has_scratchpad_ignore(root):
        issues.append(_issue("warning", "scratchpad-not-ignored", ".gitignore"))
    if legacy_scratchpad_path(root).exists():
        issues.append(_issue("warning", "legacy-scratchpad-present", LEGACY_SCRATCHPAD_RELATIVE_PATH))

    if (root / ".lliki").exists():
        issues.append(_issue("warning", "legacy-lliki-directory", ".lliki"))

    wiki = root / "wiki"
    if wiki.exists():
        link_sources: dict[str, set[str]] = {}
        for path in wiki.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                issues.append(_issue("warning", "non-utf8", path.relative_to(root).as_posix()))
                continue
            relative = path.relative_to(root).as_posix()
            if ".lliki/state.json" in text or ".lliki/scratchpad.md" in text:
                issues.append(_issue("warning", "legacy-runtime-reference", relative))
            marker_ids = _MANAGED_MARKER.findall(text)
            for marker_id in sorted({item for item in marker_ids if marker_ids.count(item) > 2}):
                issues.append(_issue("warning", "duplicate-managed-marker", relative, marker_id))
            visible_text = _HTML_COMMENT.sub("", text)
            link_sources[relative] = _linked_targets(text)
            for match in _WIKI_LINK.finditer(visible_text):
                target = match.group(1)
                if not _resolve_wiki_link(root, path, target):
                    issues.append(_issue("warning", "broken-wiki-link", relative, target))

        index = root / "wiki" / "index.md"
        if index.exists():
            index_text = index.read_text(encoding="utf-8")
            for section in _LEGACY_INDEX_SECTIONS:
                if section in index_text:
                    issues.append(_issue("warning", "legacy-mutable-index-section", "wiki/index.md", section))
            links = _linked_targets(index_text)
            for target in _INDEX_LINKS:
                if target not in links:
                    issues.append(_issue("warning", "knowledge-map-missing-link", "wiki/index.md", target))

        tasks_dir = root / "wiki" / "tasks"
        if tasks_dir.exists():
            seen_ids: dict[str, str] = {}
            for path in sorted(tasks_dir.glob("*.md")):
                if path.name in IGNORED_TASK_FILENAMES:
                    continue
                relative = path.relative_to(root).as_posix()
                try:
                    data = _frontmatter_data(path)
                except UnicodeDecodeError:
                    continue
                if data is None:
                    continue
                for key in ("id", "title", "status"):
                    if not data.get(key):
                        issues.append(_issue("warning", "task-missing-metadata", relative, key))
                task_id = data.get("id") or path.stem
                if task_id in seen_ids:
                    issues.append(_issue("warning", "duplicate-task-id", relative, f"{task_id} also in {seen_ids[task_id]}"))
                else:
                    seen_ids[task_id] = relative
                status = (data.get("status") or "").lower()
                if status and status not in SUPPORTED_STATUSES:
                    issues.append(_issue("warning", "task-invalid-status", relative, status))
            dashboard = tasks_dir / "dashboard.md"
            if dashboard.exists():
                expected = render_dashboard(load_tasks(root))
                try:
                    existing = dashboard.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    existing = ""
                if existing != expected:
                    issues.append(_issue("warning", "stale-task-dashboard", "wiki/tasks/dashboard.md"))

        docs_index = root / "wiki" / "docs" / "README.md"
        if docs_index.exists():
            links = _linked_targets(docs_index.read_text(encoding="utf-8"))
            for page in sorted((root / "wiki" / "docs").glob("*.md")):
                if page.name == "README.md":
                    continue
                target = f"docs/{page.stem}"
                if target not in links and target not in (link_sources.get("wiki/index.md") or set()):
                    issues.append(_issue("warning", "orphan-wiki-page", page.relative_to(root).as_posix()))

        exploratory_index = root / "wiki" / "exploratory" / "index.md"
        if exploratory_index.exists():
            links = _linked_targets(exploratory_index.read_text(encoding="utf-8"))
            for page in sorted((root / "wiki" / "exploratory").glob("*.md")):
                if page.name == "index.md":
                    continue
                target = f"exploratory/{page.stem}"
                if target not in links:
                    issues.append(_issue("warning", "orphan-wiki-page", page.relative_to(root).as_posix()))
    return {
        "root": str(root),
        "ok": not any(issue["severity"] == "error" for issue in issues),
        "issues": issues,
        "summary": {
            "errors": sum(1 for issue in issues if issue["severity"] == "error"),
            "warnings": sum(1 for issue in issues if issue["severity"] == "warning"),
        },
    }
