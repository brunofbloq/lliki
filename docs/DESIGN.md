# Lliki Design

Lliki is deterministic continuity infrastructure for LLM-assisted software
development. Its job is to keep coding agents oriented across context
compaction, session switches, repeated debugging, and repository evolution.

The repository wiki is the storage model. Continuity is the product.

## Boundary

The CLI owns deterministic mechanics:

- structure inspection and bootstrap;
- existing wiki update orchestration;
- managed-section synchronization;
- task dashboard generation;
- prompt rendering and token estimates;
- structural validation;
- safe append operations;
- scratchpad and backup ignore-rule maintenance.

The coding agent or human owns semantic work:

- project purpose and scope;
- architecture decisions;
- root-cause interpretation;
- lessons learned;
- concise task outcomes and validation summaries;
- maintained project documentation.

Lliki does not call an LLM, use embeddings, upload repository content, or make
semantic claims about the project.

## Context Strategy

`wiki/tasks/scratchpad.md` is the first stop when resuming active local work.
It is ignored by Git and stores compact handover/debug context for one active
task in the current worktree.

`wiki/index.md` is the first stop for new work or a workstream switch. It is a
stable knowledge map, not a mutable status board.

`wiki/tasks/dashboard.md` is a compact generated routing index for active,
blocked, and planned work. It intentionally omits completed-history bloat so
agents do not pay for irrelevant task history by default.

`wiki/decisions.md` and `wiki/lessons_learned.md` preserve durable engineering
memory. Task files keep stable intent and concise final results.

## Setup Modes

Default setup creates or repairs the wiki, updates the managed section in
`CLAUDE.md`, and prints the initialization prompt with token estimates.

Custom setup adds selected repository-local integrations. No integration is
installed globally, and custom setup uses the same `wiki/` root and scratchpad
as default setup.

## Maintenance Model

Wiki review occurs after meaningful task events and at the end of completed
requests. No permanent update is required when project truth did not change.
Mechanical refreshes may run without an LLM and should be idempotent.

`lliki update` is the deterministic migration command for existing
repositories. It updates safe managed content, creates missing local handover
files, refreshes the dashboard, and reports semantic migration work for humans
or LLM agents.

Generated task dashboard backups are stored in `wiki/tasks/.backup/` so task
routing stays compact.

## Scratchpad and Task Files

`wiki/tasks/scratchpad.md` is created by default, ignored by Git, bounded, and
non-authoritative. It may grow during active debugging, should be compacted
when stale details accumulate, and is reset when the task is completed.

Task files are stable specifications plus concise final results. During active
work, checkpoint progress, blockers, and next actions belong in
`wiki/tasks/scratchpad.md`; durable rationale belongs in `wiki/decisions.md`;
reusable findings belong in `wiki/lessons_learned.md`. Lliki does not create a
`wiki/tasks/archive/` folder.

Lliki never creates `.lliki/`, `state.json`, or runtime logs. Existing
`.lliki/` directories are reported as legacy local state and left for the user
to remove manually.

## Template Ownership

All generated text is stored under `src/lliki/templates/`. A user may export
that directory, edit Markdown normally, validate it, and select it using
`--template-dir` or `LLIKI_TEMPLATE_DIR`.
