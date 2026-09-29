# Plan: update prompt templates and wire all tasks into the tasks index

Saved to: `.hermes/plans/2026-09-29_120500-update-prompts-and-task-links.md`

## Goal

Update Lliki’s prompt templates and the prompt-loading code to reflect the current feature set, remove the embedded-systems-architect skill reminder from the relevant prompt, and make every task file in `wiki/tasks/` reachable from `wiki/tasks/tasks-index.md`.

## Current context / assumptions

- Code under review: `src/lliki/core/prompts.py` and `src/lliki/templates/prompts/*.md`.
- Current prompt files: `complete-task.md`, `explore-impact.md`, `initialize-project.md`, `migrate-legacy.md`, `review-wiki.md`.
- Current tasks indexed in `wiki/tasks/tasks-index.md`: LLIKI-004, 005, 006, 040–049, plus RELEASE-001 and the active LLIKI-048. The index already has an `Active`, `Blocked`, `Planned`, and `Closed` structure.
- The ask references “all tasks” and “software-architecture-strategist” as the complete set to link. I am assuming that means every task card currently inside `wiki/tasks/`, not only the software-architecture-strategist -related ones, unless told otherwise.
- I am not changing `src/lliki/core/prompts.py` signatures unless the template updates require it; if they do, the plan will note it explicitly.
- Hermit-style change discipline: small edits, each independently checkable, no speculative feature work.

## Architecture / proposed approach

Do this as a narrow editorial pass, not a rewrite:

1. Read every prompt file and `prompts.py` first, without editing.
2. Decide which prompt(s) are stale relative to the current feature set.
3. Update only the wording that is actually wrong or incomplete, keeping each template’s existing structure and front matter.
4. If any prompt needs a new section or new instruction, add it only where it serves an already-implemented feature.
5. Remove the embedded-systems-architect skill reference from whichever prompt currently contains it. If it shows up in more than one place, remove it from all of them.
6. Make `tasks-index.md` contain one link per task file in `wiki/tasks/`. If a task is already linked, leave it. If a task is missing, add it under the correct status section.
7. After edits, regenerate or at least sanity-check the index so the manual links do not conflict with the generated section.

## Step-by-step tasks

### Task 1 — Inventory current prompts and current tasks

Files:
- `src/lliki/templates/prompts/complete-task.md`
- `src/lliki/templates/prompts/explore-impact.md`
- `src/lliki/templates/prompts/initialize-project.md`
- `src/lliki/templates/prompts/migrate-legacy.md`
- `src/lliki/templates/prompts/review-wiki.md`
- `src/lliki/core/prompts.py`
- `wiki/tasks/tasks-index.md`
- Every file matching `wiki/tasks/LLIKI-*.md` and `wiki/tasks/RELEASE-*.md`

Actions:
1. Read all five prompt files.
2. Read `src/lliki/core/prompts.py`.
3. Read `wiki/tasks/tasks-index.md`.
4. List every task file in `wiki/tasks/` and confirm which ones already appear in the index and which do not.

Expected outcome:
- A short list of prompt files that mention embedded-systems-architect, if any.
- A short list of task files not yet linked from the index.

Verification:
- No edits yet. This task ends when the missing-link list and the skill-reference list are known.

### Task 2 — Remove the embedded-systems-architect skill reference

Candidate files:
- Any prompt file that currently says something like “Inspect the embedded-systems-architect skill if it is available.”

Actions:
1. Search the prompt files for the exact phrase or anything close to it.
2. Remove the sentence or line.
3. If removal leaves an awkward bullet or empty section, trim the surrounding line only enough to keep the prompt readable.

Do not:
- Rewrite the whole prompt to get rid of one line.
- Add new guidance just because a line was removed.

Verification:
- Re-read the affected file and confirm the reference is gone.
- If the file uses front matter or a fixed structure, confirm it still parses as a valid prompt template.

### Task 3 — Update prompts for current features

Goal:
- Make the prompt text consistent with features that already exist, and remove or adjust any guidance that would send an agent toward an old or nonexistent workflow.

Files to consider:
- `complete-task.md`
- `review-wiki.md`
- Any prompt that currently describes task completion, validation, wiki checks, index usage, or release-related behavior.

Edit rules:
- Keep the existing prompt structure.
- Prefer concrete instruction changes over general tone changes.
- If a prompt already mentions the right behavior in a different section, do not duplicate it.
- If a prompt references a workflow that is no longer current, replace it with the current workflow only if the workflow is real and already implemented.

Verification:
- After editing, re-read each changed prompt and confirm the updated text is internally consistent.
- If `src/lliki/core/prompts.py` has any hardcoded expectations that would break with the new wording, adjust it at the same time and note why.

### Task 4 — Ensure every task is linked from `tasks-index.md`

Files:
- `wiki/tasks/tasks-index.md`
- All current task files in `wiki/tasks/`

Actions:
1. Determine the current full task list from the task files themselves, not from memory.
2. Compare that list against the links in `tasks-index.md`.
3. For each missing task, add a link in the appropriate section:
   - Active tasks under `## Active`
   - Blocked tasks under `## Blocked`
   - Planned tasks under `## Planned`
   - Completed/done tasks under `## Closed`
4. Prefer the existing index style for link text and formatting.

If the index is generated:
- If the generated section is authoritative and manual edits outside it are lost, then this task must update the generator/configuration that produces the index rather than editing the markdown directly.
- If manual links outside the generated markers are preserved, add the missing links only outside the generated region unless the generator already emits them.

Verification:
- Read the index back and confirm every known task file now has a corresponding link.
- Confirm no duplicate entries were introduced.

### Task 5 — Validate prompt loading and index coherence

Commands to run:
1. Load the prompts through the existing code path and confirm they still load without error.
2. If there is an existing `lliki` command that refreshes or validates the tasks index, run it and confirm it is happy with the updated index.
3. If no such command exists, at minimum re-read the index and confirm it is well-formed Markdown with no broken link syntax.

If any validation command exists in the repo, use that exact command here rather than inventing one.

## Tests / validation

Because this is mostly content work, the “tests” are mostly deterministic checks:

1. Prompt loading check
   - Expected: `src/lliki/core/prompts.py` or its current loading path returns all five prompts without raising.
   - Failure mode: a front-matter or parsing change breaks loading.

2. Index completeness check
   - Expected: every task file present under `wiki/tasks/` has a corresponding link in `wiki/tasks/tasks-index.md`.
   - Failure mode: a newly added task file is missing, or an existing link was accidentally removed.

3. Skill-reference removal check
   - Expected: no prompt file contains the embedded-systems-architect instruction.
   - Failure mode: the line was edited but not removed, or it was removed from one prompt but exists in another.

4. Format check
   - Expected: Markdown still renders cleanly, front matter still parses, and the index still has the same section structure.

## Risks, tradeoffs, and open questions

- Risk: editing prompts can subtly change agent behavior. Keep changes tight and avoid broad rewording unless the old wording is actually misleading.
- Risk: the index may be generated from code or metadata. If so, manual linking may be the wrong fix, and the correct fix is to update the index generator or task metadata instead.
- Open question: should the index link every task, or only tasks in certain status groups?
- Open question: is “all tasks” meant to include archived or release-oriented tasks too?
- Open question: does `prompts.py` need any code change, or only the Markdown templates?
- Open question: is the embedded-systems-architect reference in one prompt or several?

If any of those are decisive and I cannot answer them from the repo, the implementer should stop at the relevant inventory task and ask before editing.

## Next step after the plan

If this plan is approved, the next move is to execute it in small verifiable edits, starting with the inventory task, then the skill-reference removal, then the prompt updates, then the task-index linking, then the validation commands.
