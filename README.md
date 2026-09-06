# metrics-calculator-python

Object-oriented software quality metrics for Python projects, computed from the
`ast`. It implements the Chidamber & Kemerer suite (DIT, RFC, NOC, CBO, LCOM),
the Li & Henry maintainability metrics (MPC, SIZE2, WAC) and the related size /
complexity counts (LOC, NOM, NOCC, WMPC1, WMPC2).

Every reported value, with the formula **as actually implemented** (which is not
always the textbook definition), is in [`docs/metrics.md`](docs/metrics.md).

It ships three ways to use it: a Python API (`analyze(...)`), a command-line tool
(`metrics-calculator`), and a desktop app (`metrics-calculator-gui`).

---

## Run it

Requires **Python 3.11, 3.12 or 3.13**. The project is not on PyPI yet, so install
from the Git repository.

### With `pipx` (recommended for the command-line / desktop tools)

```sh
pipx install "metrics-calculator-python[cli] @ git+https://github.com/minaschar/metrics-calculator-python.git"
# for the desktop app instead:
pipx install "metrics-calculator-python[cli,gui] @ git+https://github.com/minaschar/metrics-calculator-python.git"
```

### With `pip` into a virtualenv

```sh
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install "metrics-calculator-python[cli,gui] @ git+https://github.com/minaschar/metrics-calculator-python.git"
```

Extras: `cli` pulls in Typer/Rich/pandas/openpyxl for the command-line tool and
`.xlsx` export; `gui` pulls in PySide6 for the desktop app. The bare core (the
`analyze()` API) has **no dependencies** beyond the standard library.

### Command line

```sh
metrics-calculator analyze path/to/project                    # Rich table on stdout
metrics-calculator analyze path/to/project -f json -o out.json # table | json | csv | html | xlsx
metrics-calculator analyze path/to/project --fail-under RFC=40 --fail-under CBO=15
metrics-calculator diff old_run new_run                        # dir-or-JSON vs dir-or-JSON
metrics-calculator --help
```

- `--fail-under METRIC=MAX` (repeatable) makes it a CI quality gate.
- `diff` compares two runs; each side is a project directory (analysed on the
  spot) or a JSON file previously written with `analyze -f json`.
- Scope with `--include` / `--exclude` glob options, or a
  `[tool.metrics_calculator]` table in the target project's `pyproject.toml`
  (or a standalone `metrics-calculator.toml`). By default the scanner skips
  `.venv/`, `site-packages/`, `__pycache__/`, `node_modules/`, `build/`, `dist/`
  and similar.
- **Exit codes:** `0` success · `1` a `--fail-under` threshold was exceeded (or
  `diff` found changes) · `2` bad usage.
- The `-f json` payload carries `"schema_version": 1`; per-class rows are keyed by
  the metric abbreviations.

### Desktop app

```sh
metrics-calculator-gui                 # or: python -m metrics_calculator.gui
metrics-calculator-gui path/to/project
```

Pick a project; analysis runs off the UI thread with a progress bar and Cancel.
Results land in a sortable / filterable table with threshold and outlier
colouring, plus per-metric distribution histograms, drill-down from a class to
its source, a diagnostics panel and a registry-generated metrics manual.
Light / dark theme, remembered between runs.

### Python API

```python
from metrics_calculator import analyze, AnalysisConfig

result = analyze("path/to/project", AnalysisConfig())
for file in result.files:
    for cls in file.classes:
        print(cls.class_name, cls.complexity.dit, cls.cohesion.lcom)

for diag in result.diagnostics:  # files that were skipped / could not parse
    print(diag)
```

`analyze(path, config) -> ProjectMetrics` is the whole public surface; it imports
no UI code.

---

## Develop it

### Prerequisites

- Python 3.11–3.13
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — manages the
  virtualenv, the lockfile and every dev command

### Set up

```sh
git clone https://github.com/minaschar/metrics-calculator-python.git
cd metrics-calculator-python
uv sync --all-extras            # creates .venv with core + cli + gui + dev tools
uv run pre-commit install       # optional: run the checks on every commit
```

### Everyday commands

```sh
uv run metrics-calculator analyze .          # run the CLI against this repo
uv run metrics-calculator-gui .              # run the desktop app

uv run pytest                                # tests
uv run ruff check .                          # lint
uv run ruff format --check .                 # formatting (drop --check to apply)
uv run mypy                                  # types (strict)
```

CI runs exactly `uv run ruff check .`, `uv run ruff format --check .`,
`uv run mypy` and `uv run pytest -v` on Python 3.11 / 3.12 / 3.13; `pre-commit`
runs the same tools through `uv` so versions match the lockfile.

### When you change a metric

```sh
uv run python -m metrics_calculator.docs                       # refresh docs/metrics.md
SNAPSHOT_UPDATE=1 uv run pytest tests/test_engine_snapshots.py # re-record fixture snapshots
uv run pytest tests/test_engine_snapshots.py                   # then review the diff
```

`docs/metrics.md` and `tests/snapshots/*.json` are committed and checked by tests;
never hand-edit them. Metric abbreviations (LOC, NOM, SIZE2, …) are frozen.

### Build the desktop binary

```sh
uv run pyinstaller --clean --noconfirm packaging/metrics-calculator-gui.spec
# -> dist/MetricsCalculator[.exe]
```

### More

Architecture, the package layout and how to add a metric (one registry entry) are
in [CONTRIBUTING.md](CONTRIBUTING.md). Release notes are in
[CHANGELOG.md](CHANGELOG.md).

---

## Supported syntax and limitations

- Parses with the running interpreter's `ast`; a file with a syntax error is
  skipped and reported as a diagnostic.
- `async def` methods, comprehensions and `match` statements are handled.
- **Coupling is name-based.** Remote calls and base classes are matched by name,
  with no type resolution, so a local variable and an unrelated class that share
  a name are conflated — inherent to the C&K / Li–Henry approximations, and
  called out per metric in `docs/metrics.md`.
- Cyclomatic complexity is approximate: control-flow keywords and `match` cases
  count; `and` / `or` / `except` / `assert` do not.
- DIT counts only inheritance within the analysed project.

## Not implemented (future work)

- **QMOOD design-quality attributes** (Bansiya & Davis 2002). The original tool
  declared six of them but never computed them; they were removed rather than
  kept as always-zero fields, and are listed as future work.
- **Technical-debt scoring.** No such model has ever existed in this codebase,
  despite an earlier project blurb; the GitHub repository description should be
  updated to drop that claim.

## Licence

EPL-2.0. See [LICENSE](LICENSE).
