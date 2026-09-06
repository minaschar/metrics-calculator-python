# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once it has a
released version. The version lives in `pyproject.toml` and is exposed as
`metrics_calculator.__version__`.

## [Unreleased]

Complete rebuild of the tool from a pre-packaging research script into an
installable Python package with a CLI and a desktop app. The metric definitions
are preserved; their implementations were audited and their known defects fixed.

### Added

- `metrics_calculator` package with `analyze(path, config) -> ProjectMetrics` as
  the entire public API and zero runtime dependencies in the core.
- A **metric registry** — one entry per metric (name, category, description,
  formula as implemented, source paper) driving the CLI headers, every export
  format, the desktop manual and `docs/metrics.md`.
- `metrics-calculator` CLI (`analyze`, `diff`) with CSV / JSON / HTML / XLSX
  output, `--fail-under` gates and configurable include/exclude globs.
- `metrics-calculator-gui` PySide6 desktop app: off-thread analysis with
  progress and cancel, a model/view results table with threshold and outlier
  colouring, distribution histograms, source drill-down, a diagnostics panel and
  a registry-generated manual, with a PyInstaller build.
- `uv`-managed environment, `pyproject.toml` + lockfile, `pytest` / `ruff` /
  `mypy` / `pre-commit`, and GitHub Actions across Python 3.11–3.13 plus a
  packaging job for Windows and macOS.
- Golden-snapshot regression suite over sample-project fixtures.
- `schema_version` field in the `analyze --format json` output.

### Fixed (metric values move — see the snapshot diffs)

- **DIT** is now a pure function of a class and its ancestors: `0` at the root,
  `1 + max(DIT of project bases)` otherwise, with an inheritance-cycle guard.
  The original misdirected its result onto an ancestor and returned `-1` for a
  single recursed parent.
- **MPC / CBO** no longer multiply a call site by the number of files defining a
  method of that name.
- **MPC / CBO** no longer count attribute *reads* (`f(obj.attr)`) as calls;
  only attributes in call position count.
- `async def` methods are now visible to NOM, WMPC1, WMPC2, RFC, LCOM and CC.
- **LCOM** uses a per-method field set that stops at nested functions and
  classes, instead of one accumulator shared and cleared between methods.
- **WAC / SIZE2** now count `x: int = 0` and `x += 1` class attributes.
- Dotted base classes (`class Foo(pkg.Base)`) are now resolved (`-> Base`),
  feeding DIT, NOCC and CBO.
- The scanner no longer descends into the analysed project's `.venv/`,
  `site-packages/`, `__pycache__/`, `node_modules/`, `build/`, `dist/` and
  similar directories by default.

### Removed

- The QMOOD design-quality category (six attributes that were declared but never
  computed — always `0.0`). Recorded as future work in `docs/metrics.md`.
- `app/requirements.txt` (UTF-16 encoded; `pip` could not read it), replaced by
  the `uv`-managed `pyproject.toml`.

The pre-rewrite `app/` package (its `pyuic5` GUI, the old engine and the
Windows-only hardcoded paths) is superseded and slated for deletion.
