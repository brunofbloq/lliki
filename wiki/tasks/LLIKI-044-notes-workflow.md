---
id: LLIKI-044
title: Notes folder, notes CLI, note template
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-044-notes-workflow: Notes folder, notes CLI, note template

## Goal

First-class notes: `lliki notes new|list|show|append|search` over `wiki/notes/`.

## Background

Spec sections 9, 10. Encryption is 0.4.1 — out of scope.

## Required Behavior

- `notes new TITLE` creates `wiki/notes/YYYY-MM-DD-slug.md` with front matter (type/title/created/updated/tags), refreshes notes-index, refuses overwrite.
- list shows notes newest-first; show prints content; appends `append` adds a section or text; `search` is a deterministic case-insensitive scan of names and content.

## Acceptance Criteria

- Each command works on a fresh init repo without any LLM.

## Result

`lliki notes new|list|show|append|search` implemented over `wiki/notes/`; `notes new` writes `YYYY-MM-DD-slug.md` with front matter, refreshes notes-index, and refuses overwrite.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; each command works on a fresh init repo without any LLM.
