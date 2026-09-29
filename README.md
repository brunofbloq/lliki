# Lliki

`lliki` is local continuity infrastructure for LLM-assisted software
development. It helps coding agents recover after context loss, load only the
context they need, avoid repeated investigation, and preserve engineering
knowledge as a repository evolves.

The implementation is a small repository wiki plus deterministic CLI commands.
The product is not "another docs generator"; it is a way to keep humans and
coding LLMs oriented during real development on non-trivial codebases.

Lliki does not call an LLM, require API credentials, or transmit repository
content by default. It performs local file mechanics; the human or coding agent
still owns semantic engineering decisions.


```text
 __         __         __     __  __     __    
/\ \       /\ \       /\ \   /\ \/ /    /\ \   
\ \ \____  \ \ \____  \ \ \  \ \  _"-.  \ \ \  
 \ \_____\  \ \_____\  \ \_\  \ \_\ \_\  \ \_\ 
  \/_____/   \/_____/   \/_/   \/_/\/_/   \/_/ 

```

## What Lliki Solves

- Recover after LLM compaction, session resets, or agent switches.
- Minimize whole-repo and whole-wiki context loading.
- Prevent repeated debugging and rediscovery.
- Preserve durable engineering decisions and lessons.
- Keep agent behavior consistent as code, tasks, and docs change.

## How Lliki Works

- `wiki/wiki-index.md` is the stable knowledge map for new work or workstream
  switches. Every `wiki/` folder has a named index (`docs-index.md`,
  `tasks-index.md`, `notes-index.md`, ...) that links its children.
- `wiki/decisions.md` and `wiki/lessons_learned.md` hold durable engineering
  memory.
- `wiki/tasks/` is the local folder where the tasks and related helper files will live.
  - `wiki/tasks/scratchpad.md` is ignored local resume memory for the active task.
  - `wiki/tasks/tasks-index.md` is the generated catalog for every task plus a
    generated `Current Task` route (scratchpad-selected task and scratchpad
    link); closed tasks stay reachable by compact ID-only links.
- `wiki/notes/` holds lightweight notes that are not yet tasks, decisions, or
  maintained documentation.

The new agent flow is:

```text
Start or switch work:
  wiki-index -> named folder index -> focused source files

Resume known work:
  scratchpad -> task file -> git verification -> focus source files

Complete work:
  task result -> decisions/lessons/docs -> index refresh -> scratchpad reset
```

## Default Setup

Running bare `lliki` shows a read-only overview: welcome plus the common
commands (`init`, `update`, `doctor`, `index`, `tasks`, `context`, `prompt`).
It writes nothing. `lliki --help` lists every command.

Setup runs via:

```bash
lliki init
```

The TUI offers:

```text
[1] Default - create/repair wiki and update CLAUDE.md
[2] Custom  - repository-local integrations
```

Default setup creates:

```text
CLAUDE.md
wiki/
|-- wiki-index.md
|-- wiki-rules.md
|-- tasks/
|   |-- tasks-index.md
|   `-- scratchpad.md
|-- decisions.md
|-- lessons_learned.md
|-- exploratory/
|   `-- exploratory-index.md
|-- notes/
|   `-- notes-index.md
`-- docs/
    |-- docs-index.md
    |-- project-overview.md
    |-- development-workflow.md
    `-- repository-rules.md
```

It also adds `/wiki/tasks/scratchpad.md` to `.gitignore`, then prints the LLM
initialization prompt and its estimated token usage.

Non-interactive equivalent:

```bash
lliki init --default --yes
```

## Obsidian Workflow

Open the repository's `wiki/` directory as an Obsidian vault. Start at
`wiki-index.md`; each subfolder's `<folder>-index.md` links its documents and
child indexes as graph hubs. Follow `[[wikilinks]]` and Obsidian backlinks to
navigate without loading the whole vault. No community plugins, Dataview, or
Templater are required.

Tasks, notes, and explorations created by Lliki use YAML front matter for
metadata and plain Markdown for content. See `wiki/wiki-rules.md` for field
conventions. Lliki's CLI and Markdown files also work without Obsidian.

## Installation

### pipx

```bash
pipx install lliki
```

### pip

```bash
python -m pip install lliki
```

### GitHub development version

```bash
pipx install "git+https://github.com/brunofbloq/lliki.git"
```

### Local development

```bash
python -m pip install -e .
lliki --version
```

The same installed `lliki` command works in Bash, PowerShell, CMD, macOS,
Linux, and Windows.

## Custom Setup

Custom setup uses the same `wiki/` root and `wiki/tasks/scratchpad.md`
handover file. It can opt into repository-local integrations:

- generic `AGENTS.md` integration;
- repository-local Claude skill and optional hooks;
- repository-local Hermes context through `.hermes.md`.

Example:

```bash
lliki init --custom --integrate generic,claude,hermes --yes
```

The legacy `--runtime` and `--scratchpad` options are deprecated. New
initialization never creates `.lliki/`, `state.json`, or runtime logs.

## Agent Workflow

The user does not need to run maintenance commands during normal development.
Generated instructions teach the coding agent to:

1. resume active local work from `wiki/tasks/scratchpad.md` and `wiki/tasks/tasks-index.md`;
2. begin new work from `wiki/wiki-index.md`;
3. load only relevant context;
4. update durable project knowledge after meaningful events;
5. use `lliki` internally for mechanical checks when efficient;
6. avoid whole-wiki reads and whole-file rewrites.

Manual commands remain available when a token-free structural check is useful.

## Token-Free Commands

```bash
lliki doctor
lliki context
lliki index
lliki tasks
lliki update
lliki templates diff
```

Content creation needs no LLM either:

```bash
lliki task new "Implement API"
lliki notes new "Toradex modem experiment"
lliki explore new "Authentication alternatives"
lliki notes list
lliki notes search modem
```

Use `--json` with `doctor`, `context`, `index`,
`tasks`, or `update` when an agent or script needs machine-readable
output. `lliki version --check` queries PyPI explicitly; background update
notices fire at most once per 24 h after the first two launches and never
transmit repository data (`LLIKI_NO_UPDATE_CHECK=1` disables them).

## Updating an Existing Wiki

After upgrading Lliki, run:

```bash
lliki update
```

The command applies deterministic safe updates, migrates the 0.3 layout
(`wiki/index.md` -> `wiki/wiki-index.md`, `wiki/tasks/dashboard.md` and the
former `resume.md` -> `tasks-index.md`, docs/exploratory named indexes) without
losing manually maintained content, creates missing helper files, fixes the
scratchpad `.gitignore` rule, refreshes indexes, and runs structural
checks. It reports legacy `.lliki/` state and mutable wiki-index sections
without deleting or rewriting them.

## Suggested LLM Prompts

```bash
lliki prompt list
lliki prompt show initialize-project
lliki prompt show migrate-legacy
lliki prompt show complete-task
lliki prompt show explore-impact
lliki prompt show review-wiki
```

Every prompt prints:

- approximate prompt-only tokens;
- expected total call range;
- a reminder that actual use depends on model and loaded repository context.

## Editing Templates

Export the built-in template pack:

```bash
lliki templates export ./my-lliki-templates
```

Edit the Markdown files directly, including `CLAUDE.md`, wiki pages,
integration instructions, and prompts. Validate them:

```bash
lliki templates validate --template-dir ./my-lliki-templates
```

Preview repository changes:

```bash
lliki templates diff \
  --template-dir ./my-lliki-templates \
  --root .
```

Apply only missing files and managed-section changes:

```bash
lliki templates sync \
  --template-dir ./my-lliki-templates \
  --root .
```

The environment variable form is also supported:

```bash
export LLIKI_TEMPLATE_DIR="$PWD/my-lliki-templates"
lliki init
```

PowerShell:

```powershell
$env:LLIKI_TEMPLATE_DIR = "$PWD\my-lliki-templates"
lliki init
```

## Task Metadata and Index Generation

Task files can use YAML front matter:

```markdown
---
id: HWRD-115
title: Sensor bring-up
status: active
priority: high
updated: 2026-07-31
---
```

`lliki index` regenerates every `<folder>-index.md` generated region
deterministically; manual content outside the generated markers is preserved.
The tasks index lists active, blocked, planned, and closed tasks; closed links
show only task IDs. Its generated `Current Task` region renders only the
scratchpad-selected current task and never auto-selects a next task.
`wiki/wiki-index.md` stays a stable knowledge map. The legacy `--update-index`
option is accepted as a deprecated no-op. Generated-file backups are stored
under `wiki/tasks/.backup/`, which is ignored by Git.

Task files should keep stable intent, constraints, and final outcomes. Use
`wiki/tasks/scratchpad.md` for temporary progress and checkpoints; use
`wiki/decisions.md` and `wiki/lessons_learned.md` for durable history.

## Safe Update Behavior

- Existing content is never blindly replaced.
- Managed sections are identified by HTML comment markers.
- Existing `CLAUDE.md` content is preserved; the stable managed contract is
  appended when no marker exists.
- Backups are created before managed updates; dashboard backups are kept in
  `wiki/tasks/.backup/`.
- Decisions and lessons use append-only files.
- Context-sensitive wiki files are created with explicit `Needs validation`
  markers for LLM or human initialization.

## Repository-Local Agent Integrations

### Claude Code

Custom setup can create:

```text
.claude/skills/lliki/SKILL.md
.claude/settings.json
```

Hooks are optional. When enabled, they perform only mechanical index and
structural maintenance and do not invent semantic documentation or scratchpad
content.

### Hermes

Custom setup can create `.hermes.md`, which instructs Hermes to begin from the
same wiki entry point and use the CLI internally when efficient.

### Generic agents

Custom setup can create `AGENTS.md` for compatible coding agents.

## Development and Release

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src
python -m pip wheel . --no-deps --wheel-dir dist
```

See [wiki/docs/DESIGN.md](wiki/docs/DESIGN.md) for architecture and update ownership.
See [wiki/docs/RELEASE_PROCESS.md](wiki/docs/RELEASE_PROCESS.md) for TestPyPI, Twine,
tagging, and PyPI release steps.

## Interactive Welcome

Running `lliki` or `lliki init` in an interactive terminal displays the Lliki
ASCII welcome; bare `lliki` additionally shows the common-command overview
panel. The banner is intentionally omitted from non-interactive runs, JSON
output, hooks, and CI. Set `LLIKI_NO_BANNER=1` to suppress it locally.
