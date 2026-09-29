---
id: LLIKI-040
title: Freeze folder-index convention and rename wiki/index.md to wiki/wiki-index.md
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-040-information-architecture: Freeze folder-index convention and rename wiki/index.md to wiki/wiki-index.md

## Goal

Establish the `<folder-name>-index.md` convention as the contract for Lliki 0.4.0 and rename the top-level wiki index.

## Background

Spec: `wiki/exploratory/implementation_plan.md` sections 1, 4, 18, 34-P0. Convention: every directory under `wiki/` carries its own named index acting as a references-only collection node.

## Required Behavior

- `wiki/index.md` becomes `wiki/wiki-index.md` (template + this repo).
- `wiki-rules.md` documents the convention and the agent navigation rule (wiki-index -> folder index -> document; resume via `wiki/tasks/resume.md`; no recursive wiki reads).
- Indexes stay references-only.

## Acceptance Criteria

- Fresh `lliki init` produces `wiki/wiki-index.md` and no `wiki/index.md`.
- `lliki doctor` accepts the new layout.
- Tests updated and passing (`python -m unittest discover -s tests`).

## Result

`wiki/index.md` renamed to `wiki/wiki-index.md` in template and repo; `wiki-rules.md` documents the folder-index convention and the navigation rule (wiki-index -> folder index -> document; resume via `wiki/tasks/resume.md`). Indexes remain references-only.

## Validation

44/44 `python -m unittest discover -s tests` pass; `lliki doctor --root .` reports 0 errors 0 warnings; fresh `lliki init` produces `wiki/wiki-index.md` and no `wiki/index.md`.
