"""Command-line interface: `metrics-calculator analyze` / `... diff`."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..config import AnalysisConfig
from ..engine import analyze
from ..registry import METRIC_REGISTRY
from ..reporting import to_csv, to_html, to_json, to_rows, to_xlsx
from ..thresholds import check_thresholds, parse_threshold_option
from .diff import diff_metric_rows, load_metric_rows

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()
error_console = Console(stderr=True)

_FORMATS = ("table", "json", "csv", "html", "xlsx")


def _build_config(
    config_path: Path | None, include: list[str] | None, exclude: list[str] | None, root: Path
) -> AnalysisConfig:
    base = AnalysisConfig.from_toml(config_path) if config_path else AnalysisConfig.discover(root)
    if include is None and exclude is None:
        return base
    return AnalysisConfig(
        include=tuple(include) if include else base.include,
        exclude=tuple(exclude) if exclude else base.exclude,
        thresholds=base.thresholds,
    )


def _render_table(project_metrics_rows: list[dict[str, object]], project_name: str) -> None:
    table = Table(title=project_name)
    table.add_column("File", style="dim")
    table.add_column("Class")
    for abbreviation in METRIC_REGISTRY:
        table.add_column(abbreviation, justify="right")

    for row in project_metrics_rows:
        table.add_row(
            str(row["file_name"]),
            str(row["class_name"]),
            *(str(row[abbreviation]) for abbreviation in METRIC_REGISTRY),
        )
    console.print(table)


@app.command("analyze")
def analyze_command(
    path: Annotated[
        Path, typer.Argument(exists=True, file_okay=False, help="Project root to analyze.")
    ],
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="table, json, csv, html or xlsx.")
    ] = "table",
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Write to this file instead of stdout.")
    ] = None,
    config_path: Annotated[
        Path | None, typer.Option("--config", help="Explicit TOML config file.")
    ] = None,
    include: Annotated[
        list[str] | None, typer.Option("--include", help="Glob to include (repeatable).")
    ] = None,
    exclude: Annotated[
        list[str] | None, typer.Option("--exclude", help="Glob to exclude (repeatable).")
    ] = None,
    fail_under: Annotated[
        list[str] | None,
        typer.Option(
            "--fail-under", help="METRIC=MAX, repeatable. Exits 1 if any class exceeds MAX."
        ),
    ] = None,
    no_progress: Annotated[bool, typer.Option("--no-progress")] = False,
) -> None:
    """Analyze a project and print or export its per-class metric table."""
    if output_format not in _FORMATS:
        error_console.print(f"error: --format must be one of {', '.join(_FORMATS)}")
        raise typer.Exit(code=2)
    if output_format == "xlsx" and output is None:
        error_console.print("error: --format xlsx requires --output PATH")
        raise typer.Exit(code=2)

    config = _build_config(config_path, include, exclude, path)

    thresholds = dict(config.thresholds)
    if fail_under:
        try:
            for raw in fail_under:
                metric, limit = parse_threshold_option(raw)
                thresholds[metric] = limit
        except ValueError as exc:
            error_console.print(f"error: {exc}")
            raise typer.Exit(code=2) from exc

    if no_progress:
        result = analyze(path, config)
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=error_console,
        ) as progress:
            task = progress.add_task("Analyzing files", total=None)

            def _on_progress(completed: int, total: int) -> None:
                progress.update(task, completed=completed, total=total)

            result = analyze(path, config, on_progress=_on_progress)

    for diagnostic in result.diagnostics:
        error_console.print(str(diagnostic), style="yellow")

    rendered: str | None
    if output_format == "table":
        _render_table(to_rows(result), result.project_name)
        rendered = None
    elif output_format == "json":
        rendered = to_json(result)
    elif output_format == "csv":
        rendered = to_csv(result)
    elif output_format == "html":
        rendered = to_html(result)
    else:
        assert output is not None  # validated above: xlsx requires --output
        to_xlsx(result, output)
        rendered = None

    if rendered is not None:
        if output is not None:
            output.write_text(rendered, encoding="utf-8")
        else:
            # markup=False: this is machine-readable output (json/csv/html);
            # never let Rich interpret a bracketed substring as a style tag.
            console.print(rendered, markup=False, highlight=False, soft_wrap=True)

    violations = check_thresholds(result, thresholds) if thresholds else []
    for violation in violations:
        error_console.print(str(violation), style="red")

    if violations:
        raise typer.Exit(code=1)


@app.command("diff")
def diff_command(
    old: Annotated[Path, typer.Argument(help="Old run: a project directory or exported JSON.")],
    new: Annotated[Path, typer.Argument(help="New run: a project directory or exported JSON.")],
    config_path: Annotated[
        Path | None, typer.Option("--config", help="Explicit TOML config file.")
    ] = None,
    output_format: Annotated[str, typer.Option("--format", "-f", help="table or json.")] = "table",
) -> None:
    """Compare two analysis runs and report added/removed classes and
    metric changes -- point it at two directories, or two files previously
    exported with `analyze --format json`."""
    if output_format not in ("table", "json"):
        error_console.print("error: --format must be table or json")
        raise typer.Exit(code=2)

    config = AnalysisConfig.from_toml(config_path) if config_path else AnalysisConfig()
    old_rows = load_metric_rows(old, config)
    new_rows = load_metric_rows(new, config)
    diff = diff_metric_rows(old_rows, new_rows)

    if output_format == "json":
        import json

        payload = json.dumps(
            {
                "added_classes": [list(k) for k in diff.added_classes],
                "removed_classes": [list(k) for k in diff.removed_classes],
                "changed": [
                    {
                        "file_name": c.file_name,
                        "class_name": c.class_name,
                        "metric": c.metric,
                        "old": c.old,
                        "new": c.new,
                        "delta": c.delta,
                    }
                    for c in diff.changed
                ],
            },
            indent=2,
        )
        console.print(payload, markup=False, highlight=False, soft_wrap=True)
        raise typer.Exit(code=0 if diff.is_empty else 1)

    if diff.is_empty:
        console.print("No differences.")
        raise typer.Exit(code=0)

    for file_name, class_name in diff.added_classes:
        console.print(f"[green]+ {file_name}:{class_name}[/green]")
    for file_name, class_name in diff.removed_classes:
        console.print(f"[red]- {file_name}:{class_name}[/red]")

    if diff.changed:
        table = Table(title="Changed metrics")
        table.add_column("File")
        table.add_column("Class")
        table.add_column("Metric")
        table.add_column("Old", justify="right")
        table.add_column("New", justify="right")
        table.add_column("Delta", justify="right")
        for change in diff.changed:
            style = "red" if change.delta > 0 else "green"
            table.add_row(
                change.file_name,
                change.class_name,
                change.metric,
                str(change.old),
                str(change.new),
                f"[{style}]{change.delta:+g}[/{style}]",
            )
        console.print(table)

    raise typer.Exit(code=1)
