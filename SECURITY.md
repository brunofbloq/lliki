# Security

`lliki` is local-only by default. It makes no network calls and requires no
runtime credentials.

Do not place API keys, passwords, tokens, private keys, or credentials in
`CLAUDE.md`, `AGENTS.md`, wiki files, template packs, command-line arguments, or
committed `.env` files.

Future LLM-provider integrations should use operating-system keychains,
provider-standard environment variables, or CI secret stores. External context
transmission must remain explicit and reviewable.

`wiki/tasks/scratchpad.md` is local handover state and is gitignored. Legacy `.lliki/`
directories, if present from older versions, are local state and should not be
published.
It may contain project-sensitive resume notes or debug information and should
not be uploaded automatically.
