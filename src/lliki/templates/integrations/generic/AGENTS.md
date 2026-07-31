<!-- lliki:managed:start id=generic-agent-contract -->
# Repository Agent Instructions

Read and follow `CLAUDE.md` as the stable repository contract. Read `wiki/index.md` first, then follow only the links relevant to the current
request. Follow `wiki/wiki-rules.md` when maintaining project knowledge.

Review wiki updates after meaningful task events and at the end of completed
user requests. Update only durable project knowledge that changed; do not edit
permanent wiki files after every command.

Use the `lliki` CLI internally for mechanical inspection, validation,
template synchronization, or task-dashboard refresh when it is available. The
user should not need to invoke it during normal development.

Project-specific commands and modification boundaries belong under `wiki/docs/`,
not in this file.

If `.lliki/state.json` exists, keep it concise and update it only for task
changes, interruption/resumption, or meaningful next-action changes. If optional
`.lliki/scratchpad.md` exists, use it only for difficult debugging, distill
confirmed outcomes into the wiki, and clear temporary noise when finished.

<!-- lliki:managed:end id=generic-agent-contract -->
