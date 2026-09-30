# Changelog

## 0.4.1 - 2026-09-30

- Fixed `print_welcome` binding its output stream at import time; it now
  resolves `sys.stdout` at call time, so redirected streams no longer crash
  with `UnicodeEncodeError` on Windows cp1252 consoles.

## 0.4.0 - 2026-09-30

- Reorganized the wiki around named folder indexes (`wiki-index.md` plus
  `<folder>-index.md` per directory) with deterministic, LLM-free generation
  and preserved manual content outside generated regions.
- `wiki/index.md` renamed to `wiki/wiki-index.md`; project documentation and
  assets migrated under `wiki/docs/` and `assets/`.
- Task workflow rebuilt: `tasks-index.md` is the single execution entry with a
  generated scratchpad-driven `Current Task` region; the separate `resume.md`
  route was retired. Closed tasks stay reachable via compact ID-only links.
- Added content commands: `lliki tasks new`, `lliki notes`, `lliki explore`,
  `lliki append`; notes and decisions/lessons are front-matter Markdown.
- Documented the Obsidian vault format contract (wikilinks, YAML front
  matter, no Dataview/Templater dependency).
- Added lazy, cached PyPI update detection (`lliki version --check`,
  background notice, `LLIKI_NO_UPDATE_CHECK=1`); no repository data sent.
- Compacted the command surface: bare `lliki` shows a read-only common-command
  overview; bare `tasks`, `index`, and `integration` perform their default
  action; `doctor --json` carries legacy-location inspection; `hook` moved to
  `lliki integration hook` with a compatibility alias; removed `state`,
  `inspect`, `--runtime`, `--scratchpad`, and `--update-index`.
- Leaner prompt templates and agent contracts; removed embedded-specialist
  and resume-route wording.
- Optional semantic code search pilot documented via `cocoindex-code`
  (`ccc` skill), fully external to lliki core.

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
