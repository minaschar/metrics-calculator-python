# metrics-calculator-python

Object-oriented software quality metrics for Python projects, computed from the
`ast`. It implements the Chidamber & Kemerer suite (DIT, RFC, NOC, CBO, LCOM),
the Li & Henry maintainability metrics (MPC, SIZE2, WAC) and the related size /
complexity counts (LOC, NOM, NOCC, WMPC1, WMPC2).

Every reported value, with the formula **as actually implemented** (which is not
always the textbook definition), is in [`docs/metrics.md`](docs/metrics.md).

## Install

```sh
pip install metrics-calculator-python           # core engine + Python API
pip install "metrics-calculator-python[cli]"    # + the command-line tool
pip install "metrics-calculator-python[gui]"    # + the desktop app
pip install "metrics-calculator-python[cli,gui]" # everything (xlsx export needs both)
```

The core engine has **no dependencies** beyond the standard library.

## Python API

```python
from metrics_calculator import analyze, AnalysisConfig

result = analyze("path/to/project", AnalysisConfig())
for file in result.files:
    for cls in file.classes:
        print(cls.class_name, cls.complexity.dit, cls.cohesion.lcom)
```

`analyze(path, config) -> ProjectMetrics` is the whole public surface. It imports
no UI code. Skipped and unparseable files come back in `result.diagnostics`
rather than being printed and dropped.

## Command line

```sh
metrics-calculator analyze path/to/project                 # rich table
metrics-calculator analyze path/to/project -f csv -o m.csv # csv / json / html / xlsx
metrics-calculator analyze path/to/project --fail-under RFC=40 --fail-under CBO=15
metrics-calculator diff old_run new_run                    # dir-or-JSON vs dir-or-JSON
```

- `--fail-under METRIC=MAX` (repeatable) turns the tool into a CI quality gate.
- `diff` compares two runs; each side is a project directory (analysed on the
  spot) or a JSON file previously written with `analyze -f json`.
- `--include` / `--exclude` globs, or a `[tool.metrics_calculator]` table in the
  target project's `pyproject.toml` (or a `metrics-calculator.toml`).

**Exit codes:** `0` success, `1` a `--fail-under` threshold was exceeded (or
`diff` found changes), `2` bad usage.

The `analyze -f json` payload carries `schema_version` (currently `1`); the
per-class rows are keyed by the metric abbreviations.

## Desktop app

```sh
metrics-calculator-gui                 # or: python -m metrics_calculator.gui
metrics-calculator-gui path/to/project
```

A PySide6 app: pick a project, analysis runs off the UI thread with progress and
cancel, results in a sortable/filterable table with threshold and outlier
colouring, per-metric distribution histograms, drill-down from a class to its
source, a diagnostics panel, and a metrics manual generated from the registry.
Light/dark theme. A single-file build is produced by
`pyinstaller packaging/metrics-calculator-gui.spec`.

## Supported syntax and limitations

- Parses with the running interpreter's `ast`; a file with a syntax error is
  skipped and reported as a diagnostic.
- `async def` methods, comprehensions and `match` statements are handled.
- **Coupling is name-based.** Remote calls and base classes are matched by name,
  with no type resolution, so a local variable and an unrelated class that share
  a name are conflated (this is inherent to the C&K/Li-Henry approximations and
  is called out per metric in `docs/metrics.md`).
- Cyclomatic complexity is approximate: control-flow keywords and `match` cases
  count; `and` / `or` / `except` / `assert` do not.
- DIT counts only inheritance within the analysed project.

## Not implemented (future work)

- **QMOOD design-quality attributes** (Bansiya & Davis 2002: reusability,
  flexibility, understandability, functionality, extendability, effectiveness).
  The original tool declared these but never computed them; they were removed
  rather than kept as always-zero fields, and are listed in the manual and
  `docs/metrics.md` as future work.
- **Technical-debt scoring.** No such model has ever existed in this codebase,
  despite an earlier project blurb; the GitHub repository description should be
  updated to drop that claim.

## Development

Dependencies and the virtualenv are managed with
[uv](https://docs.astral.sh/uv/). See [CONTRIBUTING.md](CONTRIBUTING.md).

```sh
uv sync --all-extras
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run mypy
```

## Licence

EPL-2.0. See [LICENSE](LICENSE).
