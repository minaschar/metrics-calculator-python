"""Runs the new `metrics_calculator.analyze()` engine and serialises its
output to the same shape as `_analysis_harness.py` (the legacy engine),
so both can be checked against the same committed golden snapshots.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from metrics_calculator import AnalysisConfig, analyze


def analyze_fixture(fixture_dir: Path) -> dict[str, Any]:
    result = analyze(fixture_dir, AnalysisConfig())

    files_payload = []
    for file_metrics in sorted(result.files, key=lambda f: f.file_name):
        classes_payload = []
        for class_metrics in sorted(file_metrics.classes, key=lambda c: c.class_name):
            classes_payload.append(
                {
                    "class_name": class_metrics.class_name,
                    # The original tool always wrote `dit` and `hierarchy`
                    # together with the identical value in every branch of
                    # calc_dit -- they were redundant storage of the same
                    # number. `dit` here reproduces that invariant.
                    "hierarchy": class_metrics.complexity.dit,
                    "loc": class_metrics.size.loc,
                    "nom": class_metrics.size.nom,
                    "size2": class_metrics.size.size2,
                    "wac": class_metrics.size.wac,
                    "nocc": class_metrics.size.nocc,
                    "dit": class_metrics.complexity.dit,
                    "wmpc1": class_metrics.complexity.wmpc1,
                    "wmpc2": class_metrics.complexity.wmpc2,
                    "rfc": class_metrics.complexity.rfc,
                    "cbo": class_metrics.coupling.cbo,
                    "mpc": class_metrics.coupling.mpc,
                    "lcom": class_metrics.cohesion.lcom,
                }
            )
        files_payload.append({"file_name": file_metrics.file_name, "classes": classes_payload})

    return {"noc": result.noc, "files": files_payload}
