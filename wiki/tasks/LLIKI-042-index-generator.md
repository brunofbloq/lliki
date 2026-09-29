---
id: LLIKI-042
title: Deterministic recursive folder-index generation and lliki index refresh
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-042-index-generator: Deterministic recursive folder-index generation and lliki index refresh

## Goal

`lliki index refresh [folder|--all]`: deterministic, LLM-free generation of `<folder>-index.md` managed regions covering child folders and documents.

## Background

Spec sections 6, 7, 8, 11 (parent-index refresh).

## Required Behavior

- Scan `wiki/`, ensure every directory has its named index; generated region delimited by `<!-- lliki:generated:start id=folder-index -->`.
- Manual content outside the region untouched.
- Links resolve wiki-root-relative; tasks folder groups by status; collections link child folder indexes.
- Any new folder (e.g. `wiki/research/`) gains `research-index.md` automatically on refresh/init/update.

## Acceptance Criteria

- Recursive folders get indexes; refresh is idempotent; doctor WIKI005 detects stale regions.

## Result

`lliki index refresh` is deterministic, LLM-free, and recursive; any new folder (e.g. `wiki/research/`) gains its named index automatically (verified with a `wiki/research/vision` probe). Manual content outside generated regions is preserved. Task index keeps closed tasks reachable via ID-only links while `resume.md` stays a current-work route.

## Validation

46 tests pass; `lliki doctor` 0 errors 0 warnings; refresh is idempotent and WIKI005 detects stale generated regions. Regression covers done, completed, and cancelled task links without routing them as planned.
