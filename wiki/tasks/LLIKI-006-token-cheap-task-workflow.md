---
id: LLIKI-006
title: Simplify task workflow for token-cheap maintenance
status: done
priority: high
updated: 2026-08-01
baseline_commit: 0d30dc2fe922c8be3204c6c6fe669ca1d7205b95
---
# LLIKI-006: Simplify Task Workflow for Token-Cheap Maintenance

## Goal

Make `wiki/tasks/` cheaper to read, easier to maintain, and safer for
concurrent agents by separating stable task intent, temporary execution
progress, generated routing, and durable history.

## Background

The current task workflow still creates avoidable token and diff noise:

- dashboard backup files are written beside task files;
- `dashboard.md` includes more generated text than routing requires;
- completed task files can duplicate evidence already promoted to decisions or
  lessons;
- acceptance criteria may be checked off during execution even though the
  scratchpad is the better place for temporary progress.

This task was specified against baseline commit
`0d30dc2fe922c8be3204c6c6fe669ca1d7205b95`.

## Required Behavior

- Store dashboard backups under `wiki/tasks/.backup/` instead of directly under
  `wiki/tasks/`.
- Ignore `/wiki/tasks/.backup/` in Git and exclude it from task discovery and
  doctor scans.
- Simplify `wiki/tasks/dashboard.md` into a minimal routing index with only the
  sections needed to find current work.
- Keep task files focused on stable intent and final outcome:
  - preserve goal, background, required behavior, constraints, and acceptance
    criteria as stable task definition;
  - avoid updating acceptance checkboxes during execution;
  - record temporary progress only in `wiki/tasks/scratchpad.md`;
  - at completion, add a concise result and validation summary.
- Move durable rationale and reusable findings to their concrete homes:
  - accepted rationale belongs in `wiki/decisions.md`;
  - reusable findings belong in `wiki/lessons_learned.md`;
  - task files should link to those records instead of duplicating long evidence
    sections.
- Do not add a `wiki/tasks/archive/` folder as part of this change.

## Acceptance Criteria

- `refresh_dashboard` writes dashboard backups to `wiki/tasks/.backup/`.
- `.gitignore` contains `/wiki/tasks/.backup/`.
- Task discovery ignores `dashboard.md`, `scratchpad.md`, `.backup/`, and
  `*.bak.*`.
- The generated dashboard is compact and token-cheap.
- Completed task guidance prefers short result and validation summaries, with
  links to decisions and lessons.
- Scratchpad guidance says execution progress belongs in
  `wiki/tasks/scratchpad.md`, not acceptance-checkbox churn.
- `lliki doctor` does not warn about dashboard backups as tasks or orphan wiki
  pages.
- Existing root-level `dashboard.md.bak.*` files are either moved to
  `wiki/tasks/.backup/` or left ignored with a clear migration decision.
- Tests cover backup placement, dashboard rendering, task discovery exclusions,
  and docs/prompts guidance.

## Safety Rules

- Do not create `wiki/tasks/archive/`.
- Do not rewrite historical completed tasks except for narrowly scoped
  migration if explicitly required by tests or doctor behavior.
- Do not delete backup files without explicit approval.
- Do not change package version, publish, tag, or push.

## Validation

Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src
python -m lliki templates validate
python -m lliki tasks refresh --root .
python -m lliki doctor
```

## Result

Implemented token-cheap task maintenance. Dashboard backups now live under
`wiki/tasks/.backup/`, the generated dashboard only lists active, blocked, and
planned work, and task workflow guidance now keeps temporary progress in
`wiki/tasks/scratchpad.md` while durable rationale and reusable findings live in
their dedicated wiki files.

Related decision: [[../decisions#DEC-004: Keep Task Routing Token-Cheap]]

## Validation Summary

- `python -m unittest discover -s tests -v` passed with 34 tests.
- `python -m compileall -q src` passed.
- `python -m lliki templates validate` passed.
- `python -m lliki tasks refresh --root .` passed and moved existing dashboard
  backups to `wiki/tasks/.backup/`.
- `python -m lliki doctor` passed with 0 errors and 0 warnings.
