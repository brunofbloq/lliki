<!-- lliki:managed:start id=lliki-contract -->
# CLAUDE.md — Repository Agent Contract

This file defines stable repository-wide behavior for coding agents. It is not
project status or project documentation. Changing project knowledge belongs
under `wiki/`.

## Context loading

`wiki/index.md` is the only mandatory dynamic project entry point.

At the beginning of work:

1. Read `wiki/index.md`.
2. Follow its active-task link when one exists.
3. Load only the linked documentation, decisions, explorations, and source files
   relevant to the current request.
4. Read `wiki/tasks/dashboard.md` only when selecting or coordinating work, or
   when the index does not identify an active task.
5. Read `wiki/wiki-rules.md` when maintaining or reorganizing the wiki, creating
   a new wiki document type, or when information placement is unclear.

Do not recursively load the entire wiki or repository. Re-read the index when
switching workstreams, resuming after a significant interruption, or when
another agent may have changed project context.

## Evidence and scope

Prefer explicit user instructions and repository evidence over assumptions.
Treat measurements, authoritative specifications, source code, accepted
project decisions, and maintained documentation according to the authority
order defined in `wiki/wiki-rules.md`.

Do not invent requirements, hardware values, commands, protected paths,
architecture, task status, build results, or validation outcomes. Mark missing
information as `Unknown`, `TBD`, or `Needs validation`.

Before editing, understand the active task's goal, scope, constraints,
acceptance criteria, and expected evidence. Make the smallest coherent change
that satisfies the request. Avoid unrelated refactors, formatting sweeps,
renames, dependency upgrades, generated-file churn, and cleanup outside scope.

Project commands and toolchain procedures belong in
`wiki/docs/development-workflow.md`. Project-specific protected paths, generated
or vendor boundaries, and modification procedures belong in
`wiki/docs/repository-rules.md`. Do not duplicate them here.

## Agent and skill usage

Use specialist skills, subagents, or agent tools only when they are available
and materially relevant to the task. Inspect their actual instructions before
using them. Project evidence and the user's intent remain authoritative over
generic specialist guidance.

When the `lliki` CLI is available, agents may use it internally for
mechanical operations such as structural inspection, managed-template checks,
task-dashboard refresh, safe appends, and wiki validation. The user should not
need to invoke these commands during normal development.

## Wiki updates

The implementing agent owns semantic wiki updates caused by its work.

Review whether a wiki update is needed:

- after a meaningful task event, such as a status change, completed subtask,
  accepted decision, confirmed reusable finding, or durable change in project
  truth; and
- at the end of each completed user request.

When project truth did not change, do not edit the wiki merely to update a
timestamp. Do not update permanent wiki files after every command, read, build,
or failed experiment.

Apply focused changes only:

- update the active task with outcome and evidence;
- append an accepted decision only when a real decision was made;
- append a lesson only when the finding is confirmed and reusable;
- update maintained documentation only when durable project truth changed;
- update `wiki/index.md` only when project-level routing, priorities, blockers,
  or major status changed.

Temporary runtime state and scratch material are optional. When configured,
they live under `.lliki/`, are not authoritative project knowledge, and
must not be loaded unless needed for resumption or debugging.

## Completion and reporting

A task is complete when its acceptance criteria are met with traceable evidence,
applicable validation has been performed or omissions are explicit, the diff is
focused, and relevant durable project knowledge is current.

The final report must identify changed files, validation performed, verified
results, omitted checks, remaining assumptions or risks, and follow-up work.
Never claim a build, flash, test, measurement, or target result that was not
actually performed.
<!-- lliki:managed:end id=lliki-contract -->
