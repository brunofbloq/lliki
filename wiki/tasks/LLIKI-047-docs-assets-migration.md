---
id: LLIKI-047
title: Move repo docs/ into wiki/docs and docs/assets into assets/ (dogfood)
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-047-docs-assets-migration: Move repo docs/ into wiki/docs and docs/assets into assets/ (dogfood)

## Goal

Lliki dogfoods its own architecture: top-level `docs/` project documentation moves into `wiki/docs/`, `docs/assets/` moves to `assets/`.

## Background

Spec section 16, 34-P1 repository cleanup.

## Required Behavior

- `git mv` docs/AGENT_INTEGRATIONS.md, DESIGN.md, IMPLEMENTATION_CHECKPOINTS.md, RELEASE_PROCESS.md into `wiki/docs/`; links in README/CHANGELOG/workflows/MANIFEST updated.
- `assets/lliki-ascii.png` at repo root; README image URL updated.

## Acceptance Criteria

- No dangling `docs/` references; build still packages correctly.

## Result

`docs/` moved into `wiki/docs/` and `docs/assets/` into `assets/` via `git mv`; README/CHANGELOG/workflows/MANIFEST links updated; `assets/lliki-ascii.png` at repo root with README image URL updated.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; no dangling `docs/` references and the build still packages correctly.
