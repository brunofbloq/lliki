# Lliki V2 Design

## Boundary

The CLI owns deterministic mechanics:

- structure inspection and bootstrap;
- existing wiki update orchestration;
- managed-section synchronization;
- task dashboard generation;
- prompt rendering and token estimates;
- structural validation;
- safe append operations;
- scratchpad ignore-rule maintenance.

The coding agent or human owns semantic work:

- project purpose and scope;
- architecture decisions;
- root-cause interpretation;
- lessons learned;
- task outcomes and evidence;
- maintained project documentation.

## Context strategy

`wiki/index.md` is the stable knowledge map for new work and workstream
switches. `wiki/tasks/scratchpad.md` is the ignored local handover file for resuming
active work. The root agent contract remains stable. Tasks and docs link to the
minimum context needed.

## Setup modes

### Default

Creates/repairs the wiki, updates the managed section in `CLAUDE.md`, and prints
the initialization prompt with token estimates.

### Custom

Adds selected repository-local integrations. No integration is installed
globally, and custom setup uses the same `wiki/` root and scratchpad as default
setup.

## Update cadence

Wiki review occurs after meaningful task events and at the end of completed user
requests. No permanent update is required when project truth did not change.
Mechanical refreshes may run without an LLM and should be idempotent.

`lliki update` is the deterministic migration command for existing repositories.
It updates safe managed content, creates missing local handover files, refreshes
the dashboard, and reports semantic migration work for humans or LLM agents.

## Scratchpad

`wiki/tasks/scratchpad.md` is created by default, ignored by Git, bounded, and
non-authoritative. It stores compact handover/debug context for one active task
and one writing agent per worktree. It may grow during active debugging, should
be compacted when stale details accumulate, and is reset when the task is
completed.

Lliki never creates `.lliki/`, `state.json`, or runtime logs. Existing `.lliki/`
directories are reported as legacy local state and left for the user to remove
manually.

## Template ownership

All generated text is stored under `src/lliki/templates/`. A user may export
that directory, edit Markdown normally, validate it, and select it using
`--template-dir` or `LLIKI_TEMPLATE_DIR`.
