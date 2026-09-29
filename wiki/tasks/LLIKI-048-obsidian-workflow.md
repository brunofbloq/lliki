---
id: LLIKI-048
title: README Obsidian section and vault validation (documentation only)
status: active
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-048-obsidian-workflow: README Obsidian section and vault validation (documentation only)

## Goal

Document the Obsidian workflow as a format contract; verify the generated wiki opens as a plugin-free vault.

## Background

Spec sections 13, 14, 15, 32 (README part only), 34-P2 Obsidian. GitHub Pages site and logo redesign are out of scope for 0.4.0 core.

## Required Behavior

- README gains an Obsidian section: open `repo/wiki/` as vault, named indexes as graph hubs, backlinks, no plugins required; front matter conventions documented in wiki-rules.
- Verify generated wikilinks are plain `[[...]]` and YAML front matter parses.

## Acceptance Criteria

- Fresh generated wiki opens in Obsidian semantics: every folder has a named index hub; no Dataview/Templater dependency.

## Result

README documents opening `wiki/` as an Obsidian vault, named-index hubs,
backlinks, and plugin-free use. `wiki/wiki-rules.md` and its template document
wikilink and YAML front-matter conventions. Visual Obsidian launch remains
unverified because the application is not installed locally.

## Validation

Fresh `lliki init` plus task/note/exploration creation: five named indexes,
15 generated wikilinks with existing targets, three YAML front matters parsed,
no `.obsidian` plugin configuration. `lliki doctor`: 0 errors; three expected
`needs-context` warnings for fresh project-specific templates.

Remaining incomplete: vault-opening visual check (`Needs validation` on an
Obsidian-capable machine). Lesson LL-005: a clean doctor run does not prove
task reachability when statuses are exempted.

Re-verified 2026-09-29 after LLIKI-050: fresh init + task/note/exploration
yields five named indexes, 11 generated wikilinks (count changed with the
resume-route removal), all targets existing, three YAML front matters, no
`.obsidian` config, doctor 0 errors / three `needs-context` warnings.
