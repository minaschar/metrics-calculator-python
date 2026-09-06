"""Export a `ProjectMetrics` result to JSON, CSV, HTML or XLSX.

Every format is driven by `METRIC_REGISTRY` for column headers and value
lookup -- add a metric to the registry and every format picks it up.
"""

from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path

from ..registry import METRIC_REGISTRY
from ..results import ClassMetrics, ProjectMetrics

_ROW_HEADER = ("file_name", "class_name")


def _row(class_metrics: ClassMetrics) -> dict[str, object]:
    row: dict[str, object] = {
        "file_name": class_metrics.file_name,
        "class_name": class_metrics.class_name,
    }
    for definition in METRIC_REGISTRY.values():
        row[definition.abbreviation] = definition.accessor(class_metrics)
    return row


def to_rows(project_metrics: ProjectMetrics) -> list[dict[str, object]]:
    return [_row(cm) for file_metrics in project_metrics.files for cm in file_metrics.classes]


def to_json(project_metrics: ProjectMetrics) -> str:
    payload = {
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
    fieldnames = [*_ROW_HEADER, *METRIC_REGISTRY]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(to_rows(project_metrics))
    return buffer.getvalue()


def to_html(project_metrics: ProjectMetrics) -> str:
    fieldnames = [*_ROW_HEADER, *METRIC_REGISTRY]
    header_cells = "".join(f"<th>{html.escape(name)}</th>" for name in fieldnames)
    body_rows = []
    for row in to_rows(project_metrics):
        cells = "".join(f"<td>{html.escape(str(row[name]))}</td>" for name in fieldnames)
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        "<!doctype html><meta charset='utf-8'>"
        f"<title>Metrics: {html.escape(project_metrics.project_name)}</title>"
        "<style>table{border-collapse:collapse}"
        "th,td{border:1px solid #ccc;padding:4px 8px;text-align:right}"
        "th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}</style>"
        f"<h1>{html.escape(project_metrics.project_name)}</h1>"
        f"<p>{project_metrics.noc} classes across {len(project_metrics.files)} files</p>"
        f"<table><thead><tr>{header_cells}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"
    )


def to_xlsx(project_metrics: ProjectMetrics, output_path: Path) -> None:
    # Imported lazily: pandas/openpyxl are an optional `cli` extra, not a
    # core dependency.
    import pandas as pd

    fieldnames = [*_ROW_HEADER, *METRIC_REGISTRY]
    frame = pd.DataFrame(to_rows(project_metrics), columns=fieldnames)
    frame.to_excel(output_path, index=False)
