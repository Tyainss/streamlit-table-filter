# Contributing to streamlit-table-filter

Thank you for contributing to `streamlit-table-filter`.

This guide covers the expected development workflow. For installation and usage, see [README.md](README.md).

## Before contributing

Before opening an issue or pull request, check whether the topic has already been reported and keep each contribution focused on one problem.

A useful bug report should include:

* expected and actual behavior
* steps to reproduce, preferably with a minimal Streamlit example
* the error message or traceback, if applicable
* Python, Streamlit, and package versions
* browser and operating system, if relevant

## Development workflow

1. Create a branch from the latest `main`.
2. Make one focused change.
3. Add or update tests when behavior changes.
4. Update documentation or `CHANGELOG.md` when users need to know about the change.
5. Run the local checks.
6. Open a pull request into `main`.

Avoid combining unrelated fixes, features, dependency updates, and refactors in the same pull request.

## Branch names

Use short, clear branch names.

```text
feature/short-description
fix/short-description
docs/short-description
chore/short-description
release/vX.Y.Z
```

Examples:

```text
feature/custom-selection-label
fix/selection-persistence
docs/update-usage-examples
chore/refresh-dependencies
```

Use `release/` branches only for release preparation.

## Commit messages

Use short commit messages that explain the purpose of the change.

Recommended format:

```text
:emoji: Short description
```

Recommended prefixes:

| Prefix        | Emoji | Use for                                  | Example                                      |
| ------------- | ----- | ---------------------------------------- | -------------------------------------------- |
| `:sparkles:`  | ✨     | New features or user-facing improvements | `:sparkles: Add custom selection labels`     |
| `:memo:`      | 📝    | Documentation                            | `:memo: Update usage examples`               |
| `:wrench:`    | 🛠️   | Configuration, tooling, or CI/CD         | `:wrench: Enforce Ruff formatting in CI`     |
| `:test_tube:` | 🧪    | Tests                                    | `:test_tube: Add selection reset tests`      |
| `:bug:`       | 🐛    | Bug fixes                                | `:bug: Fix selection persistence`            |
| `:rocket:`    | 🚀    | Release preparation                      | `:rocket: Prepare v0.2.0 release`           |
| `:package:`   | 📦    | Package publishing or dependency changes | `:package: Update Streamlit dependency`      |
| `:truck:`     | 🚚    | Moving or renaming code or files         | `:truck: Move shared test helpers`          |
| `:fire:`      | 🔥    | Removing code or files                   | `:fire: Remove unused helper`               |
| `:recycle:`   | ♻️    | Refactoring without behavior changes     | `:recycle: Simplify option validation`       |
| `:lock:`      | 🔒    | Security-related changes                 | `:lock: Update vulnerable dependency`       |

Keep commits logically focused. Separate implementation, tests, documentation, and CI changes when that makes the history clearer.

## Local setup

Install the project and development dependencies:

```bash
uv sync --dev
```

To include optional Polars support:

```bash
uv sync --dev --extra polars
```

## Dependencies

Use `uv` to manage dependencies.

```bash
uv add package-name
uv add --dev package-name
uv add --optional extra-name package-name
```

When dependencies change, commit both `pyproject.toml` and `uv.lock`. Do not edit `uv.lock` manually. Avoid adding dependencies unless they provide clear value.

## Code quality checks

Before opening a pull request, run:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

To reproduce the CI formatting check without modifying files:

```bash
uv run ruff format --check .
```

If package metadata, dependencies, imports, or package structure changed, also run:

```bash
uv build --no-sources
```

## Testing

Automated tests live under `tests/`. Add tests to an existing test module when the changed behavior already belongs there. Prefer test names that describe the behavior being protected.

Add or update tests when changing selection and reset behavior, state across reruns, handling of changing options, input validation, or the public API.

For changes affecting Polars support or DataFrame handling, also run:

```bash
uv run --extra polars pytest
```

For changes affecting the widget's appearance or interactions, test them in the browser using the manual testing app:

```bash
uv run --extra polars streamlit run tests/manual_app.py
```

Use `examples/demo.py` to check the widget in a dashboard. Keep the demo focused on usage rather than testing edge cases.

## Documentation and changelog

Update:

* `README.md` when installation, usage, or public API behavior changes
* `CONTRIBUTING.md` when the development workflow changes
* `CHANGELOG.md` for user-visible changes

Add user-visible changes under `## [Unreleased]`.

Tests, formatting, CI-only changes, and internal refactors normally do not need changelog entries.

## Pull requests

Open pull requests into `main` and include a short summary of the problem and solution, the checks that were run, and the related issue when applicable.

Use a closing keyword (e.g. `Fixes #123`) when the pull request fully resolves an issue.

## Releases

Only maintainers should update package versions, create release branches, or publish releases.

`streamlit-table-filter` follows semantic versioning: PATCH for backward-compatible fixes, MINOR for backward-compatible features, and MAJOR for breaking changes to a stable API. Before v1.0.0, the API may change in minor releases.

1. Update the version in `pyproject.toml` and sync `uv.lock`.
2. Finalize the release section in `CHANGELOG.md`.
3. Merge the changes into `main` and ensure CI passes.
4. Publish a GitHub release with a matching `vX.Y.Z` tag, using the corresponding changelog section as the release notes.
5. Confirm the publishing workflow succeeds and verify the package on PyPI.

Publishing is handled by [release.yml](.github/workflows/release.yml) using PyPI Trusted Publishing. Do not reuse published version tags.
