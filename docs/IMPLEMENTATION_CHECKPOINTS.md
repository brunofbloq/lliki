# Implementation Checkpoints

## 1. Context model

Completed: stable agent contract, `wiki/index.md` as the only mandatory dynamic
entry point, project-specific commands and protected paths under `wiki/docs/`.

## 2. Editable templates

Completed: all generated Markdown and LLM prompts live under
`src/lliki/templates/`; export, validation, diff, and managed sync are
available.

## 3. Setup experience

Completed: simple default setup and progressive custom setup. Runtime state,
scratchpad, hooks, and integrations remain opt-in and repository-local.

## 4. Agent integrations

Completed: generic `AGENTS.md`, Claude project skill and optional lifecycle
hooks, and Hermes `.hermes.md` context integration.

## 5. Efficient maintenance

Completed: managed-section patching, task dashboard generation, bounded context
routing, safe decision/lesson append operations, and structural doctor checks.

## 6. Distribution

Completed: Python package and wheel, pipx installers, Homebrew formula template,
Debian packaging metadata, and GitHub Actions CI/release workflows.

## 7. Verification

Completed: unit/integration tests, Python 3.9 syntax validation, wheel install and
execution test, Bash and Ruby syntax checks, idempotency checks, template export
and override checks, and secret-pattern scan.
