"""Terminal branding for Lliki's interactive setup."""

from __future__ import annotations

import os
import shutil
import sys
from typing import TextIO


LARGE_LOGO = r"""
 ____          ____          ____  ____  ___  ____
|\   \        |\   \        |\   \|\   \|\  \|\   \
\ \   \       \ \   \       \ \   \\ \   \ \  \\ \   \
 \ \   \       \ \   \       \ \   \\ \   \ \  \\ \   \
  \ \   \____   \ \   \____   \ \   \\ \   \ \  \\ \   \____
   \ \________\  \ \________\   \ \__\\ \__\ \__\\ \________\
    \|________|   \|________|    \|__| \|__|\|__| \|________|
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
            f"Author: {AUTHOR}",
            rule,
        )
    )


def print_welcome(stream: TextIO = sys.stdout, width: int | None = None) -> None:
    """Print the welcome block for a human-facing interactive setup."""
    print(render_welcome(width=width), file=stream)
    print(file=stream)
