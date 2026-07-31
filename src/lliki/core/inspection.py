from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv",
    "node_modules", "build", "Build", "dist", "out", ".cache", "__pycache__",
}



def _depth(root: Path, path: Path) -> int:
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return 999


def find_legacy_locations(root: Path, max_depth: int = 6) -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {"legacy_dirs": [], "claude_files": [], "wiki_dirs": []}
    root = root.resolve()
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        depth = _depth(root, current_path)
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and depth < max_depth]
        for directory in list(dirs):
            full = current_path / directory
            rel = full.relative_to(root).as_posix()
            rel_parts = Path(rel).parts
            is_legacy = (
                directory in {".context", ".tasks"}
                or (directory == "tasks" and "wiki" not in rel_parts)
            )
            if is_legacy:
                found["legacy_dirs"].append(rel)
            if directory == "wiki":
                found["wiki_dirs"].append(rel)
        if "CLAUDE.md" in files:
            found["claude_files"].append((current_path / "CLAUDE.md").relative_to(root).as_posix())
    for values in found.values():
        values.sort()
    return found


def repository_signals(root: Path) -> list[str]:
    candidates = {
        "CMake": ["CMakeLists.txt"],
        "STM32CubeMX": ["*.ioc"],
        "PlatformIO": ["platformio.ini"],
        "Cargo": ["Cargo.toml"],
        "Python": ["pyproject.toml", "requirements.txt"],
        "Node.js": ["package.json"],
        "Make": ["Makefile"],
    }
    signals: list[str] = []
    for name, patterns in candidates.items():
        if any(any(root.glob(pattern)) for pattern in patterns):
            signals.append(name)
    return signals
