---
id: LLIKI-051
title: CocoIndex pilot - semantic search sidecar for wiki and code
status: done
priority: normal
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-051-cocoindex-pilot: Section 28 experiment, extended-graph enrichment

## Goal

Evaluate the spec section 28 idea: use CocoIndex incremental semantic
enrichment to extend the deterministic Lliki graph, without replacing it.

## Background

Original design: build a `cocoindex` library pipeline emitting
`wiki/enrich/*.related.md` sidecars. Revised before any build: `cocoindex-code`
(`ccc`) ships the same pipeline as a finished CLI (incremental indexing, local
embeddings, MCP/skill agent integration), so the pilot was re-scoped to
Phase 0 = evaluate `ccc`; Phase 1 = materialized `wiki/enrich/` graph only if
query-time search proves insufficient.

## Required Behavior

- `ccc` skill installed for agents; index incremental (only changed docs
  reprocessed); state gitignored; lliki core untouched.
- Measured: markdown chunk quality, code recall on known anchors, reindex
  timing.

## Acceptance Criteria

- Pilot evidence recorded as decision-relevant lessons; wiki documents the
  opt-in tooling.

## Result

Phase 0 done with `cocoindex-code` 0.2.41 + `ccc` skill
(`.agents/skills/ccc/`, project-local, untracked). Index: 86 files / 463
chunks; lifecycle verified exactly (1 added → 1 reprocessed → 1 deleted,
86 unchanged throughout). Model findings: default xs embedding gives zero code
recall (all hits are `__init__.py` stubs); CodeRankEmbed crashes on the pinned
torch stack; `snowflake-arctic-embed-m` + `prompt_name: query` restores correct
top hits for code, tests, and wiki queries. Full rebuild ~150s CPU,
incremental near-instant. Lliki core: zero changes.

Phase 1 (materialized `wiki/enrich/` graph) not built: query-time search now
covers the semantic-recall need; revisit only if non-agent consumers (Obsidian
graph edges, offline routing) are demanded.

## Validation

`ccc doctor` green; anchor queries for LLIKI-050 work found
migration/update code, matching tests, DEC-007, and the task file; probe file
removed and index state cleaned. Lesson LL-006 recorded; tooling documented
in `wiki/docs/development-workflow.md`. Not validated: multi-machine model
availability, Windows MPS/CUDA paths, long-session daemon behavior.
