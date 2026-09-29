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
- **Status:** Superseded by DEC-005 (dashboard replaced by tasks-index and resume)
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

## DEC-005: Named Folder Indexes as Mandatory Wiki Collection Nodes

- **Date:** 2026-09-29
- **Status:** Accepted
- **Context:** 0.3 indexes (`index.md`, `dashboard.md`) were ambiguous across
  folders, mixed routing with generated state, and gave agents no bounded entry
  point per collection.
- **Options considered:** Keep generic `index.md` per folder; one global
  generated dashboard; named `<folder>-index.md` collection nodes with a
  separate lean `resume.md` execution route.
- **Decision:** Every `wiki/` directory owns a `<folder>-index.md` generated in
  a managed `folder-index` region (references-only, recursive, LLM-free);
  `wiki/index.md` is renamed `wiki/wiki-index.md`; `dashboard.md` is superseded
  by `tasks-index.md` (collection) + `resume.md` (route that never
  auto-selects the next task).
- **Consequences:** Obsidian graph and agent routing share one deterministic
  hierarchy; migration renames preserve manual content and are idempotent;
  doctor enforces the contract via WIKI001-007.
- **Evidence:** `src/lliki/core/indexing.py`, `src/lliki/core/migration.py`,
  `wiki/tasks/LLIKI-040..043`, 44/44 unittest pass, doctor 0/0 on this repo.
- **Related tasks:** [[tasks/LLIKI-040-information-architecture]]
- **Superseded aspect:** the separate `resume.md` execution route was retired
  by DEC-007; the named-folder index contract remains accepted.

## DEC-006: Keep a Small Scratchpad Checkpoint Alongside Raw Provenance

- **Date:** 2026-09-29
- **Status:** Accepted
- **Context:** Raw session capture was proposed as a replacement for the local scratchpad; session dumps do not provide a cheap, current next-action route.
- **Options considered:** Remove scratchpad in favor of raw sessions; retain verbose handover sections; retain a minimal local checkpoint.
- **Decision:** Keep `wiki/tasks/scratchpad.md` ignored and limited to task, current state, next action, and blocker. Raw session capture, if implemented, adds provenance rather than replacing handover.
- **Consequences:** Existing context routing and hooks remain valid; fresh templates and doctor accept the compact form while old scratchpads remain readable. Raw capture remains future work.
- **Evidence:** `src/lliki/templates/wiki/tasks/scratchpad.md`, `src/lliki/core/doctor.py`, `tests/test_lliki.py`.
- **Related tasks:** [[tasks/LLIKI-005-task-scratchpad-path]]

## DEC-007: Retire resume.md; Tasks Index Is the Single Execution Entry

- **Date:** 2026-09-29
- **Status:** Accepted
- **Context:** `resume.md` only mirrored scratchpad-selected state while costing a second generator, doctor checks, and refresh plumbing; the contract already declares the scratchpad the single handover source.
- **Options considered:** Keep two files; fold current-task route into `tasks-index.md`; drop the rendered route entirely and rely on the scratchpad.
- **Decision:** Delete `resume.md` and the `resume-route` generator. `tasks-index.md` gains a generated `## Current Task` region (scratchpad-selected task or None, plus scratchpad link). The transition rule survives as one sentence in `wiki-rules.md`.
- **Consequences:** One generated execution file; doctor stale-index check covers route drift for free; existing `resume.md` files migrate to `wiki/tasks/.backup/`; legacy-path check flags leftovers.
- **Evidence:** `src/lliki/core/indexing.py`, `src/lliki/core/migration.py`, `tests/test_lliki.py`, [[tasks/LLIKI-050-retire-resume]].
- **Related tasks:** [[tasks/LLIKI-050-retire-resume]], supersedes DEC-005 resume route

## DEC-008: Bare `lliki` Is a Read-Only Command Overview

- **Date:** 2026-09-29
- **Status:** Accepted
- **Context:** Bare `lliki` silently aliased to `init` and jumped into the setup TUI, hiding other commands and risking unintended writes.
- **Options considered:** Keep init alias; landing screen with setup still prompting; landing screen that exits.
- **Decision:** Bare `lliki` prints welcome plus a common-commands panel (init, update, doctor, index, tasks, context, prompt) and exits without writing; `lliki --help` lists all commands; setup runs only via `lliki init`. Panel help text is derived from the argparse subparsers (single source of truth).
- **Consequences:** One-time workflow change for users expecting bare-lliki setup; safer non-interactive behavior; tests guard no-write startup.
- **Evidence:** `src/lliki/cli.py`, `src/lliki/branding.py`, `tests/test_lliki.py::test_bare_lliki_shows_command_overview_without_writing`.
- **Related tasks:** [[tasks/LLIKI-052-landing-overview]]

## DEC-009: Compact Command Surface; Bare Commands Perform Their Default Action

- **Date:** 2026-09-29
- **Status:** Accepted
- **Context:** The surface carried deprecated stubs (`state`, `--runtime`, `--scratchpad`, `--update-index`), mandatory subcommands for single-action verbs, an `inspect` CLI duplicating doctor's read-only role, and `hook` as a top-level command only agents invoke.
- **Options considered:** Keep the 0.3 surface for familiarity; delete deprecated stubs and simplify; alias everything to `doctor`.
- **Decision:** Remove deprecated commands and flags outright (0.4 unreleased, no compat duty). Bare `tasks` refreshes the tasks index, bare `index` refreshes all folder indexes, bare `integration` shows status. `inspect` is deleted; `doctor --json` carries `inspection.locations/signals`. `hook` becomes `lliki integration hook` with a rewrite alias for installed settings.json.
- **Consequences:** 14 visible top-level commands with consistent verb-first ergonomics; agent installers emit the canonical hook path; old settings files keep working via the alias.
- **Evidence:** `src/lliki/cli.py`, `tests/test_lliki.py`, `tests/test_cli_subprocess.py` (51/51 pass).
- **Related tasks:** [[tasks/LLIKI-053-command-surface]]
