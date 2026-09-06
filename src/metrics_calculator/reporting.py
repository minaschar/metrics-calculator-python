"""Export a `ProjectMetrics` result to JSON, CSV, HTML or XLSX.

Every format is driven by `METRIC_REGISTRY` for column headers and value
lookup -- add a metric to the registry and every format picks it up. Lives
at package root (not under `cli/`) because the CLI and the desktop app are
both consumers.

Two layers:

- ``to_rows`` flattens a ``ProjectMetrics`` into a list of ``{column:
  value}`` dicts (file_name, class_name, then one key per registry
  metric).
- the ``rows_to_*`` writers take that row list directly. ``to_csv`` /
  ``to_html`` / ``to_xlsx`` are thin wrappers over them for the common
  "whole result" case.

The desktop app exports the *rows its table model is currently showing*
(filtered and sorted) by handing those rows straight to ``rows_to_csv`` /
``rows_to_xlsx`` -- it never scrapes text back out of widget cells.
"""

from __future__ import annotations

import csv
import html
import io
import json
from collections.abc import Sequence
from pathlib import Path

from .registry import METRIC_REGISTRY
from .results import ClassMetrics, ProjectMetrics

_ROW_HEADER = ("file_name", "class_name")
FIELDNAMES: tuple[str, ...] = (*_ROW_HEADER, *METRIC_REGISTRY)

Row = dict[str, object]


def _row(class_metrics: ClassMetrics) -> Row:
    row: Row = {
        "file_name": class_metrics.file_name,
        "class_name": class_metrics.class_name,
    }
    for definition in METRIC_REGISTRY.values():
        row[definition.abbreviation] = definition.accessor(class_metrics)
    return row


def to_rows(project_metrics: ProjectMetrics) -> list[Row]:
    return [_row(cm) for file_metrics in project_metrics.files for cm in file_metrics.classes]


def rows_to_csv(rows: Sequence[Row]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(FIELDNAMES))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def rows_to_html(rows: Sequence[Row], *, title: str, summary: str = "") -> str:
    header_cells = "".join(f"<th>{html.escape(name)}</th>" for name in FIELDNAMES)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(row[name]))}</td>" for name in FIELDNAMES)
        body_rows.append(f"<tr>{cells}</tr>")
    summary_html = f"<p>{html.escape(summary)}</p>" if summary else ""
    return (
        "<!doctype html><meta charset='utf-8'>"
        f"<title>Metrics: {html.escape(title)}</title>"
        "<style>table{border-collapse:collapse}"
        "th,td{border:1px solid #ccc;padding:4px 8px;text-align:right}"
        "th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}</style>"
        f"<h1>{html.escape(title)}</h1>"
        f"{summary_html}"
        f"<table><thead><tr>{header_cells}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"
    )


def rows_to_xlsx(rows: Sequence[Row], output_path: Path) -> None:
    # Imported lazily: pandas/openpyxl are an optional extra, not a core
    # dependency.
    import pandas as pd

    frame = pd.DataFrame(list(rows), columns=list(FIELDNAMES))
    frame.to_excel(output_path, index=False)


# Bump when the JSON export shape changes in a way consumers must notice.
JSON_SCHEMA_VERSION = 1


def to_json(project_metrics: ProjectMetrics) -> str:
    payload = {
        "schema_version": JSON_SCHEMA_VERSION,
        "project_name": project_metrics.project_name,
        "root_path": project_metrics.root_path,
        "noc": project_metrics.noc,
        "diagnostics": [
            {"path": str(d.path), "message": d.message, "severity": d.severity}
            for d in project_metrics.diagnostics
        ],
        "files": [
            {
                "file_name": file_metrics.file_name,
                "classes": [_row(cm) for cm in file_metrics.classes],
            }
            for file_metrics in project_metrics.files
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def to_csv(project_metrics: ProjectMetrics) -> str:
    return rows_to_csv(to_rows(project_metrics))


def to_html(project_metrics: ProjectMetrics) -> str:
    summary = f"{project_metrics.noc} classes across {len(project_metrics.files)} files"
    return rows_to_html(
        to_rows(project_metrics),
        title=project_metrics.project_name,
        summary=summary,
    )


def to_xlsx(project_metrics: ProjectMetrics, output_path: Path) -> None:
    rows_to_xlsx(to_rows(project_metrics), output_path)
