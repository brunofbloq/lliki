"""Terminal branding for Lliki's interactive setup."""

from __future__ import annotations

import os
import shutil
import sys
from typing import TextIO
from lliki import __version__


LARGE_LOGO = r"""
 __         __         __     __  __     __    
/\ \       /\ \       /\ \   /\ \/ /    /\ \   
\ \ \____  \ \ \____  \ \ \  \ \  _"-.  \ \ \  
 \ \_____\  \ \_____\  \ \_\  \ \_\ \_\  \ \_\ 
  \/_____/   \/_____/   \/_/   \/_/\/_/   \/_/ 
                                               
""".strip("\n").splitlines()

COMPACT_LOGO = r"""
 _       _       ___  _  __ ___
| |     | |     |_ _|| |/ /|_ _|
| |     | |      | | | ' /  | |
| |___  | |___   | | | . \  | |
|_____| |_____| |___||_|\_\|___|
""".strip("\n").splitlines()

PURPOSE = "Local-first repository wiki setup and maintenance for humans and coding tools."
PRIVACY = "No LLM API required; repository content stays local by default."
AUTHOR = "brunofbloq"
VERSION = __version__

def banner_enabled() -> bool:
    """Return whether the interactive welcome banner is enabled."""
    value = os.environ.get("LLIKI_NO_BANNER", "").strip().lower()
    return value not in {"1", "true", "yes", "on"}


def render_welcome(width: int | None = None) -> str:
    """Render a width-aware welcome block without terminal control sequences."""
    columns = width or shutil.get_terminal_size(fallback=(100, 24)).columns
    logo = LARGE_LOGO if columns >= 78 else COMPACT_LOGO
    rule_width = min(max(len(PURPOSE), len(PRIVACY), 48), max(columns, 48))
    rule = "─" * rule_width
    return "\n".join(
        (
            *logo,
            "",
            PURPOSE,
            PRIVACY,
            f"Version: {VERSION}",
            rule,
        )
    )


def print_welcome(stream: TextIO = sys.stdout, width: int | None = None) -> None:
    """Print the welcome block for a human-facing interactive setup."""
    print(render_welcome(width=width), file=stream)
    print(file=stream)


def render_commands_panel(commands: "list[tuple[str, str]]", width: int | None = None) -> str:
    """Render a framed command overview; every line is exactly ``columns`` wide."""
    columns = width or shutil.get_terminal_size(fallback=(80, 24)).columns
    name_width = max(len(name) for name, _ in commands)
    columns = max(columns, name_width + 16)
    max_help = columns - name_width - 6
    lines = ["╭─ Commands " + "─" * (columns - 13) + "╮"]
    for name, help_text in commands:
        text = help_text if len(help_text) <= max_help else help_text[: max_help - 1] + "…"
        lines.append(f"│ {name:<{name_width}}  {text:<{max_help}} │")
    lines.append("╰" + "─" * (columns - 2) + "╯")
    return "\n".join(lines)
