# Lliki V2 Design

## Boundary

The CLI owns deterministic mechanics:

- structure inspection and bootstrap;
- managed-section synchronization;
- task dashboard generation;
- prompt rendering and token estimates;
- structural validation;
- safe append operations;
- optional local runtime state.

The coding agent or human owns semantic work:

- project purpose and scope;
- architecture decisions;
- root-cause interpretation;
- lessons learned;
- task outcomes and evidence;
- maintained project documentation.

## Context strategy

`wiki/index.md` is the only mandatory dynamic entry point. The root agent
contract remains stable. Tasks link to the minimum context needed. Optional
runtime state is not authoritative and is never mandatory context.

## Setup modes

### Default

Creates/repairs the wiki, updates the managed section in `CLAUDE.md`, and prints
the initialization prompt with token estimates.

### Custom

Adds selected repository-local integrations and optional `.lliki/` state.
No integration is installed globally.

## Update cadence

Wiki review occurs after meaningful task events and at the end of completed user
requests. No permanent update is required when project truth did not change.
Mechanical refreshes may run without an LLM and should be idempotent.

## Scratchpad

Scratchpad is disabled by default. In debug mode it lives at
`.lliki/scratchpad.md`, is gitignored, and remains non-authoritative. It is
not loaded unless resuming or debugging.

## Template ownership

All generated text is stored under `src/lliki/templates/`. A user may export
that directory, edit Markdown normally, validate it, and select it using
`--template-dir` or `LLIKI_TEMPLATE_DIR`.
