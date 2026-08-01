---
id: LLIKI-005
title: Move scratchpad to task-scoped local handover file
status: done
priority: high
updated: 2026-08-01
baseline_commit: 6b29cd75412d13a978478cda30895f2b27854854
---
# LLIKI-005: Move Scratchpad to Task-Scoped Local Handover File

## Goal

Move Lliki's canonical scratchpad from `wiki/scratchpad.md` to
`wiki/tasks/scratchpad.md` and define it as local, ignored, bounded
handover/debug context for one active task per worktree.

## Background

The root wiki scratchpad reads like durable project knowledge even though it is
local runtime handover state. Keeping it under `wiki/tasks/` makes the
execution boundary clearer:

- `wiki/index.md` is the durable knowledge map.
- `wiki/tasks/*.md` are durable task specs and final results.
- `wiki/tasks/dashboard.md` is the generated task catalogue.
- `wiki/tasks/scratchpad.md` is ignored local handover/debug context.

This task was specified against baseline commit
`6b29cd75412d13a978478cda30895f2b27854854`.

## Required Behavior

- Use `wiki/tasks/scratchpad.md` as the only canonical scratchpad path.
- Ignore `/wiki/tasks/scratchpad.md` in `.gitignore`.
- Preserve scratchpad content byte-for-byte during repeated initialization,
  update, and template synchronization.
- Create the new scratchpad in default and custom initialization.
- Exclude `dashboard.md` and `scratchpad.md` from task discovery.
- Treat legacy `wiki/scratchpad.md` as preserved local state:
  - do not delete it;
  - do not move it automatically;
  - warn through `lliki update` and `lliki doctor`;
  - guide users to manually migrate useful notes.
- Update `lliki context`, hooks, `lliki update`, and `lliki doctor` to use the
  new path.
- Update templates, rules, prompts, README, agent integrations, and local wiki
  docs to describe scratchpad as bounded handover/debug context.

## Acceptance Criteria

- [x] `wiki/tasks/scratchpad.md` is the only canonical scratchpad path.
- [x] Init creates the new scratchpad path in default and custom modes.
- [x] Repeated init/update/template sync preserves scratchpad content.
- [x] `.gitignore` uses `/wiki/tasks/scratchpad.md`, not
  `/wiki/scratchpad.md`.
- [x] Task discovery excludes `dashboard.md` and `scratchpad.md`.
- [x] `lliki context` routes from the new scratchpad path.
- [x] Hooks read bounded resume context from the new scratchpad path.
- [x] `lliki update` warns about legacy `wiki/scratchpad.md` without mutating
  it.
- [x] `lliki doctor` reports the new path and bounded-content warnings.
- [x] Docs/prompts describe scratchpad as compact handover/debug context, not a
  full log.
- [x] Tests cover init, update, context, hooks, doctor, task discovery, and
  templates.

## Safety Rules

- Do not delete or rewrite legacy `wiki/scratchpad.md`.
- Do not change package version, tag, publish, push, or release.
- Keep bounded-content checks as warnings.
- Do not introduce a runtime state directory or `.lliki/` replacement.

## Validation

Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src
python -m lliki templates validate
python -m lliki update --dry-run
python -m lliki doctor
```

## Result

Implemented the task-scoped scratchpad model. Lliki now creates and preserves
`wiki/tasks/scratchpad.md`, manages `/wiki/tasks/scratchpad.md` in
`.gitignore`, routes context and hooks through the new path, excludes
`dashboard.md` and `scratchpad.md` from task discovery, and reports legacy
`wiki/scratchpad.md` as preserved local state.

## Evidence

- **Baseline commit:** `6b29cd75412d13a978478cda30895f2b27854854`
- **Source:** `src/lliki/core/paths.py`, `src/lliki/core/context.py`,
  `src/lliki/core/doctor.py`, `src/lliki/core/gitignore.py`,
  `src/lliki/core/update.py`, `src/lliki/core/tasks.py`, `src/lliki/hooks.py`
- **Templates/docs:** `src/lliki/templates/`, `README.md`, `docs/`,
  `wiki/wiki-rules.md`
- **Tests:** `tests/test_lliki.py`, `tests/test_cli_subprocess.py`
- **Validation:** `python -m unittest discover -s tests -v` passed with 29
  tests; `python -m compileall -q src` passed; `python -m lliki templates
  validate` passed; `python -m lliki update --dry-run` reported no planned
  mutations and one expected legacy scratchpad warning; `python -m lliki
  doctor` reported 0 errors and 1 expected warning for preserved
  `wiki/scratchpad.md`; `.venv\Scripts\python.exe -m build` passed and
  included `lliki/templates/wiki/tasks/scratchpad.md` in the built
  distribution artifacts.
