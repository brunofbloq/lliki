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

## LL-004: Batch-generated Markdown Must Re-read Content Before Repair

- **Date:** 2026-09-29
- **Observed behavior:** Ten task cards generated in one batch carried wrong
  front-matter ids (`LLIKI-00..09`); a follow-up repair pass reported success
  yet the ids on disk were unchanged.
- **Root cause:** The repair computed the fix from the paginated read echo
  (line-number prefixes) instead of the file, so the patch matched nothing on
  disk while the in-memory string looked corrected; success was never read
  back.
- **Resolution:** Manual fix with exact on-disk strings and per-file
  verification after writing.
- **Prevention:** When batch-generating or auto-fixing files, assert each
  mutation against a fresh read of the target file, not against the generator's
  own in-memory copy.
- **Evidence:** `wiki/tasks/LLIKI-04*.md` front matter before/after
  2026-09-29; kanban card t_430e5733 scope 1.

## LL-005: A Clean Doctor Run Does Not Prove Task Reachability When Statuses Are Exempted

- **Date:** 2026-09-29
- **Observed behavior:** Completed task files, including LLIKI-044 and LLIKI-049, had no incoming task-index links while `lliki doctor` reported no warnings.
- **Root cause:** The generator filtered terminal-status tasks, and the orphan check exempted the same statuses, hiding unreachable documents.
- **Resolution:** Keep closed tasks in a compact ID-only `## Closed` index group and apply the normal orphan check to them.
- **Prevention:** Test document reachability across all status groups whenever index generation and doctor logic change together.
- **Evidence:** `src/lliki/core/indexing.py`, `src/lliki/core/doctor.py`, `tests/test_lliki.py::test_tasks_index_links_closed_tasks_without_routing_them_as_current`.
- **Related tasks:** [[tasks/LLIKI-042-index-generator]]

## LL-006: Default Semantic-Search Embedding Model Silently Destroys Code Recall

- **Date:** 2026-09-29
- **Observed behavior:** With cocoindex-code 0.2.41 default model (snowflake-arctic-embed-xs), every Python-targeted semantic query returned 1-line `__init__.py` stubs for all three top hits; docs search was fine. nomic-ai/CodeRankEmbed crashed on load (`NomicBertModel`/torch incompatibility in the pinned env).
- **Root cause:** Too-small general-purpose embedder for code; single-line chunks attract cosine noise. Recommended "better" code model incompatible with the tool's pinned sentence-transformers stack.
- **Resolution:** Snowflake/snowflake-arctic-embed-m (with `query_params.prompt_name: query`) restored correct top hits (migration/update code, matching tests, DEC/task docs) on CPU; full rebuild 86 files/463 chunks in ~150s, incremental edits reprocess exactly 1 unit.
- **Prevention:** On any semantic-search tool, benchmark 3-5 known-anchor queries before trusting results; never accept the default model for code-heavy repos.
- **Evidence:** `ccc doctor`/`ccc search` sessions 2026-09-29 on this repo; `~/.cocoindex_code/global_settings.yml`.
- **Related tasks:** LLIKI-051 (cocoindex experiment, spec section 28)
