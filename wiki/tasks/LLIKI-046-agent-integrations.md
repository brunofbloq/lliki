---
id: LLIKI-046
title: Hermes/Claude/generic contract updates and integration status
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-046-agent-integrations: Hermes/Claude/generic contract updates and integration status

## Goal

Point all agent-facing contracts at the new architecture; fix the Hermes setup message; add `lliki integration status`.

## Background

Spec sections 17, 18, 34-P1 integrations.

## Required Behavior

- Templates (CLAUDE.md, HERMES.md, AGENTS.md, claude SKILL.md, prompts) reference `wiki/wiki-index.md`, `wiki/tasks/resume.md`, folder indexes; navigation rule: follow named indexes before scanning folders.
- `lliki init --custom --integrate hermes` prints the Hermes navigation contract message.
- `lliki integration status [--json]` reports which integrations are present and whether managed sections are current.

## Acceptance Criteria

- No template or prompt still references `wiki/index.md` or `dashboard.md`.

## Result

Agent templates (CLAUDE.md, HERMES.md, AGENTS.md, claude SKILL.md, prompts) now reference `wiki/wiki-index.md`, `wiki/tasks/resume.md`, and folder indexes; `lliki init --custom --integrate hermes` prints the Hermes navigation contract message; `lliki integration status` reports present/current integrations.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; no template or prompt still references `wiki/index.md` or `dashboard.md`.
