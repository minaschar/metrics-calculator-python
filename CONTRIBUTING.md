# Contributing

## Setup

```sh
uv sync --all-extras          # .venv with core + cli + gui + dev tools
uv run pre-commit install     # optional: run the checks on every commit
```

## Checks (all must pass; CI runs the same on 3.11–3.13)

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

`pre-commit` runs `ruff`, `ruff format` and `mypy` through `uv`, so it uses the
exact versions from `uv.lock`.

## Layout

```
src/metrics_calculator/
  __init__.py        public API: analyze(), the result dataclasses, the registry
  engine.py          orchestration: discover -> extract -> compute
  discovery.py       file walk + parse, with diagnostics
  extraction.py      structural facts per class (methods, fields, bases)
  analysis/          one module per metric family (loc, complexity, cohesion, method_calls)
  registry.py        one entry per metric: name, category, description, formula, source
  reporting.py       ProjectMetrics -> csv / json / html / xlsx (also used by the GUI)
  thresholds.py      --fail-under parsing + evaluation
  docs.py            regenerates docs/metrics.md from the registry
  cli/               Typer command-line app
  gui/               PySide6 desktop app (imports nothing back into the core)
tests/
  fixtures/<name>/   tiny sample projects analysed by the snapshot suite
  snapshots/<name>.json   the expected per-class table for each fixture
```

## Adding a metric

1. Add a field to the relevant dataclass in `results.py` and compute it in
   `engine.py` (or a new module under `analysis/`).
2. Add **one** `MetricDefinition` to `METRIC_DEFINITIONS` in `registry.py` —
   abbreviation, full name, category, description, **`formula`** (what the code
   actually does), `source`, `accessor`, and `notes` for any approximation.
   The CLI table, every export format, the desktop manual and `docs/metrics.md`
   pick it up automatically.
3. `uv run python -m metrics_calculator.docs` to refresh `docs/metrics.md`.
4. `SNAPSHOT_UPDATE=1 uv run pytest tests/test_engine_snapshots.py` to record the
   new column, then review the diff.

Never rename a public abbreviation (LOC, NOM, SIZE2, WAC, NOCC, DIT, WMPC1,
WMPC2, RFC, CBO, MPC, LCOM, NOC) — they are research vocabulary.

## Changing a metric's value

Metric semantics are frozen except by a deliberate, reviewed change. Add a
failing test, make the fix, regenerate the affected snapshots, and show the
snapshot diff in the commit so the movement in measured values is explicit.

## Snapshots

`tests/snapshots/*.json` are the source of truth for the numbers each fixture
produces. Regenerate with `SNAPSHOT_UPDATE=1`; never hand-edit them.
