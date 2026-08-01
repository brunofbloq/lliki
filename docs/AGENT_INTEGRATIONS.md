# Agent Integrations

## Default mode

No agent-specific integration is installed. Claude reads the root `CLAUDE.md`.
Hermes can also fall back to `CLAUDE.md` when no higher-priority project context
file exists.

## Generic

Creates `AGENTS.md`, which points compatible agents to the stable contract,
`wiki/tasks/scratchpad.md` for resumption, and `wiki/index.md` for new work.

## Claude

Creates a project skill at `.claude/skills/lliki/SKILL.md`. Optional
project hooks call `lliki` for mechanical dashboard refresh and lightweight
scratchpad resume context. Hooks never invent semantic decisions,
documentation, or scratchpad content.

## Hermes

Creates `.hermes.md`, which explicitly routes Hermes to the root stable
contract, scratchpad handover, and the same wiki knowledge map. No global Hermes
skill or plugin is installed.

All integrations are repository-local and opt-in.
