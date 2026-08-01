---
name: lliki
description: Maintain the repository project wiki efficiently after meaningful task events and completed user requests. Use for task routing, focused context updates, decisions, lessons, documentation synchronization, or wiki health checks.
---

<!-- lliki:managed:start id=claude-lliki-skill -->
# Lliki Workflow

1. Read `CLAUDE.md` as the stable repository contract.
2. When resuming active local work, read `wiki/tasks/scratchpad.md` first.
3. If the scratchpad names an active task, read that task, verify the snapshot,
   load only relevant focus files, and continue from the next action.
4. For new work or workstream switches, start from `wiki/index.md`.
5. During implementation, update durable wiki content only after meaningful
   task events, not after every command.
6. Use `wiki/tasks/scratchpad.md` as the only local handover file; keep it bounded
   and overwrite obsolete content.
7. At task completion, update final task status, promote durable knowledge,
   refresh the dashboard when needed, and reset the scratchpad.
8. Use `lliki inspect --json`, `lliki context --json`, `lliki doctor --json`,
   and `lliki tasks refresh` when they are cheaper than manual inspection.
9. Never claim validation that was not performed.
<!-- lliki:managed:end id=claude-lliki-skill -->
