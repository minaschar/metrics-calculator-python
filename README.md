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
