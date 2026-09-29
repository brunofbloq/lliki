---
id: LLIKI-052
title: Bare lliki landing shows common-command overview instead of setup
status: done
priority: normal
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-052-landing-overview: read-only command overview on bare lliki

## Goal

Replace the bare-`lliki` alias to `init` with a welcome + framed common-commands
overview that exits without writing; setup only via `lliki init`; all commands
remain discoverable through `lliki --help`.

## Background

User request modeled on the cocoindex-code TUI panel. The old alias made the
first thing users saw a destructive-capable setup prompt and hid the other
13 commands.

## Required Behavior

- `branding.render_commands_panel(commands, width)`: framed panel, width-aware,
  long help truncated with `…`.
- Landing panel lists `init`, `update`, `doctor`, `index`, `tasks`, `context`,
  `prompt` with help text derived from the argparse subparsers; footer points
  to `lliki --help`.
- Bare `lliki` writes nothing and returns 0. Non-interactive `init --default
  --yes` flow unchanged.
- Vague help strings tightened (`inspect`, `context`, `append`).

## Acceptance Criteria

- Tests cover no-write landing, panel content, and `--help` completeness.

## Result

Implemented in `src/lliki/cli.py` (landing branch + `_command_helps` +
`_COMMON_COMMANDS`) and `src/lliki/branding.py`. README setup section and
Interactive Welcome updated. Decision DEC-008 recorded.

## Validation

48/48 `pytest` pass, including new
`test_bare_lliki_shows_command_overview_without_writing` and
`test_help_lists_all_public_commands`; manual render check at 100 and 50
columns. Not validated: terminal encodings on consoles without box-drawing
glyphs (output path uses the existing UTF-8/replace stdio configuration).
