# Release Process

This document describes how to generate a new Lliki version. It is a human
release checklist, not an automated command.

## Preconditions

- The working tree contains only intentional release changes.
- PyPI Trusted Publishing is configured for the production project.
- TestPyPI Trusted Publishing is configured if a TestPyPI dry run is desired.
- The version number is chosen before creating the release tag.

The Git tag must point to a commit where package metadata already matches the
tag. For example:

```text
v0.3.0 requires pyproject.toml and src/lliki/__init__.py to say 0.3.0.
```

## Update Version Metadata

Update:

- `pyproject.toml`
- `src/lliki/__init__.py`
- `CHANGELOG.md`

Do not create or push the tag until these changes are committed.

## Local Validation

Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src
python -m build
python -m twine check dist/*
```

If `python -m build` or `python -m twine` is unavailable in the active
environment, install or use the project virtual environment before continuing.

## Optional TestPyPI Check

The repository includes `.github/workflows/test-publish.yml`, which can be run
manually through GitHub Actions. It builds the package, runs Twine checks, and
publishes to TestPyPI through Trusted Publishing.

After TestPyPI publishes, verify install behavior from TestPyPI in a clean
environment. Remember that TestPyPI is for validation only; it is not the
canonical installation channel for users.

## Commit the Release

Commit the version and changelog update:

```bash
git add pyproject.toml src/lliki/__init__.py CHANGELOG.md
git commit -m "Release vX.Y.Z"
```

If documentation or workflow fixes are part of the release, include them in the
same release commit only when they are intentional.

## Create or Recreate the Tag

If the tag does not exist:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

If the tag was created too early and points to the wrong commit:

```bash
git tag -d vX.Y.Z
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

Do not push a tag until it points to the release commit with matching package
metadata.

## Publish

Push `main`, then push the tag:

```bash
git push origin main
git push origin vX.Y.Z
```

Pushing `vX.Y.Z` triggers `.github/workflows/release.yml`. That workflow builds
the distributions, creates `SHA256SUMS`, attaches artifacts to the GitHub
Release, and publishes to PyPI using PyPI Trusted Publishing.

## Post-Release Verification

After GitHub Actions completes:

```bash
python -m pip install --upgrade lliki==X.Y.Z
lliki --version
lliki --help
```

Also verify:

- GitHub Release contains wheel, sdist, and `SHA256SUMS`.
- PyPI shows the expected version.
- A clean install can run `lliki init --default --yes`.

## If Publishing Fails

- If the build failed, fix the source, commit, recreate the tag locally, and
  push the corrected tag only after reviewing the failure.
- If PyPI rejects the version because it already exists, choose a new version;
  PyPI files cannot be replaced.
- If Trusted Publishing fails, verify the PyPI project, repository owner/name,
  workflow name, and environment configuration.
