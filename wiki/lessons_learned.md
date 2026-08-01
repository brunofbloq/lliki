# Lessons Learned

Record only confirmed, reusable, and non-obvious findings.

## LL-003: PowerShell UTF-8 Writes Can Add BOMs That Break Front Matter

- **Date:** 2026-08-01
- **Observed behavior:** After a mechanical Markdown path replacement, prompt
  loading failed with `Prompt template is missing front matter`.
- **Root cause:** PowerShell `Set-Content -Encoding UTF8` wrote BOM-prefixed
  files, so prompt front matter no longer began with `---`.
- **Resolution:** Rewrote touched Markdown files as UTF-8 without BOM.
- **Prevention:** For mechanical edits to prompt/template Markdown on Windows,
  use a no-BOM UTF-8 writer or `apply_patch`, then run prompt/template
  validation.
- **Evidence:** `src/lliki/templates/prompts/*.md`, `python -m unittest
  discover -s tests -v`, `python -m lliki templates validate`.
- **Related tasks:** [[tasks/LLIKI-005-task-scratchpad-path]]

## LL-002: Completed Tasks Still Need Durable Wiki Promotion

- **Date:** 2026-08-01
- **Observed behavior:** LLIKI-004 implementation completed and validation
  passed, but durable records were not immediately promoted into
  `wiki/decisions.md`, `wiki/lessons_learned.md`, and the task evidence.
- **Root cause:** The execution focused on code and validation closure before
  applying the promotion workflow from `wiki/wiki-rules.md`.
- **Resolution:** Add explicit task evidence, record accepted decisions, and
  capture this reusable process lesson.
- **Prevention:** At task completion, always check whether decisions, lessons,
  task evidence, dashboard refresh, and scratchpad reset are required before
  final reporting.
- **Evidence:** [[tasks/LLIKI-004-update-command]], `wiki/wiki-rules.md`.

## LL-001: Windows Console Encoding Can Break Unicode CLI Output

- **Date:** 2026-07-31
- **Observed behavior:** `lliki init` and prompt-printing subprocess tests failed on Windows with `charmap` encode/decode errors when output included Unicode characters.
- **Root cause:** The local Windows console/pipe defaulted to a non-UTF-8 code page, while Lliki templates and prompts contain Unicode punctuation and box-drawing characters.
- **Resolution:** Configure CLI stdio with replacement error handling at startup, and read generated UTF-8 files explicitly in tests.
- **Prevention:** When adding CLI output or tests that touch generated Markdown, keep Windows code-page behavior in mind and use explicit UTF-8 file reads.
- **Evidence:** `python -m unittest discover -s tests -v` initially failed on encoding errors and passed after the fix.

<!--
## LL-001: Lesson title

- **Date:** YYYY-MM-DD
- **Observed behavior:** What happened
- **Root cause:** Confirmed cause
- **Resolution:** What fixed or mitigated it
- **Prevention:** What should be done differently next time
- **Evidence:** Logs, measurements, code, test, or specification references
- **Related tasks:** [[tasks/task-file]]
-->
