# Lliki Next Version Plan

## Product direction

### Current Lliki

Lliki currently solves:

> Give humans and coding agents a small, durable, repository-local knowledge layer so they can recover context without repeatedly reading the repository.

The next version should extend this into:

> **A local engineering knowledge workspace that is simultaneously optimized for humans, Obsidian, CLI tools, and coding agents.**

Three principles should remain unchanged:

1. **Markdown remains the source of truth.**
2. **Agents should load references before content.**
3. **Lliki core should remain deterministic, local, cheap and LLM-independent.**

A fourth structural principle should be added:

4. **Every wiki folder is independently discoverable through its own named index.**

---

# 1. Target information architecture

Move toward the following standard structure:

```text
repo/
├── README.md
├── assets/
│   ├── lliki-logo.svg
│   ├── screenshots/
│   └── ...
│
├── wiki/
│   ├── wiki-index.md
│   ├── wiki-rules.md
│   ├── decisions.md
│   ├── lessons_learned.md
│   │
│   ├── docs/
│   │   ├── docs-index.md
│   │   ├── project-overview.md
│   │   ├── development-workflow.md
│   │   └── repository-rules.md
│   │
│   ├── tasks/
│   │   ├── tasks-index.md
│   │   ├── resume.md
│   │   ├── scratchpad.md
│   │   └── TASK-xxx.md
│   │
│   ├── exploratory/
│   │   ├── exploratory-index.md
│   │   └── *.md
│   │
│   └── notes/
│       ├── notes-index.md
│       └── *.md
│
└── ...
```

## Folder-index convention

Every directory inside `wiki/` MUST contain an index using:

```text
<folder-name>-index.md
```

Examples:

```text
wiki/wiki-index.md
wiki/docs/docs-index.md
wiki/tasks/tasks-index.md
wiki/exploratory/exploratory-index.md
wiki/notes/notes-index.md
```

If a future folder is created:

```text
wiki/research/
```

Lliki should create:

```text
wiki/research/research-index.md
```

automatically.

### Why named indexes instead of `index.md`

Using:

```text
notes-index.md
tasks-index.md
exploratory-index.md
```

instead of several files called simply `index.md` gives important benefits.

In Obsidian:

- open tabs are immediately identifiable;
- search results are less ambiguous;
- backlinks clearly show which domain index owns a document;
- graph view exposes explicit collection nodes;
- users can easily distinguish index documents from normal content.

For agents:

- paths communicate semantics without opening the file;
- folder relationships are explicit;
- indexes can act as bounded context entry points;
- deterministic graph extraction becomes easier.

The index therefore becomes a real **collection node** in the Lliki knowledge graph.

---

# 2. Indexes as graph nodes

Indexes should not merely exist for navigation.

They should create explicit relationships between a collection and its contents.

Conceptually:

```text
notes-index
   │
   ├── LINKS_TO → note-a
   ├── LINKS_TO → note-b
   └── LINKS_TO → note-c
```

Likewise:

```text
tasks-index
   │
   ├── LINKS_TO → TASK-001
   ├── LINKS_TO → TASK-002
   └── LINKS_TO → resume
```

This produces a useful hierarchy naturally from normal Markdown links:

```text
wiki-index
   │
   ├── docs-index
   ├── tasks-index
   ├── exploratory-index
   ├── notes-index
   ├── decisions
   └── lessons_learned
```

This structure works simultaneously for:

- humans;
- Obsidian;
- deterministic graph extraction;
- LLM context routing;
- future semantic indexing.

---

# 3. Indexes must be references-only

This is one of the most important token-efficiency rules.

Index files should answer:

> **What exists here and where should I go next?**

They should not duplicate the content of their children.

Example:

```markdown
# Exploratory Index

## Active

- [[camera-fov-investigation]]
- [[onnx-runtime-benchmark]]
- [[deposit-evidence-experiment]]

## Archived

- [[aws-rekognition-baseline]]
```

Optional lightweight metadata is acceptable:

```markdown
- [[camera-fov-investigation]] — vision / geometry
```

Avoid:

```markdown
- [[camera-fov-investigation]] — We investigated the camera geometry,
  tested several models, discovered that...
```

The authoritative content belongs in the linked document.

This prevents:

```text
source document
      +
index summary
      +
agent-generated summary
```

from becoming three drifting copies of the same knowledge.

---

# 4. Top-level `wiki-index.md`

Rename the current:

```text
wiki/index.md
```

to:

```text
wiki/wiki-index.md
```

The top-level index should be extremely stable and small.

Suggested structure:

```markdown
# Wiki Index

> Main knowledge map for this repository.

## Current Work

- [[tasks/tasks-index|Tasks]]
- [[tasks/resume|Resume Current Work]]

## Project Knowledge

- [[docs/docs-index|Documentation]]
- [[exploratory/exploratory-index|Exploratory Work]]
- [[notes/notes-index|Notes]]

## Durable Knowledge

- [[decisions|Decisions]]
- [[lessons_learned|Lessons Learned]]

## Wiki Operations

- [[wiki-rules|Wiki Rules]]
```

An agent starting new work should normally start at:

```text
wiki/wiki-index.md
```

An agent resuming active work should normally start at:

```text
wiki/tasks/resume.md
```

---

# 5. Rename `dashboard.md` → `resume.md`

## Problem

`dashboard.md` sounds like a reporting interface.

In practice the file is primarily an **agent navigation/resume mechanism**.

Rename:

```text
wiki/tasks/dashboard.md
```

to:

```text
wiki/tasks/resume.md
```

The task folder itself gets a separate collection index:

```text
wiki/tasks/tasks-index.md
```

This distinction is important.

### `tasks-index.md`

Answers:

```text
What tasks exist?
How are they grouped?
Which task documents can I navigate to?
```

### `resume.md`

Answers:

```text
What is currently active?
What is blocked?
What should I continue next?
```

Example `tasks-index.md`:

```markdown
# Tasks Index

## Active

- [[TASK-042-camera-pipeline]]

## Planned

- [[TASK-051-model-compression]]

## Completed

- [[TASK-031-onnx-evaluation]]

## Execution State

- [[resume|Current Work Resume]]
- [[scratchpad|Agent Scratchpad]]
```

Example `resume.md`:

```markdown
# Work Resume

## Active

- [[TASK-042-camera-pipeline]]
  - priority: high
  - updated: 2026-09-29

## Blocked

- None.

## Next

- [[TASK-051-model-compression]]
```

---

# 6. Deterministic folder index generation

Introduce:

```bash
lliki index refresh
```

Possible scopes:

```bash
lliki index refresh
lliki index refresh notes
lliki index refresh exploratory
lliki index refresh tasks
lliki index refresh docs
lliki index refresh --all
```

The command should enforce:

```text
folder/
    folder-index.md
```

Algorithm:

```text
scan wiki/
    ↓
discover directories
    ↓
ensure <folder>-index.md exists
    ↓
discover Markdown children
    ↓
read minimal metadata
    ↓
generate links
    ↓
update managed section
```

No LLM is required.

Only generated sections should be touched:

```markdown
<!-- lliki:generated:start id=folder-index -->

...

<!-- lliki:generated:end id=folder-index -->
```

Manual content outside the region remains untouched.

---

# 7. Recursive folder support

The index convention should work recursively.

Example:

```text
wiki/
└── research/
    ├── research-index.md
    │
    ├── vision/
    │   ├── vision-index.md
    │   ├── experiment-a.md
    │   └── experiment-b.md
    │
    └── hardware/
        ├── hardware-index.md
        └── benchmark.md
```

Then:

```text
research-index
   ├── vision-index
   └── hardware-index
```

and:

```text
vision-index
   ├── experiment-a
   └── experiment-b
```

This creates a natural hierarchical knowledge graph without requiring a database.

---

# 8. Parent-child relationships

When an index contains:

```markdown
- [[vision/vision-index|Vision]]
```

and the child index links:

```markdown
- [[experiment-a]]
- [[experiment-b]]
```

Lliki can later derive:

```text
research
   CONTAINS vision

vision
   CONTAINS experiment-a

vision
   CONTAINS experiment-b
```

even though the source of truth remains ordinary Markdown.

This is especially useful for future:

```bash
lliki knowledge query
```

operations.

---

# 9. First-class Notes

Create by default:

```text
wiki/notes/
wiki/notes/notes-index.md
```

Notes represent information that is useful but not yet:

- a task;
- a decision;
- an investigation;
- maintained documentation;
- a reusable lesson.

This fills an important gap in the current information model.

---

# 10. Notes CLI

Add:

```bash
lliki notes new
lliki notes list
lliki notes show
lliki notes write
lliki notes append
lliki notes search
```

Example:

```bash
lliki notes new "Toradex modem experiment"
```

creates:

```text
wiki/notes/2026-09-29-toradex-modem-experiment.md
```

and automatically refreshes:

```text
wiki/notes/notes-index.md
```

Possible metadata:

```yaml
---
type: note
created: 2026-09-29
updated: 2026-09-29
tags:
  - modem
---
```

---

# 11. Generic creation commands

Create one internal document factory supporting:

```bash
lliki task new
lliki notes new
lliki explore new
```

Potential later additions:

```bash
lliki decision new
lliki lesson new
```

Shared behavior:

```text
slug generator
frontmatter generator
date handling
template rendering
safe file creation
parent index refresh
```

Internally:

```python
create_document(
    kind="task",
    title="...",
    template="task.md",
)
```

After creating a document:

```text
create document
      ↓
identify parent folder
      ↓
refresh parent <folder>-index.md
```

---

# 12. Task templates

Add editable built-in templates:

```text
templates/content/
├── task.md
├── note.md
└── exploratory.md
```

Task example:

```markdown
---
id:
type: task
title:
status: planned
priority:
created:
updated:
---

# Goal

# Context

# Acceptance Criteria

# Implementation

# Validation

# Result
```

---

# 13. Obsidian compatibility

Obsidian compatibility should be a **format contract**, not an Obsidian dependency.

Use normal Markdown and wikilinks:

```markdown
[[docs/docs-index]]
[[notes/notes-index]]
[[tasks/TASK-042]]
```

Support YAML front matter:

```yaml
---
type: task
status: active
tags:
  - lliki
  - cli
---
```

Avoid depending on:

```text
Dataview
Templater
community plugins
Obsidian proprietary metadata
```

They may enhance the experience but cannot be required.

---

# 14. Why folder indexes improve Obsidian

Named folder indexes provide a clear map in both the file explorer and graph view.

For example:

```text
wiki-index
      │
      ▼
tasks-index
      │
      ├── TASK-001
      ├── TASK-002
      └── resume
```

Obsidian backlinks then naturally answer:

```text
Which collection references this object?
What other objects belong to this collection?
How is this document connected to the overall wiki?
```

The index files become intentional graph hubs.

---

# 15. README Obsidian section

Explain that users can open:

```text
repo/wiki/
```

directly as an Obsidian vault.

Document that:

- every directory has a named index;
- indexes create navigation hubs;
- backlinks reveal relationships;
- graph view exposes collection relationships;
- Markdown remains readable outside Obsidian;
- Git remains storage/versioning;
- no plugin is required.

Visual concept:

```text
Markdown
   ↓
Lliki Wiki
   │
   ├── Humans
   ├── Obsidian
   ├── Coding Agents
   └── Automation
```

---

# 16. Move project documentation

Move:

```text
docs/AGENT_INTEGRATIONS.md
docs/DESIGN.md
docs/IMPLEMENTATION_CHECKPOINTS.md
docs/RELEASE_PROCESS.md
```

to:

```text
wiki/docs/
```

The resulting folder must include:

```text
wiki/docs/docs-index.md
```

Move:

```text
docs/assets/
```

to:

```text
assets/
```

Result:

```text
assets/
wiki/docs/
    docs-index.md
    ...
```

This allows Lliki to dogfood its own information architecture.

---

# 17. Hermes integration

Target:

```bash
lliki init --custom --integrate hermes
```

Message:

```text
Hermes integration configured.

Created/updated:
  .hermes.md

Hermes navigation contract:
  1. Resume existing work from wiki/tasks/resume.md.
  2. Start new work from wiki/wiki-index.md.
  3. Follow named folder indexes before scanning folders.
  4. Read only relevant linked documents.
  5. Update durable knowledge only when appropriate.
```

The same principle should apply to Claude and generic agent integrations.

---

# 18. Agent navigation rule

Add this explicitly to `wiki-rules.md`.

For new work:

```text
wiki/wiki-index.md
       ↓
relevant <folder>-index.md
       ↓
relevant document
```

For resumed work:

```text
wiki/tasks/resume.md
       ↓
active task
       ↓
linked knowledge
```

Agents should avoid:

```text
recursively reading wiki/**/*.md
```

unless specifically necessary.

---

# 19. PyPI version update detection

Do not query PyPI on every execution.

Recommended:

```text
CLI launch
   ↓
read update-check cache
   ↓
launch threshold / timestamp
   ↓
occasionally query PyPI
   ↓
cache response
```

Example policy:

```text
first launch      no request
second launch     no request
third launch      check
then              maximum once / 24 h
```

Provide:

```bash
lliki version --check
```

and:

```text
LLIKI_NO_UPDATE_CHECK=1
```

No repository data should be transmitted.

---

# 20. Notes encryption

Keep normal notes plaintext:

```text
wiki/notes/
```

Optional commands:

```bash
lliki notes encrypt <note>
lliki notes decrypt <note>
```

Do not invent a cryptographic scheme.

Document clearly:

> Encrypted files cannot participate directly in normal Obsidian navigation, backlinks, full-text search, or agent context until decrypted.

For that reason encryption should be an optional later feature rather than part of the base notes implementation.

---

# 21. Doctor checks

Extend:

```bash
lliki doctor
```

to validate the index contract.

Examples:

```text
WIKI001 missing folder index
WIKI002 broken internal link
WIKI003 orphan document
WIKI004 legacy dashboard path
WIKI005 generated index stale
WIKI006 incorrect index filename
WIKI007 index does not link child folder index
```

Example:

```text
wiki/exploratory/
```

without:

```text
wiki/exploratory/exploratory-index.md
```

should generate a warning/error.

---

# 22. Orphan detection

A Markdown document should generally be reachable from:

```text
wiki-index
     ↓
folder-index
     ↓
document
```

Therefore `doctor` can identify documents with no incoming collection relationship.

Example:

```text
WARNING WIKI003:
wiki/notes/random-test.md
is not referenced by notes-index.md
```

This improves both Obsidian navigation and agent discoverability.

---

# 23. Context-routing model

Extend:

```bash
lliki context --json
```

to return:

```json
{
  "entry": "wiki/wiki-index.md",
  "resume": "wiki/tasks/resume.md",
  "scratchpad": "wiki/tasks/scratchpad.md",
  "tasks": "wiki/tasks/tasks-index.md",
  "docs": "wiki/docs/docs-index.md",
  "exploratory": "wiki/exploratory/exploratory-index.md",
  "notes": "wiki/notes/notes-index.md",
  "decisions": "wiki/decisions.md",
  "lessons": "wiki/lessons_learned.md"
}
```

Future custom folders can optionally appear automatically:

```json
{
  "collections": {
    "research": "wiki/research/research-index.md",
    "hardware": "wiki/hardware/hardware-index.md"
  }
}
```

---

# 24. Lightweight knowledge manifest

Add:

```bash
lliki knowledge build
```

Output to a non-source cache location such as:

```text
.lliki-cache/knowledge.json
```

Example:

```json
{
  "version": 1,
  "documents": [
    {
      "path": "wiki/tasks/TASK-042.md",
      "type": "task",
      "title": "Implement notes",
      "status": "active",
      "collection": "wiki/tasks/tasks-index.md",
      "links": [
        "wiki/docs/design.md"
      ],
      "tags": [
        "cli"
      ]
    }
  ]
}
```

No LLM is required.

Extract:

```text
path
title
frontmatter
wikilinks
Markdown links
tags
document type
parent folder
parent index
timestamps
status
```

---

# 25. Folder indexes become graph collections

The deterministic graph can expose explicit nodes:

```text
Collection
Document
Tag
```

Relationships:

```text
Collection ──CONTAINS────> Document
Collection ──CONTAINS────> Collection
Document ───LINKS_TO─────> Document
Document ───TAGGED_WITH──> Tag
```

Example:

```text
wiki-index
    │
    └── CONTAINS → notes-index
                        │
                        ├── CONTAINS → modem-notes
                        └── CONTAINS → camera-notes
```

This provides useful graph structure before introducing any semantic inference.

---

# 26. `lliki knowledge query`

Potential commands:

```bash
lliki knowledge query --collection notes

lliki knowledge query --links-to TASK-042

lliki knowledge query --tag camera

lliki knowledge query --type exploratory

lliki knowledge query --related TASK-042
```

For example:

```bash
lliki knowledge query --collection exploratory
```

can resolve through:

```text
wiki/exploratory/exploratory-index.md
```

rather than scanning the entire wiki.

---

# 27. Why not CocoIndex in core yet?

Lliki should preserve:

```text
pip install
     ↓
lliki init
     ↓
Markdown
```

External semantic infrastructure should remain optional.

Architecture:

```text
Markdown
    ↓
Lliki deterministic structure
    ↓
knowledge graph / manifest
    │
    ├── native query
    ├── CocoIndex
    ├── Graphify
    └── future adapters
```

Lliki owns:

```text
file structure
document semantics
folder indexes
explicit links
metadata
document lifecycle
```

External tools may own:

```text
semantic relationships
embeddings
entity extraction
vector retrieval
LLM inference
```

---

# 28. CocoIndex experiment — Lliki 0.5+

Potential optional pipeline:

```text
wiki/**/*.md
      ↓
CocoIndex incremental change detection
      ↓
changed documents only
      ↓
semantic enrichment
      ↓
extended graph
```

The deterministic Lliki graph remains the baseline.

CocoIndex enriches it rather than replacing it.

---

# 29. Provenance

Semantic relationships must preserve origin.

Example:

```json
{
  "source": "Sentry",
  "relation": "depends_on",
  "target": "RS485",
  "evidence": "wiki/docs/sentry.md",
  "origin": "inferred",
  "confidence": 0.89
}
```

Distinguish:

```text
COLLECTION
DECLARED
LINKED
EXTRACTED
INFERRED
```

A relationship created because an index references a child should be deterministic:

```text
origin = collection
```

A Markdown wikilink:

```text
origin = linked
```

An LLM-derived relationship:

```text
origin = inferred
```

---

# 30. README redesign

Suggested opening:

> # LLIKI
>
> **Persistent project memory for coding agents.**
>
> Your code changes.  
> Your agents change.  
> Your context shouldn't disappear.

Visual:

```text
             ┌──────────────┐
             │ Your project │
             └──────┬───────┘
                    │
                  lliki
                    │
           ┌────────▼────────┐
           │ Repository Wiki │
           └────────┬────────┘
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
     Human        Obsidian      Agents
```

The named-index concept should also appear visually:

```text
wiki-index
  ├── tasks-index
  ├── docs-index
  ├── exploratory-index
  └── notes-index
```

This is a simple way of explaining Lliki's information model.

---

# 31. Improve logo

Assets:

```text
assets/
├── lliki-logo.svg
├── lliki-logo-dark.svg
├── lliki-mark.svg
└── screenshots/
```

Visual themes:

```text
knowledge
links
nodes
continuity
context
```

The linked-index hierarchy could even inform the visual identity.

Avoid generic:

```text
robot
AI brain
sparkles
```

imagery.

---

# 32. GitHub Pages website

Suggested structure:

```text
/
├── Hero
├── Why Lliki
├── How it works
├── Knowledge structure
├── Install
├── Agent workflow
├── Obsidian
├── CLI
├── Architecture
└── GitHub
```

One strong diagram:

```text
                      wiki-index
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
   tasks-index       docs-index        notes-index
        │                 │                  │
    task files         docs             note files
```

This communicates both:

- human navigation;
- machine context routing.

---

# 33. CLI target

```text
lliki
├── init
├── update
├── doctor
├── inspect
├── context
│
├── task
│   └── new
│
├── tasks
│   └── refresh
│
├── notes
│   ├── new
│   ├── list
│   ├── show
│   ├── append
│   ├── search
│   ├── encrypt
│   └── decrypt
│
├── explore
│   └── new
│
├── index
│   └── refresh
│
├── knowledge
│   ├── build
│   └── query
│
├── integration
│   └── status
│
├── prompt
│   ├── list
│   └── show
│
├── templates
│   ├── export
│   ├── validate
│   ├── diff
│   └── sync
│
└── version
    └── --check
```

---

# 34. Release breakdown

## 0.4.0 — Wiki as Workspace

### P0 — information architecture

- [ ] Define `<folder-name>-index.md` as a mandatory convention
- [ ] Rename `wiki/index.md` → `wiki/wiki-index.md`
- [ ] Rename `dashboard.md` → `resume.md`
- [ ] Add `wiki/tasks/tasks-index.md`
- [ ] Add `wiki/docs/docs-index.md`
- [ ] Add `wiki/exploratory/exploratory-index.md`
- [ ] Add `wiki/notes/notes-index.md`
- [ ] Require an index for every future wiki subfolder
- [ ] Add recursive folder-index generation
- [ ] Convert indexes to references-only
- [ ] Add safe migration support
- [ ] Update context routing
- [ ] Update `doctor`

### P1 — content operations

- [ ] `lliki task new`
- [ ] `lliki notes new`
- [ ] `lliki notes list`
- [ ] `lliki notes show`
- [ ] `lliki notes append`
- [ ] `lliki notes search`
- [ ] `lliki explore new`
- [ ] shared content/template factory
- [ ] automatically refresh the relevant parent index

### P1 — integrations

- [ ] Fix Hermes setup message
- [ ] Review Hermes template
- [ ] Add `lliki integration status`
- [ ] Update Claude/generic instructions
- [ ] Tell agents to traverse folder indexes before files

### P1 — repository cleanup

- [ ] Move `/docs/*` → `/wiki/docs/`
- [ ] Move `/docs/assets` → `/assets`
- [ ] Fix documentation links
- [ ] Dogfood named-index convention in Lliki itself

### P2 — update experience

- [ ] PyPI update checker
- [ ] delayed/periodic checks
- [ ] cached result
- [ ] `LLIKI_NO_UPDATE_CHECK`
- [ ] explicit `lliki version --check`

### P2 — Obsidian

- [ ] document Obsidian workflow
- [ ] explain named indexes
- [ ] validate wikilinks
- [ ] document YAML conventions
- [ ] add README icons
- [ ] verify generated wiki as a vault without plugins

---

# 35. 0.4.1 — Private Notes

- [ ] threat model
- [ ] encryption format
- [ ] `notes encrypt`
- [ ] `notes decrypt`
- [ ] safe Git behavior
- [ ] document Obsidian limitations
- [ ] plaintext leakage tests

---

# 36. 0.5.0 — Structured Knowledge

- [ ] Markdown metadata parser
- [ ] wikilink parser
- [ ] folder collection parser
- [ ] backlink graph
- [ ] `knowledge.json`
- [ ] `lliki knowledge build`
- [ ] `lliki knowledge query`
- [ ] orphan detection
- [ ] relationship provenance

Initial graph:

```text
Collection ──CONTAINS────> Collection
Collection ──CONTAINS────> Document
Document ───LINKS_TO─────> Document
Document ───TAGGED_WITH──> Tag
```

No LLM.

---

# 37. Recommended implementation order

```text
01  Freeze folder-index convention
 ↓
02  index.md → wiki-index.md
 ↓
03  dashboard.md → resume.md
 ↓
04  create named indexes for existing folders
 ↓
05  recursive deterministic index generator
 ↓
06  doctor/context updates
 ↓
07  add notes/
 ↓
08  generic document factory
 ↓
09  task/note/explore commands
 ↓
10  automatic parent-index refresh
 ↓
11  Hermes + agent contract updates
 ↓
12  move docs/assets
 ↓
13  Obsidian validation/documentation
 ↓
14  PyPI update checker
 ↓
15  release 0.4.0
 ↓
16  encryption
 ↓
17  deterministic knowledge graph
 ↓
18  query interface
 ↓
19  benchmark token reduction
 ↓
20  CocoIndex/Graphify experiment
```

---

# 38. Definition of Done for 0.4.0

A fresh user runs:

```bash
pipx install lliki
cd project
lliki init
```

and receives:

```text
wiki/
├── wiki-index.md
├── wiki-rules.md
├── decisions.md
├── lessons_learned.md
│
├── docs/
│   └── docs-index.md
│
├── tasks/
│   ├── tasks-index.md
│   ├── resume.md
│   └── scratchpad.md
│
├── exploratory/
│   └── exploratory-index.md
│
└── notes/
    └── notes-index.md
```

Any additional folder created through Lliki:

```text
wiki/research/
```

must automatically receive:

```text
wiki/research/research-index.md
```

Then:

```bash
lliki task new "Implement API"
lliki notes new "API thoughts"
lliki explore new "Authentication alternatives"
```

should:

1. create the Markdown document;
2. add metadata;
3. update the appropriate named index;
4. preserve manual content;
5. require no LLM.

Opening `wiki/` in Obsidian should immediately expose a readable graph:

```text
wiki-index
    │
    ├── tasks-index
    ├── docs-index
    ├── exploratory-index
    └── notes-index
```

A coding agent should be able to call:

```bash
lliki context --json
```

and know exactly which collection to inspect without recursively reading the repository.

`lliki doctor` should detect:

- missing indexes;
- incorrectly named indexes;
- broken links;
- orphan documents;
- stale generated indexes;
- legacy paths.

Existing 0.3 repositories must migrate safely using:

```bash
lliki update
```

without losing manually maintained knowledge.

---

# Product architecture after 0.5

```text
                           LLIKI
                             │
                    ┌────────▼────────┐
                    │   wiki-index    │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
        tasks-index      docs-index      notes-index
             │               │               │
             └───────────────┼───────────────┘
                             │
                    Markdown documents
                             │
                  deterministic parsing
                             │
                    ┌────────▼────────┐
                    │  Lliki Graph    │
                    └────────┬────────┘
                             │
                    optional enrichment
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
           CocoIndex                    Graphify /
                                        others
```

The strategic distinction remains:

> **Lliki should own project knowledge structure, relationships and navigation — not model intelligence.**

Named folder indexes make that structure explicit for humans, Obsidian and agents while simultaneously giving the future Lliki graph a deterministic hierarchy.