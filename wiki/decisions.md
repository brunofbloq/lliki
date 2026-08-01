# Architecture Decision Log

This file is append-only. Supersede decisions; do not erase history.

## DEC-001: Add `lliki update` as the Existing-Wiki Migration Entry Point

- **Date:** 2026-08-01
- **Status:** Accepted
- **Context:** Existing repositories can lag behind the installed Lliki template
  model and may still contain legacy `.lliki/` state or mutable
  `wiki/index.md` sections.
- **Options considered:** Keep documenting a multi-command update sequence;
  make `lliki init` responsible for migration; add a dedicated deterministic
  `lliki update` command.
- **Decision:** Add `lliki update` as the human-first deterministic migration
  command. It applies only safe mechanical updates and reports semantic
  migration work instead of rewriting user-authored wiki content.
- **Consequences:** Existing repos have one recommended migration command;
  semantic conversion remains a human/LLM responsibility; `--json` remains
  available for agents and scripts.
- **Evidence:** `src/lliki/core/update.py`, `src/lliki/cli.py`,
  `tests/test_lliki.py`, `tests/test_cli_subprocess.py`.
- **Related tasks:** [[tasks/LLIKI-004-update-command]]

## DEC-002: Include a Baseline Git Commit in Task Specs

- **Date:** 2026-08-01
- **Status:** Accepted
- **Context:** A task may rely on the exact source state that existed when it
  was created or planned.
- **Options considered:** Rely on task creation date only; ask agents to infer
  baseline from Git history; record an explicit baseline commit in task
  metadata.
- **Decision:** New implementation tasks should include a baseline Git commit
  reference, preferably in front matter as `baseline_commit`.
- **Consequences:** Agents can detect staleness and reason about whether the
  task was written against the current code state.
- **Evidence:** Current LLIKI-004 task updated with
  `baseline_commit: 6b29cd75412d13a978478cda30895f2b27854854`.
- **Related tasks:** [[tasks/LLIKI-004-update-command]]

## DEC-003: Store Active Scratchpad Under `wiki/tasks/`

- **Date:** 2026-08-01
- **Status:** Accepted
- **Context:** The scratchpad is local handover/debug context for active task
  execution, not durable project knowledge.
- **Options considered:** Keep `wiki/scratchpad.md`; remove scratchpad
  entirely; move it under `wiki/tasks/scratchpad.md`.
- **Decision:** Use `wiki/tasks/scratchpad.md` as the canonical local
  scratchpad path and ignore `/wiki/tasks/scratchpad.md` in Git.
- **Consequences:** The knowledge map stays durable and cleaner; task execution
  state lives beside task files; legacy `wiki/scratchpad.md` is preserved and
  reported for manual migration.
- **Evidence:** `src/lliki/core/paths.py`, `src/lliki/core/gitignore.py`,
  `src/lliki/core/context.py`, `src/lliki/core/doctor.py`,
  `tests/test_lliki.py`.
- **Related tasks:** [[tasks/LLIKI-005-task-scratchpad-path]]

## DEC-004: Keep Task Routing Token-Cheap

- **Date:** 2026-08-01
- **Status:** Accepted
- **Context:** Task routing should stay cheap for agents and friendly to
  concurrent work.
- **Options considered:** Keep completed history in `dashboard.md`; add a
  task archive folder; keep the dashboard focused on current routing only.
- **Decision:** Generate a compact dashboard with active, blocked, and planned
  tasks only. Store dashboard backups in `wiki/tasks/.backup/`, keep temporary
  execution progress in `wiki/tasks/scratchpad.md`, and keep durable history in
  decisions, lessons, and concise completed task results.
- **Consequences:** Agents read less task history by default; completed tasks
  remain available directly; backup files no longer pollute task navigation.
- **Related tasks:** [[tasks/LLIKI-006-token-cheap-task-workflow]]

<!--
## DEC-001: Decision title

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Rejected | Superseded
- **Context:** Why a decision was required
- **Options considered:** Alternatives evaluated
- **Decision:** What was decided
- **Consequences:** Benefits, costs, constraints, and follow-up work
- **Evidence:** Datasheet, measurement, code, test, or analysis references
- **Related tasks:** [[tasks/task-file]]
-->
