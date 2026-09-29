---
id: LLIKI-053
title: Command surface compaction - width fix, deprecated removal, doctor+inspect merge
status: done
priority: normal
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-053-command-surface: lean command UX

## Goal

Fix the landing panel width adaptation, remove all deprecated command surface,
make single-action verbs work bare, merge `hook` under `integration`, and
merge `inspect` into `doctor`.

## Background

User-driven UX review after LLIKI-052: panel mis-rendered (off-by-one top
border, 52-char floor, piped fallback 100); argparse surfaced deprecated stubs
and machine-only commands to humans.

## Required Behavior

- `render_commands_panel`: every line exactly terminal width; grows help
  truncation instead of overflowing narrow terminals.
- Deleted: `state` (show/update), `init --runtime`, `init --scratchpad`,
  `tasks refresh --update-index`, `inspect`, `tasks refresh` and `index
  refresh` subcommands.
- Bare `lliki tasks` refreshes tasks-index; bare `lliki index` refreshes all
  folder indexes; bare `lliki integration` shows status.
- `lliki hook <event>` rewrites to `lliki integration hook <event>` before
  parsing (installed settings.json compatibility); hidden from `--help`.
- `doctor --json` includes `inspection.locations` + `inspection.signals` and a
  `--max-depth` flag; text mode prints `Legacy locations:` only when legacy
  directories exist; exit code remains driven by health issues only.

## Acceptance Criteria

- Panel line widths uniform at 40/80/120; removed surface rejected; alias and
  bare forms tested; suite green.

## Result

Implemented in `src/lliki/cli.py`, `src/lliki/branding.py`,
`src/lliki/integrations/install.py` (hooks now write the canonical
`lliki integration hook` command). Docs and templates updated (README,
SKILL.md, wiki-rules + local, development-workflow, project-overview).
DEC-009 recorded.

## Validation

51/51 `pytest` pass, including new uniform-width panel, bare tasks/index,
doctor inspection JSON/text, hook alias, and removal-rejection tests;
subprocess suite rerouted from `inspect` to `doctor`. Manual smoke of all
bare commands on this repo; `lliki update`/`lliki doctor` 0/0. Not validated:
real Claude session with previously installed settings.json (alias path is
unit-tested only).
