# Implementation Checkpoints

## 1. Continuity Model

Completed: `wiki/tasks/scratchpad.md` provides ignored local handover for
resuming active LLM-assisted work after context loss, compaction, or session
switches.

## 2. Low-Token Routing

Completed: `wiki/index.md` is the new-work knowledge map,
`wiki/tasks/dashboard.md` is the compact current-work routing index, and agents
are instructed to avoid whole-wiki and whole-repository reads.

## 3. Durable Knowledge Promotion

Completed: decisions, lessons, maintained docs, task files, and scratchpad
state have separate roles so valuable engineering knowledge is preserved
without turning every task into a transcript.

## 4. Editable Templates

Completed: all generated Markdown and LLM prompts live under
`src/lliki/templates/`; export, validation, diff, and managed sync are
available.

## 5. Setup Experience

Completed: simple default setup and progressive custom setup. The shared
`wiki/` root and ignored scratchpad are default behavior; hooks and integrations
remain opt-in and repository-local.

## 6. Deterministic Maintenance

Completed: managed-section patching, task dashboard generation, bounded context
routing, safe decision/lesson append operations, structural doctor checks, and
existing-wiki update orchestration.

## 7. Distribution

Completed: Python package and wheel, pipx installers, packaging metadata, and
GitHub Actions CI/release workflows.

## 8. Verification

Completed: unit/integration tests, syntax validation, wheel install and
execution smoke tests, idempotency checks, template export and override checks,
and release workflow validation.
