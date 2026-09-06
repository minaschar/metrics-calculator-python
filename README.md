# Metrics Calculator for Python projects (Under construction)

## Development environment

Dependencies and the virtual environment are managed with [uv](https://docs.astral.sh/uv/)
(`pyproject.toml` / `uv.lock` at the repo root — `app/requirements.txt` is gone).

```sh
uv sync              # create .venv and install runtime + dev dependencies
uv run pytest        # run the test suite
uv run ruff check .  # lint
uv run ruff format . # format
uv run mypy          # type-check
```

A full README rewrite (install instructions, CLI usage, limitations) is planned once the
modernization effort lands the new package and CLI.

## Not implemented (future work)

- **QMOOD design-quality attributes** (Bansiya & Davis 2002: reusability, flexibility,
  understandability, functionality, extendability, effectiveness). The original tool declared
  these but never computed them; they were removed rather than kept as always-zero fields.
- **Technical-debt scoring.** Despite an earlier project description, no technical-debt model
  has ever existed in this codebase. (The GitHub repository description should be updated to
  drop that claim.)
