---
id: LLIKI-045
title: Shared document factory, lliki task new / explore new, content templates
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-045-content-creation-commands: Shared document factory, lliki task new / explore new, content templates

## Goal

One internal factory `create_document(kind, title, ...)` powering `lliki task new`, `lliki notes new`, `lliki explore new` with editable `templates/content/{task,note,exploratory}.md`.

## Background

Spec sections 11, 12.

## Required Behavior

- Slug generator, date handling, frontmatter rendering (id, type, title, status, priority, created, updated), safe creation, parent folder index auto-refresh.
- `task new` assigns next `LLIKI-<NNN>` id deterministically from existing task files.
- `templates export` ships content templates.

## Acceptance Criteria

- Three creation commands each produce a valid, doctor-clean document plus updated index.

## Result

Shared `create_document(kind, title, ...)` factory powers `lliki task new`, `notes new`, and `explore new`; `templates export` ships content templates; `task new` assigns the next `LLIKI-<NNN>` id deterministically.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; all three creation commands produce a valid, doctor-clean document plus an updated index.
