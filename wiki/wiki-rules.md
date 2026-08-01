<!-- lliki:managed:start id=wiki-rules -->
# Wiki Rules

The wiki is derived project knowledge. Repository files, tests, generated
configuration, accepted specifications, and explicit task instructions are the
evidence layer. The root agent contract defines stable agent behavior; this
file defines how project knowledge moves through the wiki.

## Entry Points

- Resume active local work from `wiki/tasks/scratchpad.md` when it identifies an
  active task.
- Start new work or switch workstreams from `wiki/index.md`.
- Use `wiki/tasks/dashboard.md` for task navigation and overall status.
- Read only the pages and repository files relevant to the request.

## Information Placement

Each piece of project knowledge should have one authoritative home.

- Current validated project behavior belongs in `wiki/docs/`.
- Unresolved analysis belongs in `wiki/exploratory/`.
- Work definition and overall task status belong in `wiki/tasks/`.
- Accepted rationale belongs in `wiki/decisions.md`.
- Confirmed reusable findings belong in `wiki/lessons_learned.md`.
- Temporary active execution and handover context belongs in
  `wiki/tasks/scratchpad.md`.

Reference existing knowledge with links instead of copying it into multiple
files.

## Ingest Workflow

Use when authoritative evidence enters the repository: requirements, code or
architecture changes, specifications, errata, completed investigations,
incidents, measurements, test reports, or accepted external constraints.

1. Identify the authoritative source and its scope.
2. Search the existing wiki before creating a new page.
3. Update the one maintained location for each affected fact.
4. Preserve useful source references and validation evidence.
5. Identify contradictions with existing docs, decisions, lessons, or tasks.
6. Update links and indexes only when navigation changed.
7. Do not copy source content wholesale into the wiki.
8. Mark unresolved conclusions as exploratory or `Needs validation`.

## Query Workflow

Use for normal engineering and coding requests.

1. Resume from `wiki/tasks/scratchpad.md` when local active work exists.
2. Otherwise start from `wiki/index.md`.
3. Read only relevant wiki pages.
4. Verify implementation-sensitive claims against current source code, tests,
   configuration, Git state, or authoritative specifications.
5. Perform the requested work.
6. Record current handover details only in the scratchpad.
7. Promote only validated durable conclusions.
8. Do not update the wiki merely because files were read or commands were run.

## Scratchpad Workflow

`wiki/tasks/scratchpad.md` is local, ignored, non-authoritative, bounded
handover/debug context. It supports one active task and one writing agent per
worktree. Parallel tasks should use separate worktrees.

Keep at most:

- one active task;
- one concrete next action;
- five confirmed outcomes;
- three active blockers;
- eight focus paths or symbols;
- five remaining validation items.

Do not store terminal transcripts, full command output, copied task
specifications, obsolete blockers, obsolete next actions, raw reasoning, copied
chat, or chronological checkpoint history. Append during active debugging only
when the checkpoint, confirmed outcome, blocker, validation state, focus, next
action, or handover state changes materially. Compact stale details when it
grows and reset it after completion.

## Lint Workflow

Deterministic structural lint is owned by `lliki doctor`. It checks local files
without an LLM, network service, credential, vector store, or embedding system.

Semantic lint is owned by the `review-wiki` prompt. It checks meaning,
freshness, contradictions, evidence, and information placement. Semantic lint
must make focused evidence-supported corrections and must not rewrite the whole
wiki.

## Promotion Workflow

Use at task completion or when a conclusion becomes durable.

1. Verify acceptance criteria and validation evidence.
2. Update the task's overall status and concise final result.
3. Promote accepted rationale to `wiki/decisions.md` only when a real decision
   was made.
4. Promote reusable confirmed findings to `wiki/lessons_learned.md`.
5. Update `wiki/docs/` only when current validated project behavior changed.
6. Resolve or clearly mark affected exploratory material.
7. Refresh the generated task dashboard when task metadata changed.
8. Reset `wiki/tasks/scratchpad.md` to its inactive template.
9. Do not copy scratchpad history into the completed task.

## Provenance

For implementation-sensitive or high-impact claims, preserve enough evidence to
recheck the claim. Use lightweight references such as:

```markdown
## Evidence

- Source: `src/...`
- Tests: `tests/...`
- Requirement: `TASK-123` or external specification
- Validated against commit: `abc1234`
- Last reviewed: 2026-08-01
```

Do not require every page to contain every field. Prefer links and exact paths
over copied source text.

## Staleness

- A wiki statement is not authoritative merely because it is newer.
- Verify implementation-sensitive claims against source, tests, configuration,
  or specifications.
- When a page is suspected stale, mark the affected statement or section rather
  than invalidating unrelated content.
- Use `Needs validation` when evidence is incomplete.
- Update `Last reviewed` only after a real evidence-backed review.
- Never create timestamp-only edits.
- Scratchpad snapshots are hints for staleness detection, not authority.

## Contradictions

Use this authority order and do not silently discard material contradictions:

1. Applicable safety, security, and legal constraints.
2. Explicit instructions for the current task.
3. Reproducible measurements and approved hardware evidence.
4. Exact-part authoritative specifications, schematics, and errata.
5. Source code, generated configuration, build configuration, and linker data.
6. Accepted decisions and maintained documentation.
7. Active tasks and confirmed lessons.
8. Exploratory material.
9. Local scratchpad handover.
10. Generic model or skill knowledge.

When claims conflict, identify the conflicting claims and evidence, prefer the
higher-authority evidence when resolvable, correct the maintained page instead
of creating a parallel conflicting page, mark replaced decisions as superseded,
and preserve unresolved conflicts with the evidence required to resolve them.
<!-- lliki:managed:end id=wiki-rules -->
