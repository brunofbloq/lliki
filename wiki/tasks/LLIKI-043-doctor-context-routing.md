---
id: LLIKI-043
title: Doctor index-contract checks and context --json collection routing
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-043-doctor-context-routing: Doctor index-contract checks and context --json collection routing

## Goal

Extend `lliki doctor` and `lliki context --json` for the 0.4 information architecture.

## Background

Spec sections 21, 22, 23.

## Required Behavior

- Doctor codes: WIKI001 missing folder index, WIKI002 broken internal link (rename of broken-wiki-link), WIKI003 orphan document, WIKI004 legacy path (index.md/dashboard.md/docs README), WIKI005 stale generated index, WIKI006 incorrect index filename, WIKI007 index does not link child folder index.
- `context --json` returns entry/resume/scratchpad/tasks/docs/exploratory/notes/decisions/lessons plus `collections` for custom folders; keeps mode/active_task.

## Acceptance Criteria

- DoD checks pass on fresh init; targeted warnings on drifted wikis; existing scratchpad checks retained.

## Result

`lliki doctor` gains WIKI001-WIKI007 index-contract checks; `lliki context --json` returns entry/resume/scratchpad/tasks/docs/exploratory/notes/decisions/lessons plus `collections` for custom folders, keeping mode/active_task.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; DoD checks pass on fresh init with targeted warnings on drifted wikis.
