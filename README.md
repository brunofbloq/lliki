# Lliki

`lliki` is a local CLI that creates and maintains a low-token, model-neutral project wiki for humans and coding tools. The normal user workflow remains simple: initialize the
repository once, print the recommended LLM onboarding prompt, and then work with
Claude, Hermes, or another coding agent normally.

The application performs deterministic file mechanics. The LLM remains
responsible for semantic engineering decisions and project documentation.

Lliki does not call an LLM, require API credentials, or transmit repository content by default. Optional repository-local integrations let coding agents use its deterministic wiki-management commands.

<p align="center">
  <img src="https://raw.githubusercontent.com/brunofbloq/lliki/main/docs/assets/lliki-ascii.png" alt="Lliki ASCII logo" width="760">
</p>

## Default setup

Run:

```bash
lliki init
```

The TUI offers:

```text
[1] Default — create/repair wiki and update CLAUDE.md
[2] Custom  — repository-local integrations
```

Default setup creates:

```text
CLAUDE.md
wiki/
├── index.md
├── wiki-rules.md
├── scratchpad.md
├── tasks/
│   └── dashboard.md
├── decisions.md
├── lessons_learned.md
├── exploratory/
│   └── index.md
└── docs/
    ├── README.md
    ├── project-overview.md
    ├── development-workflow.md
    └── repository-rules.md
```

It also adds `/wiki/tasks/scratchpad.md` to `.gitignore`, then prints the LLM
initialization prompt and its estimated token usage in the terminal. 

Non-interactive equivalent:

```bash
lliki init --default --yes
```


## Key design decisions

- `wiki/index.md` is the stable knowledge map for new work and workstream switches.
- The default setup creates only the wiki and safely creates or patches
  `CLAUDE.md`.
- `wiki/tasks/scratchpad.md` is created by default as ignored local handover state.
- Hooks and agent integrations are opt-in.
- All Markdown templates and suggested prompts are editable files, not Python
  string literals.
- Every suggested LLM prompt includes a prompt-token estimate and expected total
  call range.
- Permanent wiki updates are event-driven: after meaningful task events and at
  the end of completed user requests, only when project truth changed.

## Installation

### pipx

```bash
pipx install lliki
```

### pip

```bash
python -m pip install lliki
```

### Homebrew

```bash
brew install brunofbloq/tap/lliki
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

### Local pipx install

```bash
pipx install .
```

The same installed `lliki` command works in Bash, PowerShell, CMD, macOS,
Linux, and Windows.

### Windows PowerShell helper

```powershell
.\scripts\install.ps1 -Source .
```

### Bash helper

```bash
./scripts/install.sh .
```

Homebrew and Debian packaging templates are under `packaging/`.


## Custom setup

Custom setup uses the same `wiki/` root and `wiki/tasks/scratchpad.md` handover file.
It can opt into repository-local integrations:

- generic `AGENTS.md` integration;
- repository-local Claude skill and optional hooks;
- repository-local Hermes context through `.hermes.md`.

Example:

```bash
lliki init --custom --integrate generic,claude,hermes --yes
```

The legacy `--runtime` and `--scratchpad` options are deprecated. New
initialization never creates `.lliki/`, `state.json`, or logs.

## Normal agent workflow

The user does not need to run maintenance commands during normal development.
Generated instructions teach the coding agent to:

1. begin new work from `wiki/index.md`;
2. resume active local work from `wiki/tasks/scratchpad.md`;
3. load only relevant context;
4. update project knowledge after meaningful events and completed requests;
5. use `lliki` internally for mechanical checks when efficient;
6. avoid whole-wiki reads and whole-file rewrites.

Manual commands remain available when a token-free structural check is useful.

## Token-free commands

```bash
lliki inspect
lliki doctor
lliki context
lliki tasks refresh
lliki update
lliki templates diff
```

Use `--json` with `inspect`, `doctor`, `context`, `tasks refresh`, or `update`
when an agent or script needs machine-readable output.

## Updating an Existing Wiki

After upgrading Lliki, run:

```bash
lliki update
```

The command applies deterministic safe updates, creates missing
`wiki/tasks/scratchpad.md`, fixes the scratchpad `.gitignore` rule, refreshes the task
dashboard, and runs structural checks. It reports legacy `.lliki/` state and
mutable `wiki/index.md` sections without deleting or rewriting them.

## Suggested LLM prompts

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

## Editing templates like documents

Export the built-in template pack:

```bash
lliki templates export ./my-lliki-templates
```

Edit the Markdown files directly, including `CLAUDE.md`, wiki pages, integration
instructions, and prompts. Validate them:

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

## Task metadata and dashboard generation

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

`lliki tasks refresh` generates `wiki/tasks/dashboard.md` without an LLM.
`wiki/index.md` remains a stable knowledge map and is not mutated by dashboard
refreshes. The legacy `--update-index` option is accepted as a deprecated no-op.

## Safe update behavior

- Existing content is never blindly replaced.
- Managed sections are identified by HTML comment markers.
- Existing `CLAUDE.md` content is preserved; the stable managed contract is
  appended when no marker exists.
- Backups are created before managed updates.
- Decisions and lessons use append-only files.
- Context-sensitive wiki files are created with explicit `Needs validation`
  markers for LLM or human initialization.

## Repository-local agent integrations

### Claude Code

Custom setup can create:

```text
.claude/skills/lliki/SKILL.md
.claude/settings.json
```

Hooks are optional. When enabled, they perform only mechanical dashboard and
structural maintenance and do not invent semantic documentation or scratchpad
content.

### Hermes

Custom setup can create `.hermes.md`, which instructs Hermes to begin from the
same wiki entry point and use the CLI internally when efficient.

### Generic agents

Custom setup can create `AGENTS.md` for compatible coding agents.

## Development and tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src
python -m pip wheel . --no-deps --wheel-dir dist
```

See [docs/DESIGN.md](docs/DESIGN.md) for architecture and update ownership.

## Interactive welcome

Running `lliki` or `lliki init` in an interactive terminal displays the Lliki
ASCII welcome, a concise project-purpose statement, and the author. The banner
is intentionally omitted from non-interactive runs, JSON output, hooks, and CI.
Set `LLIKI_NO_BANNER=1` to suppress it locally.