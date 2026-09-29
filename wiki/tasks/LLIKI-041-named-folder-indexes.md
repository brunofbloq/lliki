---
id: LLIKI-041
title: Create named indexes for existing folders and dashboard.md -> resume.md + tasks-index.md
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-041-named-folder-indexes: Create named indexes for existing folders and dashboard.md -> resume.md + tasks-index.md

## Goal

Ship the named folder indexes for docs/tasks/exploratory/notes and split the old generated dashboard into `tasks-index.md` (collection) + `resume.md` (lean execution route).

## Background

Spec sections 5, 9; accepted design in `wiki/exploratory/dashboard_to_resume.md`: resume renders only current task, scratchpad link, optional next task, transition rule; never auto-selects a next task.

## Required Behavior

- `lliki update` migrates `wiki/index.md` -> `wiki/wiki-index.md`, `wiki/docs/README.md` -> `wiki/docs/docs-index.md`, `wiki/exploratory/index.md` -> `wiki/exploratory/exploratory-index.md`, `wiki/tasks/dashboard.md` -> `wiki/tasks/tasks-index.md` + new `resume.md`, preserving manual content outside generated regions and backing up replaced files.
- Migration is idempotent and `--dry-run` safe.
- `wiki/notes/` + `notes-index.md` created on init/update.

## Acceptance Criteria

- 0.3-style repo migrates without losing manually maintained knowledge.
- Re-running `lliki update` changes nothing.

## Result

Named indexes created for docs/tasks/exploratory/notes; `dashboard.md` split into `tasks-index.md` (collection) + `resume.md` (lean execution route). `lliki update` migrates the 0.3 layout, preserving manual content and backing up replaced files.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; 0.3 migration is idempotent (re-running `lliki update` changes nothing) and `--dry-run` safe.
