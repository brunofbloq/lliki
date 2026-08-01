# Agent Integrations

Lliki integrations are repository-local instructions that help coding agents
resume work after context loss and avoid loading unnecessary repository
context. They do not install global agent behavior.

## Default Mode

No agent-specific integration is installed. Agents read the root `CLAUDE.md`
when their environment supports it. New work starts from `wiki/index.md`;
resume work starts from `wiki/tasks/scratchpad.md`.

## Resume Flow

When an agent resumes after compaction, a new session, or a handoff, the
expected route is:

```text
wiki/tasks/scratchpad.md
-> referenced task file
-> Git status and recorded commit check
-> listed focus files
-> next action
```

The agent should not begin by loading the whole wiki, all task files, or the
entire repository when the scratchpad identifies active work.

## Generic

Creates `AGENTS.md`, which points compatible agents to the stable contract,
`wiki/tasks/scratchpad.md` for resumption, and `wiki/index.md` for new work.

## Claude

Creates a project skill at `.claude/skills/lliki/SKILL.md`. Optional project
hooks call `lliki` for mechanical dashboard refresh and lightweight scratchpad
resume context. Hooks never invent semantic decisions, documentation, or
scratchpad content.

## Hermes

Creates `.hermes.md`, which explicitly routes Hermes to the root stable
contract, scratchpad handover, and the same wiki knowledge map.

All integrations are opt-in and repository-local.
