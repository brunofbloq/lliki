# Repository Rules and Protected Paths

This is the authoritative location for project-specific modification boundaries.

## Protected or Sensitive Paths

- `src/lliki/templates/`: source of generated wiki, prompt, and integration
  text. Changes here affect future `lliki init`, `templates sync`, prompt
  rendering, and documentation bootstrap behavior.
- `CLAUDE.md`: contains a managed Lliki contract section. Keep it stable and
  project-neutral; put changing project facts under `wiki/`.
- `wiki/`: durable project knowledge for this repository. Update selectively
  after meaningful task events and completed requests.
- `.github/workflows/`: CI and release automation, including PyPI publish.
- `pyproject.toml`, `MANIFEST.in`, `packaging/`, `scripts/`, `dist/`, and
  `SHA256SUMS`: packaging and distribution-related files.
- `wiki/tasks/scratchpad.md`: ignored local handover state. Keep it bounded and
  non-authoritative.
- `.lliki/`, when present, is legacy local state. New Lliki behavior must not
  create or depend on it.

## Modification Procedures

- Prefer focused edits that preserve deterministic CLI behavior and template
  idempotency.
- Use `lliki update` as the normal deterministic migration path for existing
  repositories after upgrading Lliki.
- When changing templates, validate with `lliki templates validate` and review
  generated differences with `lliki templates diff` where relevant.
- When changing bootstrap, patching, task, prompt, context, doctor, or CLI behavior,
  run the unittest suite and relevant Lliki command checks.
- Do not overwrite existing wiki or agent files wholesale unless the user
  explicitly asks for regeneration; preserve unmanaged user content and managed
  section boundaries.
- If adding optional integrations, keep them repository-local and opt-in.

## Repository Structure and Ownership

- `src/lliki/`: Python package implementation.
- `src/lliki/core/`: deterministic mechanics and data handling.
- `src/lliki/integrations/`: repository-local integration installers.
- `src/lliki/templates/`: built-in Markdown/template pack.
- `tests/`: unittest coverage.
- `docs/`: human-maintained design and implementation notes.
- `scripts/` and `packaging/`: installer and package-manager support.
- `wiki/`: initialized project knowledge for this working repository.

## Prohibited Changes

- Do not introduce mandatory LLM/API/network dependencies into default CLI
  mechanics.
- Do not create `.lliki/`, `state.json`, or runtime logs in new behavior.
- Do not store project-specific changing facts in `CLAUDE.md`.
- Do not treat `.lliki/` as authoritative durable knowledge.
- Do not claim validation, packaging, publish, or release results unless they
  were actually run and recorded.
