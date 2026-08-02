# Changelog

## UNRELEASED - 2026-08-02
- Change the TUI messages for more specific and accurate setup
- Improved README.md for better scope

## 0.3.0 - 2026-08-01

- Refactored Lliki around a stable `wiki/index.md` knowledge map and default
  ignored `wiki/tasks/scratchpad.md` handover file.
- Added `lliki update` for deterministic existing-wiki migration.
- Removed new `.lliki/`, `state.json`, runtime log, and runtime scratchpad
  behavior from initialization and hooks.
- Deprecated runtime CLI options, `lliki state`, and index mutation from
  `lliki tasks refresh --update-index`.
- Expanded deterministic doctor checks and evolved `review-wiki` into the
  semantic wiki lint prompt.

## 0.2.1 - 2026-07-31

- Added a width-aware Lliki ASCII welcome banner to interactive setup.
- Added concise project-purpose, privacy, and author text.
- Kept non-interactive, JSON, hook, and CI output banner-free.
- Added `LLIKI_NO_BANNER=1` as an optional local override.

## 0.2.0 - 2026-07-31

- Rebuilt the bootstrap as an installable, model-neutral CLI.
- Moved all Markdown and prompts out of Python into editable package templates.
- Added simple default and progressive custom setup paths.
- Made runtime state and scratchpad optional.
- Added repository-local Claude, Hermes, and generic-agent integrations.
- Added managed-section patching instead of whole-file replacement.
- Added prompt token estimates, structural doctor checks, and task dashboard refresh.
- Added Homebrew and Debian packaging templates.
