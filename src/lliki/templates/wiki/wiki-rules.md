<!-- lliki:managed:start id=wiki-rules -->
# Wiki Rules

The wiki is the repository's persistent and evolving project knowledge. It
contains what the project is, what is known, and what is currently happening.
The root agent contract defines how agents work.

## Entry point and selective loading

`wiki/index.md` is the only mandatory dynamic entry point. From it, open the
active task and only the context relevant to the current request. Do not load
the entire wiki by default.

Use `wiki/tasks/dashboard.md` for task selection or multi-task coordination,
not as mandatory session context.

## Structure and ownership

- `index.md`: concise project routing, priorities, active task, and major blockers.
- `tasks/dashboard.md`: operational task overview, preferably generated from task metadata.
- `tasks/*.md`: task scope, acceptance criteria, progress, evidence, and outcome.
- `decisions.md`: append-only accepted, rejected, and superseded decisions.
- `lessons_learned.md`: confirmed reusable engineering findings.
- `exploratory/`: investigation, alternatives, impact analysis, and unresolved findings.
- `docs/`: validated and maintained project documentation.

The person or agent performing the work owns the corresponding semantic updates.
A curator may review consistency at explicit checkpoints but must not invent
technical conclusions.

## Authority order

When information conflicts, use this order and investigate material conflicts:

1. Applicable safety, security, and legal constraints.
2. Explicit instructions for the current task.
3. Reproducible measurements and approved hardware evidence.
4. Exact-part authoritative specifications, schematics, and errata.
5. Source code, generated configuration, build configuration, and linker data.
6. Accepted decisions and maintained documentation.
7. Active tasks and confirmed lessons.
8. Exploratory material.
9. Optional temporary runtime state or scratch material.
10. Generic model or skill knowledge.

## Information lifecycle

Move information according to maturity rather than copying it everywhere:

```text
observation or experiment
        ↓
active task or exploratory report
        ↓
validated result
        ↓
decision, lesson, or maintained documentation
```

Exploratory findings are not authoritative until validated and promoted.
Temporary runtime information, when enabled, lives under `.lliki/` and is
not part of the permanent wiki.

## Update policy

Review wiki needs after meaningful task events and at the end of completed user
requests. Update only files whose underlying truth changed.

Do not update permanent wiki files after every command or minor source edit.
Do not create empty timestamp-only changes.

Update `index.md` only when project-level routing, priorities, major blockers,
or significant milestones change. Update tasks for meaningful progress, scope,
status, evidence, or outcome changes. Update decisions, lessons, and docs only
with validated information useful beyond the current task.

## Writing and structural rules

Keep content concise, factual, evidence-linked where practical, explicit about
unknowns, and understandable without reconstructing a chat transcript. Prefer
stable headings, checklists, tables, exact names, absolute dates, and links to
authoritative locations instead of duplication.

Create only missing files during bootstrap. Never overwrite existing project
content automatically. Before renaming, moving, merging, or deleting wiki files,
check references, preserve meaningful history, and confirm destructive changes.
<!-- lliki:managed:end id=wiki-rules -->
