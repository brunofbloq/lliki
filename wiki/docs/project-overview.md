# Project Overview

## Purpose and Scope

Lliki is a local-first Python CLI that creates and maintains a concise project
wiki for humans and coding agents. It owns deterministic repository mechanics:
wiki/template bootstrap, managed-section synchronization, structural
inspection, token-estimated prompt rendering, task-dashboard refresh, bounded
context routing, scratchpad ignore-rule maintenance, safe append operations,
and repository-local agent integrations.

The project explicitly does not call an LLM, require API credentials, or
transmit repository content by default. Humans and coding agents remain
responsible for semantic project documentation and engineering decisions.

## Target and Architecture

Lliki is packaged as a Python project named `lliki` with the console script
`lliki = "lliki.cli:main"` and `requires-python = ">=3.9"`.

Major source areas:

- `src/lliki/cli.py`: argparse command surface for `init`, `inspect`,
  `doctor`, `prompt`, `templates`, `tasks`, `context`, `state`, `append`, and
  `hook`.
- `src/lliki/core/`: deterministic operations for bootstrap, template
  resources, patching, inspection, doctor checks, prompts, tasks, context
  routing, Git-ignore handling, and append behavior.
- `src/lliki/integrations/`: repository-local integration installation.
- `src/lliki/templates/`: editable built-in Markdown templates, prompts, and
  integration files.
- `src/lliki/branding.py` and `hooks.py`: interactive welcome output and hook
  entry points.

Tests live under `tests/` and cover bootstrap behavior, CLI subprocess use,
template validation, task dashboard generation, scratchpad routing, prompt
metadata, hook output, deprecated compatibility stubs, and doctor checks.

## Current Phase and Durable Constraints

The repository contains an implemented alpha-stage CLI (`0.2.1` in
`pyproject.toml`), distribution artifacts, packaging templates, and CI/release
workflows. Current work should treat the wiki as the durable coordination layer
for future changes.

Durable constraints:

- Keep generated/user-editable text in Markdown templates under
  `src/lliki/templates/` rather than hard-coded Python literals when practical.
- Keep default setup minimal: wiki plus `CLAUDE.md` and ignored
  `wiki/tasks/scratchpad.md`; hooks and agent integrations are opt-in.
- Keep semantic conclusions in `wiki/`; keep `CLAUDE.md` stable and
  project-neutral.
- Do not require network services, API credentials, or LLM calls for normal CLI
  mechanics.
- Specialist skill note: the generated prompt mentions
  `embedded-systems-architect`, but that skill is not available in this
  session and no embedded target is evidenced by this Python CLI repository.

## Evidence

- `README.md`: product purpose, setup modes, commands, and normal agent
  workflow.
- `pyproject.toml`: package metadata, supported Python version, console entry
  point, and package data.
- `docs/DESIGN.md`: deterministic CLI boundary, context strategy, setup modes,
  scratchpad, and template ownership.
- `docs/AGENT_INTEGRATIONS.md`: generic, Claude, and Hermes repo-local
  integration behavior.
- `docs/IMPLEMENTATION_CHECKPOINTS.md`: completed implementation and
  verification checkpoints.
- `.github/workflows/ci.yml` and `.github/workflows/release.yml`: CI matrix and
  release packaging/publish workflow.
- `src/lliki/` and `tests/`: implementation and regression coverage.
