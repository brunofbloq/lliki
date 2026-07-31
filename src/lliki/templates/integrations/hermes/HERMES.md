<!-- lliki:managed:start id=hermes-agent-contract -->
# Hermes Repository Instructions

Read and follow `CLAUDE.md` as the stable repository contract. Use `wiki/index.md` as the only mandatory dynamic project entry point. Follow
only the links needed for the current request and use `wiki/wiki-rules.md` when
maintaining project knowledge.

Review wiki updates after meaningful task events and at the end of completed
user requests. Make focused semantic updates only when durable project truth
changed. Use the local `lliki` CLI for mechanical inspection, validation,
or task-dashboard refresh when efficient.

Do not require the user to run lliki commands during normal work.

If `.lliki/state.json` exists, keep it concise and update it only for task
changes, interruption/resumption, or meaningful next-action changes. If optional
`.lliki/scratchpad.md` exists, use it only for difficult debugging, distill
confirmed outcomes into the wiki, and clear temporary noise when finished.

<!-- lliki:managed:end id=hermes-agent-contract -->
