"""Runs today's analysis pipeline exactly as ``gui/mainWindow.py`` does.

This module exists solely to produce deterministic golden snapshots of the
*current* (pre-rewrite) engine's behaviour, bugs included -- it is the
regression net for the modernization effort described in the project brief,
not part of any public API. It will be deleted once Phase 1 lands a real
``analyze()`` entry point and Phase 4 has verified the rewrite against these
same snapshots.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.entities.the_project import Project
from src.generator.generate_ast import AstGenerator
from src.metrics.calculator.metrics_calculator import MetricsCalculator
from src.visitors.init_visitor import InitCommonsNodeVisitor


def analyze_fixture(fixture_dir: Path) -> dict[str, Any]:
    project = Project(str(fixture_dir), fixture_dir.name)
    AstGenerator(project).start_parsing()

    for python_file_obj in project.get_files():
        InitCommonsNodeVisitor(python_file_obj).visit_Module(python_file_obj.get_generated_ast())

    for python_file_obj in project.get_files():
        for class_obj in python_file_obj.get_file_classes():
            MetricsCalculator(class_obj)

    files_payload = []
    for python_file_obj in sorted(project.get_files(), key=lambda f: f.get_file_name()):
        classes_payload = []
        for class_obj in sorted(
            python_file_obj.get_file_classes(), key=lambda c: c.get_class_name()
        ):
            size = class_obj.get_size_category_metrics()
            complexity = class_obj.get_complexity_category_metrics()
            coupling = class_obj.get_coupling_category_metrics()
            cohesion = class_obj.get_cohesion_category_metrics()
            classes_payload.append(
                {
                    "class_name": class_obj.get_class_name(),
                    "hierarchy": class_obj.get_hierarchy(),
                    "loc": size.get_loc(),
                    "nom": size.get_nom(),
                    "size2": size.get_size2(),
                    "wac": size.get_wac(),
                    "nocc": size.get_nocc(),
                    "dit": complexity.get_dit(),
                    "wmpc1": complexity.get_wmpc1(),
                    "wmpc2": complexity.get_wmpc2(),
                    "rfc": complexity.get_rfc(),
                    "cbo": coupling.get_cbo(),
                    "mpc": coupling.get_mpc(),
                    "lcom": cohesion.get_lcom(),
                }
            )
        files_payload.append(
            {"file_name": python_file_obj.get_file_name(), "classes": classes_payload}
        )

    return {
        "noc": MetricsCalculator.calc_noc(project.get_files()),
        "files": files_payload,
    }
