---
id: LLIKI-004
title: Add lliki update for existing wiki migration
status: done
priority: high
updated: 2026-08-01
baseline_commit: 6b29cd75412d13a978478cda30895f2b27854854
---
# LLIKI-004: Add `lliki update`

## Goal

Add a single human-friendly command for upgrading an existing repository wiki to
the currently installed Lliki template/model without requiring users to run a
sequence of lower-level maintenance commands.

## Background

After the scratchpad/knowledge-map refactor, existing repositories may still
have:

- old `.lliki/` runtime state;
- mutable active-status sections in `wiki/index.md`;
- missing `wiki/scratchpad.md`;
- missing `/wiki/scratchpad.md` in `.gitignore`;
- stale managed sections, prompts, integrations, or wiki rules.

This task was specified against baseline commit
`6b29cd75412d13a978478cda30895f2b27854854`.

Users should be able to run:

```bash
lliki update
```

and get a safe migration report plus any deterministic updates that can be made
without rewriting user-authored project knowledge.

## Required Behavior

- Inspect the current repository wiki/template state.
- Detect legacy `.lliki/` usage and report it as manual cleanup guidance.
- Detect legacy mutable `wiki/index.md` sections.
- Create `wiki/scratchpad.md` when missing and preserve it byte-for-byte when
  present.
- Ensure `.gitignore` contains exactly one effective `/wiki/scratchpad.md`
  entry.
- Apply safe managed-section template updates.
- Refresh `wiki/tasks/dashboard.md`.
- Run structural doctor checks after updates.
- Prefer human-readable output by default.
- Provide `--json` for automation.
- Support `--dry-run` to report planned actions without writing files.
- Print a focused LLM migration prompt only when semantic migration is needed,
  such as converting a legacy mutable index to the stable knowledge map.

## Safety Rules

- Do not blindly rewrite user-authored `wiki/index.md`.
- Do not delete, move, or rewrite `.lliki/`.
- Do not automatically untrack `wiki/scratchpad.md` if it is already tracked.
- Do not rewrite scratchpad content.
- Do not call an LLM, network service, or external API.
- Do not change package version, publish, tag, or push.

## Suggested CLI

```bash
lliki update --root .
lliki update --root . --dry-run
lliki update --root . --json
```

## Acceptance Criteria

- [x] `lliki update` performs deterministic safe migration steps.
- [x] Existing scratchpad content is preserved.
- [x] Missing scratchpad is created.
- [x] Scratchpad ignore rule is created or deduplicated.
- [x] Managed sections are updated safely.
- [x] Dashboard refresh runs without mutating `wiki/index.md`.
- [x] Legacy `.lliki/` is reported but untouched.
- [x] Legacy mutable index sections trigger warning and LLM prompt guidance.
- [x] Human output is concise and actionable.
- [x] JSON output is stable for agents/scripts.
- [x] Dry-run makes no filesystem changes.
- [x] Unit tests cover fresh, current, legacy, and dry-run scenarios.

## Result

Implemented `lliki update` as deterministic maintenance orchestration around
template sync, scratchpad ignore-rule repair, dashboard refresh, doctor checks,
and semantic migration reporting. The command supports human output, `--json`,
and `--dry-run`.

## Evidence

- **Baseline commit:** `6b29cd75412d13a978478cda30895f2b27854854`
- **Source:** `src/lliki/core/update.py`, `src/lliki/cli.py`
- **Tests:** `tests/test_lliki.py`, `tests/test_cli_subprocess.py`
- **Validation:** `python -m unittest discover -s tests -v` passed with 27
  tests; `python -m compileall -q src` passed; `python -m lliki templates
  validate` passed; `python -m lliki update --dry-run` passed; `python -m
  lliki update` passed; `python -m lliki doctor` reported 0 errors and 0
  warnings; wheel build, Twine check, and clean installed-wheel smoke passed.

## Validation

Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src
lliki templates validate
lliki update --dry-run
lliki update
lliki doctor
```

Also verify an installed wheel can run `lliki update` in a temporary repository.
