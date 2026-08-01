---
id: RELEASE-001
title: Publish Lliki as a public GitHub, PyPI, and Homebrew project
status: active
priority: high
updated: 2026-08-01
---
# RELEASE-001: Publish Lliki Publicly

## Goal

Prepare and publish Lliki as a public open-source project owned by
`brunofbloq`, with source on GitHub, package distribution through PyPI, and a
Homebrew tap formula.

## Scope

- Public GitHub source repository: `brunofbloq/lliki` exists, is public, is
  empty at inspection time, and defaults to `main`.
- Python package and CLI: `lliki`.
- Intended release version: `0.2.1`.
- PyPI project: `lliki`.
- Homebrew tap repository: `brunofbloq/homebrew-tap` was not found or not
  accessible at inspection time.
- Homebrew install command: `brew install brunofbloq/tap/lliki`.
- Optional Debian artifact preparation, if tooling is available.

## Confirmed User Decisions

- Work from this current repository folder, not from a fresh ZIP extraction.
- Treat `dist/` as generated release output and exclude it from the source
  commit.
- Treat root `SHA256SUMS` as generated release output. Regenerate checksums from
  final release artifacts in the release workflow instead of committing a
  pre-existing checksum file.
- Avoid personal maintainer email addresses unless a tool or metadata format
  strictly requires one; ask before adding any email.
- External publication actions are authorized in principle after safety
  checkpoints pass, including GitHub pushes/tags, PyPI publishing, and Homebrew
  tap publication. Continue to stop at required manual browser/authentication
  checkpoints.
- Treat Homebrew validation in this environment as syntax/structure-only until
  runtime testing can happen on macOS or Linuxbrew.

## Release Principles

- Do not expose or commit credentials, tokens, keys, private URLs, or private
  information.
- Do not force-push.
- Do not overwrite an existing remote repository.
- Do not create a release tag before GitHub CI passes.
- Do not publish to PyPI before Trusted Publishing is configured and confirmed.
- Do not make the repository public until the source has been reviewed for
  confidential information.
- Ask before irreversible external actions that are not already explicitly
  authorized.
- Prefer PyPI Trusted Publishing over permanent PyPI tokens.
- Keep a concise execution log and checkpoint report after each phase.

## Plan

1. Inspect release candidate and source tree.
   - Confirm actual version, package metadata, CLI entry point, workflows,
     tests, packaging files, templates, and installer scripts.
   - Search for obsolete identifiers and confidential content.
   - Verify GitHub repository availability, Homebrew tap availability, and PyPI
     name ownership/availability.
   - Stop if confidential content is found.

2. Update ownership and public metadata.
   - Normalize ownership to `brunofbloq`.
   - Update GitHub URLs to `https://github.com/brunofbloq/lliki`.
   - Update README installation paths for PyPI, pip, Homebrew, and GitHub.
   - Avoid adding a personal email unless explicitly provided and approved.

3. Validate locally.
   - Run Python syntax checks, unit tests, package build, wheel install,
     CLI smoke tests, default/custom init tests, template availability checks,
     script syntax checks, Homebrew formula Ruby syntax checks, package metadata
     checks, and distribution-content review.
   - Clean temporary files, caches, logs, local-only artifacts, `dist/`, and
     generated root checksum files before committing.

4. Initialize and publish the GitHub source repository.
   - Use the existing public empty repository `brunofbloq/lliki` if it remains
     empty and suitable.
   - Create or repair a clean local Git repository on `main` if needed.
   - Stage and review the full file list before committing.
   - Create `brunofbloq/lliki` as a public repository only after source review.
   - Push the initial public release commit.

5. Verify GitHub CI.
   - Inspect the Actions run triggered by the push.
   - Fix any failures with focused commits.
   - Do not bypass or disable failing checks merely to release.

6. Test remote GitHub installation.
   - Install from `git+https://github.com/brunofbloq/lliki.git` in a clean
     environment.
   - Verify `lliki --version`, `lliki --help`, and a fresh initialization.

7. Configure PyPI Trusted Publishing.
   - Confirm PyPI project `lliki`.
   - Confirm GitHub environment `pypi`.
   - Confirm release workflow uses `environment: pypi` and `id-token: write`.
   - Stop for browser/user confirmation where required before tagging.

8. Publish `v0.2.1`.
   - Confirm local validation, CI, remote install, Trusted Publishing,
     changelog, version metadata, and clean working tree.
   - Tag and push `v0.2.1`.
   - Monitor release workflow.
   - Verify GitHub Release and PyPI installation.

9. Publish the Homebrew tap.
   - Create `brunofbloq/homebrew-tap` if it still does not exist.
   - Generate `Formula/lliki.rb` from the published PyPI source distribution
     URL and SHA-256.
   - Commit, push, and test installation where Homebrew is available.
   - If Homebrew is unavailable locally, validate Ruby syntax and document
     untested runtime status.

10. Optional Debian release preparation.
    - Validate Debian metadata and attempt `.deb` build when tooling exists.
    - Attach a validated `.deb` to the GitHub release if successful.
    - Treat hosted APT repository setup as future work unless explicitly
      approved.

## Required Searches

Review matches rather than blindly replacing all results:

```text
bloqit
bloqit/lliki
bloqit/tap
agent-wiki
agent_wiki
repo-wiki
repo_wiki
.agent-wiki
.repo-wiki
TODO
FIXME
password
secret
token
api_key
private key
BEGIN RSA
BEGIN OPENSSH
```

## Checkpoints

## Execution Log

### 2026-07-31: Checkpoints 1-6 Complete

- **Completed:** Inspected release source, normalized public ownership metadata,
  ran required source scans, validated locally, created initial commit
  `787f416` on `main`, configured `origin` as
  `https://github.com/brunofbloq/lliki.git`, pushed to GitHub, fixed the CI
  Python 3.9 failure, and pushed commit `3ed7a2b`.
- **Files changed:** Public source metadata and release hygiene updates were
  committed. CI fix changed `src/lliki/core/patching.py` to avoid
  Python 3.10+ `Path.write_text(newline=...)`. Local `wiki/` remains ignored
  and uncommitted.
- **Validation:** Unit tests passed; compileall passed; Lliki template
  validation and doctor checks passed; wheel and sdist built; `twine check`
  passed; clean wheel install and init smoke tests passed; GitHub CI run
  `30671402745` passed across Ubuntu, macOS, and Windows for Python 3.9, 3.11,
  and 3.13; remote install from
  `git+https://github.com/brunofbloq/lliki.git` resolved to `3ed7a2b`, installed
  `lliki 0.2.1`, and passed CLI/init/template smoke tests.
- **Unavailable locally:** Bash validation was blocked by Windows/WSL access
  permissions; Ruby/Homebrew runtime validation is unavailable in this
  environment.
- **Warnings:** Build emitted non-blocking setuptools license metadata
  deprecation warnings.
- **Blocker:** Release tag and PyPI publish are blocked until PyPI Trusted
  Publishing is configured and confirmed for this repository.
- **Next action:** Configure PyPI Trusted Publishing for project `lliki` with
  owner `brunofbloq`, repository `lliki`, workflow `release.yml`, and GitHub
  environment `pypi`; then tag and push `v0.2.1`.

### 2026-08-01: TestPyPI Rehearsal Workflow Added

- **Completed:** Added and pushed manual workflow
  `.github/workflows/test-publish.yml` in commit `6b29cd7`.
- **Purpose:** Build distributions, run `twine check`, upload artifacts, and
  publish to TestPyPI through Trusted Publishing using environment `testpypi`.
- **Blocker:** TestPyPI account-side pending Trusted Publisher must be created
  by the project owner before the manual workflow can publish.
- **Next action:** In TestPyPI, add GitHub Trusted Publisher with project
  `lliki`, owner `brunofbloq`, repository `lliki`, workflow
  `test-publish.yml`, and environment `testpypi`; then run the manual GitHub
  workflow.

### 2026-08-01: TestPyPI Rehearsal Passed

- **Completed:** TestPyPI workflow run `30672584779` completed successfully.
- **Validation:** Clean install from TestPyPI with
  `lliki==0.2.1` succeeded; `lliki --version`, `lliki init --help`, default
  initialization, and `lliki templates validate` passed.
- **Next action:** Configure real PyPI Trusted Publishing for project `lliki`
  with owner `brunofbloq`, repository `lliki`, workflow `release.yml`, and
  environment `pypi`; then tag and push `v0.2.1`.

### 2026-08-01: GitHub Release and PyPI Publish Passed

- **Completed:** Created and pushed annotated tag `v0.2.1` at commit
  `6b29cd75412d13a978478cda30895f2b27854854`.
- **Validation:** Release workflow run `30704668030` completed successfully;
  both `build` and `publish-pypi` jobs passed.
- **Published resources:** GitHub Release
  `https://github.com/brunofbloq/lliki/releases/tag/v0.2.1`; PyPI package
  `https://pypi.org/project/lliki/0.2.1/`.
- **Artifacts:** GitHub Release contains `lliki-0.2.1-py3-none-any.whl`,
  `lliki-0.2.1.tar.gz`, and `SHA256SUMS`.
- **Install verification:** Clean real-PyPI install of `lliki==0.2.1`
  succeeded; `lliki --version`, `lliki --help`, default initialization, and
  `lliki templates validate` passed.
- **Next action:** Publish the Homebrew tap formula using the PyPI source
  distribution URL and SHA-256.

### 2026-08-01: Homebrew Formula Prepared

- **Prepared formula:** Rendered `dist/lliki.rb` from
  `packaging/homebrew/Formula/lliki.rb.in`.
- **Source distribution URL:**
  `https://files.pythonhosted.org/packages/37/c7/6f42ed7a1b2a6878bd4e0625a6d650ddbed4680651220dfbb210232624ce/lliki-0.2.1.tar.gz`.
- **SHA-256:**
  `2b0860be49f173c2ad227c3f6b0e49f3e4371b5cc7fc3f5eab9bdeccd6d6fa50`.
- **Structure validation:** Formula checks passed for class name, virtualenv
  helper, homepage, PyPI source URL, SHA-256, `python@3.13` dependency,
  install block, and smoke-test block.
- **Runtime validation:** Ruby and Homebrew are not available in this Windows
  environment, so `brew audit`, `brew install`, and `brew test` remain deferred
  to macOS/Linuxbrew as previously agreed.
- **Current blocker:** `brunofbloq/homebrew-tap` still returns 404 from the
  GitHub API/connector, and the available GitHub connector can create files only
  in an existing repository. Create the public empty tap repository, then publish
  `Formula/lliki.rb`.

### Checkpoint 1: Release Candidate Inspection

Report detected version, package and CLI identifiers, obsolete identifiers,
confidential-content findings, repository availability, PyPI name status, and
blockers requiring user input.

### Checkpoint 2: Metadata Update

Report metadata files changed, remaining old ownership references, license and
author metadata status, and required user decisions.

### Checkpoint 3: Local Validation

Report exact results for tests, build, wheel installation, default/custom init,
Bash validation, PowerShell validation, Homebrew syntax, secret scan, and
remaining warnings.

### Checkpoint 4: GitHub Repository

Report repository creation, visibility, default branch, pushed commit SHA,
GitHub Actions status, and repository settings still requiring configuration.

### Checkpoint 5: GitHub CI

Report workflow URL, jobs executed, passed/failed jobs, fixes made, and final CI
status.

### Checkpoint 6: Remote GitHub Install

Report remote install result, installed version, initialization result, and any
packaging/template-resource issues.

### Checkpoint 7: PyPI Trusted Publishing

Report PyPI name status, Trusted Publisher status, GitHub `pypi` environment
status, release workflow readiness, and remaining user action.

### Checkpoint 8: Release Publish

Report tag SHA, release workflow result, GitHub Release URL, PyPI project URL,
package artifacts, pipx installation result, and published version.

### Checkpoint 9: Homebrew Tap

Report tap repository creation, formula commit SHA, source URL and SHA used,
Homebrew test results, and final installation command.

## Definition of Done

- [x] All ownership references use `brunofbloq`.
- [x] No obsolete `bloqit/lliki` or `bloqit/tap` references remain.
- [x] No confidential information is present in the public source.
- [ ] The source tree is clean.
- [x] All automated tests pass.
- [x] Wheel and source distribution build successfully.
- [x] The wheel installs and runs in a clean environment.
- [x] `brunofbloq/lliki` exists as a public repository.
- [x] GitHub CI passes.
- [x] Installation directly from GitHub succeeds.
- [x] PyPI Trusted Publishing is configured.
- [x] GitHub release `v0.2.1` is published.
- [x] PyPI package `lliki==0.2.1` is published and installable.
- [ ] `brunofbloq/homebrew-tap` exists publicly.
- [ ] The Lliki Homebrew formula is published.
- [ ] Homebrew installation is tested, or untested status is documented.
- [x] README installation instructions are accurate.
- [x] Manual configuration steps are documented.
- [ ] Final repository, release, PyPI, and Homebrew links are provided.

## External Actions Requiring Confirmation

- Replacing, deleting, or overwriting an existing remote repository.
- Creating or making public `brunofbloq/homebrew-tap`.
- Adding remotes or pushing commits/tags to GitHub.
- Creating GitHub releases.
- Publishing to PyPI.
- Publishing or pushing Homebrew tap formula changes.
- Using any fallback PyPI credential/token approach instead of Trusted
  Publishing.

## Open Questions

- No blocking planning questions remain. New questions should be raised only
  when discovered during checkpoint execution.

## Evidence

- Source brief: Codex attachment
  `6b176d2b-560e-4762-9a09-c9826e6e1a8d/pasted-text.txt`.
- GitHub connector inspection on 2026-07-31:
  `brunofbloq/lliki` exists as a public empty repository; connector returned
  404 for `brunofbloq/homebrew-tap`.
- Current project context: [[../docs/project-overview|Project Overview]],
  [[../docs/development-workflow|Development Workflow and Commands]],
  [[../docs/repository-rules|Repository Rules and Protected Paths]].
