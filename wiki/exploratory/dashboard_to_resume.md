Keep the existing file count and rename:

```text
wiki/tasks/dashboard.md
```

to:

```text
wiki/tasks/resume.md
```

Its role becomes a **lean execution entry point**, not a Kanban board.

## Final responsibility

`resume.md` answers only:

1. What task should the LLM work on now?
2. Where is the active scratchpad?
3. What task may follow?
4. Under what condition may the next task begin?

It should not contain:

* backlog;
* full task status lists;
* priority;
* sprint;
* owner;
* detailed acceptance criteria;
* debugging history;
* duplicated task requirements.

Those remain in the linked task files, external project-management tools, and `scratchpad.md`.

## Recommended structure

```markdown
# Resume

> Execution entry point for coding agents.
> Read the current task and its scratchpad first.
> Do not start the possible next task unless its transition rule is satisfied.

## Current Task

- **Task:** [[HWRD-115-can-fd-protocol|HWRD-115 — CAN-FD Protocol]]
- **Scratchpad:** [[scratchpad|Active Task Scratchpad]]

Resume from the latest meaningful checkpoint in the scratchpad.

## Possibly Next Task

- **Task:** [[HWRD-118-can-integration-validation|HWRD-118 — CAN Integration Validation]]

### Transition Rule

Start the possible next task only when the current task:

- satisfies its acceptance criteria;
- passes its required validation;
- has no unresolved blocking issue;
- records a final result in the task file.

If the current task fails or becomes blocked:

1. update `[[scratchpad|Active Task Scratchpad]]`;
2. stop the execution sequence;
3. report the blocker;
4. do not start the possible next task.
```

## Obsidian linking

Because `resume.md`, `scratchpad.md`, and task files live in the same directory:

```text
wiki/tasks/
├── resume.md
├── scratchpad.md
├── HWRD-115-can-fd-protocol.md
└── HWRD-118-can-integration-validation.md
```

Use simple Obsidian links:

```markdown
[[scratchpad]]
[[HWRD-115-can-fd-protocol]]
[[HWRD-118-can-integration-validation]]
```

Aliases improve readability:

```markdown
[[scratchpad|Active Task Scratchpad]]
[[HWRD-115-can-fd-protocol|HWRD-115 — CAN-FD Protocol]]
```

The underlying link remains stable even when the visible title is longer.

## Empty states

When no task is active:

```markdown
# Resume

## Current Task

- None.

## Possibly Next Task

- None.
```

When a current task exists but no next task is planned:

```markdown
## Possibly Next Task

- None.

No task should be selected automatically after the current task completes.
```

This avoids the LLM guessing what to do next.

## Multiple-task prompts

This supports a concise user instruction such as:

> Follow `wiki/tasks/resume.md`. Complete the current task and, only if its transition rule is satisfied, continue with the possible next task.

The LLM then follows:

```text
resume.md
    ↓
current task
    ↓
scratchpad
    ↓
implementation and validation
    ↓
transition rule
    ├── satisfied → possible next task
    └── not satisfied → stop and report
```

## Relationship with `scratchpad.md`

`resume.md` should contain only routing and sequencing.

`scratchpad.md` contains:

* current checkpoint;
* confirmed findings;
* debugging experiments;
* blockers;
* focused files;
* next implementation action.

Do not copy scratchpad content into `resume.md`.

The current task reference is intentionally present in both, but for different purposes:

```text
resume.md
    declares which task is selected

scratchpad.md
    records the local implementation state of that selected task
```

The doctor should verify that both reference the same task.

## Generated versus manually maintained

The current `dashboard.md` is mechanically generated from all task front matter. After renaming it to `resume.md`, that behavior should change.

`resume.md` should no longer list every active, blocked, planned, and completed task. It should render only:

* zero or one current task;
* the scratchpad link;
* zero or one possible next task;
* the standard transition rule.

The selected task references could be stored in a small managed section or inferred from explicit metadata, but the file must remain human-editable and Obsidian-friendly.

A good managed structure is:

```markdown
# Resume

<!-- lliki:generated:start id=resume-route -->
## Current Task

- **Task:** [[HWRD-115-can-fd-protocol|HWRD-115 — CAN-FD Protocol]]
- **Scratchpad:** [[scratchpad|Active Task Scratchpad]]

## Possibly Next Task

- **Task:** [[HWRD-118-can-integration-validation|HWRD-118 — CAN Integration Validation]]

### Transition Rule

Start the possible next task only after the current task satisfies its
acceptance criteria, passes required validation, has no unresolved blocker,
and records its final result.
<!-- lliki:generated:end id=resume-route -->
```

This allows Lliki to update the route without rewriting surrounding user content.

## Required implementation consequences

The implementation task should now specify:

* rename the template and target from `wiki/tasks/dashboard.md` to `wiki/tasks/resume.md`;
* migrate an existing managed `dashboard.md` safely;
* stop generating active/blocked/planned/completed task groups;
* remove `--update-index`;
* update `lliki tasks refresh` to maintain the resume route rather than a Kanban view;
* update `lliki context` to read `resume.md` and `scratchpad.md`;
* update all agent templates and prompts from `dashboard.md` to `resume.md`;
* update the default tree, README, design documentation, tests, and examples;
* ensure task discovery explicitly excludes both `resume.md` and `scratchpad.md`;
* validate that Current Task and Possibly Next Task reference existing task files;
* validate that Current Task matches the task referenced by the scratchpad;
* allow no next task;
* never automatically choose a next task based on priority or filename;
* preserve Obsidian `[[wiki links]]`.

The resulting structure remains minimal:

```text
wiki/tasks/
├── resume.md
├── scratchpad.md
└── <task>.md
```

That is cleaner than adding `workspace.md`, `state.md`, or another execution-routing file.
