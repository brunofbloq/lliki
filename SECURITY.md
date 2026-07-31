# Security

`lliki` is local-only by default. It makes no network calls and requires no
runtime credentials.

Do not place API keys, passwords, tokens, private keys, or credentials in
`CLAUDE.md`, `AGENTS.md`, wiki files, template packs, command-line arguments, or
committed `.env` files.

Future LLM-provider integrations should use operating-system keychains,
provider-standard environment variables, or CI secret stores. External context
transmission must remain explicit and reviewable.

The optional `.lliki/` directory is local runtime state and is gitignored.
It may contain project-sensitive resume notes or debug information and should
not be uploaded automatically.
