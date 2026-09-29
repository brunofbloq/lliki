---
id: LLIKI-050
title: Retire resume.md; tasks-index as single execution entry; lean prompts
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-050-retire-resume: tasks-index as single execution entry and lean prompts

## Goal

Remove `wiki/tasks/resume.md` and its `resume-route` generator entirely; the
generated `## Current Task` region inside `tasks-index.md` plus the scratchpad
become the single execution entry. Lean the prompt templates of vestigial
specialist-skill/embedded wording.

## Background

The resume route only mirrored scratchpad state (already declared the single
handover source in the agent contract) and cost a second generator, doctor
checks, and refresh plumbing across `cli`, `hooks`, `update`, `bootstrap`,
`migration`. Merge discussion confirmed the two files answer different
questions but the second answer is derivable from the first.

## Required Behavior

- `lliki init`/`update`/`index refresh` render `## Current Task` inside the
  tasks-index generated region (scratchpad-selected task or `- None.`, plus
  scratchpad link); no `resume.md` is created anywhere.
- Existing `resume.md` is retired to `wiki/tasks/.backup/` by the layout
  migration; doctor flags a leftover via the legacy-path check.
- `lliki tasks refresh` refreshes the tasks folder index.
- Transition rule survives as one sentence in `wiki-rules.md` Task Workflow.
- `initialize-project` prompt: sequential numbering, no specialist-skills
  footer; `explore-impact` prompt: no embedded-specific hardware/timing/power
  wording; `complete-task` prompt: no resume references.
- Templates, contract files, integrations, README, and local wiki reflect the
  single-index route.

## Acceptance Criteria

- No `resume`/`RESUME` identifiers remain in `src/lliki` except the scratchpad
  routing mode string and the legacy-path/migration entries.
- Full test suite passes; new tests cover the `## Current Task` region and the
  resume retirement migration.
- This repo runs `lliki update` + `lliki doctor` clean with the new region.

## Result

`resume.md` and the `resume-route` generator removed from code, templates,
integrations, and docs. `tasks-index.md` renders a generated `## Current Task`
region from the scratchpad; migration retires old `resume.md` to
`wiki/tasks/.backup/`; doctor legacy-path check flags leftovers. Prompts
leaned: no specialist-skills footer, sequential numbering, no embedded or
resume wording. Transition rule moved into `wiki-rules.md` Task Workflow.

## Validation

46/46 `pytest` pass, including rewritten current-task/migration tests.
`lliki update` and `lliki doctor` on this repo: 0 errors, 0 warnings;
`tasks-index.md` regenerated with the LLIKI-050 current-task route. Not
validated: real Claude hook session runtime (smoke-tested via hook unit test
only).
