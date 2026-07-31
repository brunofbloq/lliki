---
name: lliki
description: Maintain the repository project wiki efficiently after meaningful task events and completed user requests. Use for task routing, focused context updates, decisions, lessons, documentation synchronization, or wiki health checks.
---

<!-- lliki:managed:start id=claude-lliki-skill -->
# Lliki Workflow

1. Start from `wiki/index.md`; do not load the whole wiki.
2. Follow the active task and only its relevant links.
3. During implementation, update permanent wiki content only after meaningful
   task events, not after every command.
4. At the end of a completed request, determine whether project truth, task
   status, a decision, a reusable lesson, or maintained documentation changed.
5. Make focused edits only. Do not rewrite unrelated files.
6. Use `lliki inspect --json`, `lliki doctor --json`, and
   `lliki tasks refresh` when they are cheaper than manual inspection.
7. Temporary runtime state or scratch material is optional and non-authoritative.
8. Never claim validation that was not performed.

If `.lliki/state.json` exists, keep it concise and update it only for task
changes, interruption/resumption, or meaningful next-action changes. If optional
`.lliki/scratchpad.md` exists, use it only for difficult debugging, distill
confirmed outcomes into the wiki, and clear temporary noise when finished.

<!-- lliki:managed:end id=claude-lliki-skill -->
