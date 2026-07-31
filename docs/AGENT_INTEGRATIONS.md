# Agent Integrations

## Default mode

No agent-specific integration is installed. Claude reads the root `CLAUDE.md`.
Hermes can also fall back to `CLAUDE.md` when no higher-priority project context
file exists.

## Generic

Creates `AGENTS.md`, which points compatible agents to the stable contract and
`wiki/index.md`.

## Claude

Creates a project skill at `.claude/skills/lliki/SKILL.md`. Optional
project hooks call `lliki` for mechanical dashboard refresh and lightweight
resume context. Hooks never invent semantic decisions or documentation.

## Hermes

Creates `.hermes.md`, which explicitly routes Hermes to the root stable contract
and the same wiki entry point. No global Hermes skill or plugin is installed.

All integrations are repository-local and opt-in.
