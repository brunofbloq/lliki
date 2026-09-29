# Development Workflow and Commands

This is the authoritative location for project-specific commands and environment
assumptions. Keep every recorded command executable and verified.

## Prerequisites

- Python 3.9 or newer.
- `pip` for editable local installation.
- PowerShell on Windows for `scripts/install.ps1`; Bash for
  `scripts/install.sh`.
- Optional: `pipx` for user-level CLI installation.

## Build

Local editable install:

```bash
python -m pip install -e .
lliki --version
```

Build distributions, when the `build` package is available:

```bash
python -m build
```

Release CI builds wheels and source distributions from tags matching `v*`,
writes `SHA256SUMS`, uploads artifacts, and publishes to PyPI through the
configured GitHub Actions environment.

## Test and Static Analysis

Primary local regression suite:

```bash
python -m unittest discover -s tests -v
```

Syntax/package checks used by CI:

```bash
python -m compileall -q src
lliki templates validate
```

Useful Lliki structural checks while working in this repository:

```bash
lliki doctor
lliki context
lliki tasks
lliki update
lliki templates diff
```

Use `--json` on supported commands when an agent or script needs
machine-readable output.

## Flash, Run, and Debug

This is a local CLI project; no firmware flash or target-device debug workflow
is evidenced.

Run the CLI directly after editable install:

```bash
lliki --help
lliki init --default --yes
```

On Windows consoles that cannot encode prompt box-drawing characters, set UTF-8
output for the command:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\lliki.exe init --default --yes
```

## Optional Semantic Code Search (ccc, opt-in)

LLIKI-051 pilot: `cocoindex-code` provides local semantic search over `*.py`
and `*.md`. It is external tooling; Lliki core never depends on it.

```powershell
uv tool install 'cocoindex-code[full]'   # ccc on PATH, local embeddings
ccc index                                # incremental; state in .cocoindex_code/ (gitignored)
ccc search "stale generated index"
```

Required setup on this machine (see LL-006): set
`~/.cocoindex_code/global_settings.yml` to
`Snowflake/snowflake-arctic-embed-m` with `query_params.prompt_name: query`;
the default xs model has unusable code recall and CodeRankEmbed crashes on
the pinned stack. Set `$env:PYTHONIOENCODING='utf-8'` for non-TTY shells.
Project settings live in `.cocoindex_code/settings.yml`
(includes `**/*.py`, `**/*.md`; excludes `.backup/`, scratchpad, hidden dirs).

## Validation Evidence

Record durable validation outcomes in the active task or relevant wiki page
when they affect project truth. Keep transient command output in the terminal
or in `wiki/tasks/scratchpad.md` only when it is needed for bounded local handover.
