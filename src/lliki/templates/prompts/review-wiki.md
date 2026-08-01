---
id: review-wiki
title: Semantic wiki lint
expected_total_tokens: 3000-10000
---
Review the project wiki for semantic consistency, freshness, evidence quality,
and information placement. This is the LLM semantic-lint workflow; deterministic
structure checks belong to `lliki doctor`.

1. If resuming active local work, read `wiki/tasks/scratchpad.md` first. Otherwise
   start from `wiki/index.md`.
2. Read `wiki/wiki-rules.md` and only the relevant wiki pages.
3. Verify implementation-sensitive claims against source code, tests,
   configuration, specifications, Git evidence, or task evidence where
   relevant.
4. Find contradictions, stale claims, duplicated authoritative descriptions,
   incorrect information placement, unsupported decisions or lessons, orphaned
   conclusions, exploratory claims presented as validated truth, and completed
   task conclusions that were never promoted.
5. Distinguish corrections supported by evidence from items requiring human
   validation.
6. Make only focused, evidence-supported corrections. Do not perform an
   unbounded whole-wiki rewrite or formatting sweep.
7. Do not treat local scratchpad claims as durable truth unless independently
   validated.
8. Report changed files, evidence used, unresolved contradictions, and deferred
   validation.
