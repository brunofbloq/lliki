---
id: initialize-project
title: Initialize project wiki
expected_total_tokens: 3000-7000
---
Review this repository and initialize its project wiki.

1. Read `CLAUDE.md` and `wiki/wiki-rules.md`.
2. Read `wiki/wiki-index.md` as the new-work project context entry point.
3. Inspect the repository selectively. Do not recursively load the entire repository.
4. Update:
   - `wiki/wiki-index.md`
   - `wiki/docs/project-overview.md`
   - `wiki/docs/development-workflow.md`
   - `wiki/docs/repository-rules.md`
   - `wiki/tasks/scratchpad.md` only if active handover state is needed
5. Keep `CLAUDE.md` stable and project-neutral.
6. Store durable project-specific information under maintained `wiki/` pages and
   temporary active handover in `wiki/tasks/scratchpad.md`.
7. Do not invent missing facts. Use `Unknown`, `TBD`, or `Needs validation`.
8. Preserve existing content unless it is clearly obsolete or contradictory.
9. Report unresolved assumptions and the evidence used for the initialization.
