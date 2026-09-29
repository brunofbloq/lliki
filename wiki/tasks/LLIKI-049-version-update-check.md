---
id: LLIKI-049
title: PyPI update detection with cached lazy policy
status: done
priority: high
created: 2026-09-29
updated: 2026-09-29
baseline_commit: 4f7bbfac104836d8c13d011c2b3606699affb171
---
# LLIKI-049-version-update-check: PyPI update detection with cached lazy policy

## Goal

`lliki version --check`, background update notice honoring the 3rd-launch/24h policy, `LLIKI_NO_UPDATE_CHECK=1`.

## Background

Spec section 19. Stdlib urllib only, no new dependency, no repo data transmitted, failures silent.

## Required Behavior

- Cache in user-level `~/.lliki-update-check.json` with launch count and last-check timestamp; first two launches make no request; thereafter at most once per 24h.
- `version --check` forces a query and prints result.

## Acceptance Criteria

- Tests with injected fetcher prove the policy without network.

## Result

`lliki version --check` and the background update notice honor the 3rd-launch/24h policy with `LLIKI_NO_UPDATE_CHECK=1`; cache in `~/.lliki-update-check.json`; stdlib urllib only, failures silent.

## Validation

44/44 tests pass; `lliki doctor` 0 errors 0 warnings; tests with an injected fetcher prove the policy without network.
