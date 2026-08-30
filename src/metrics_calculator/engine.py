"""Orchestrates a full analysis run: discover files, extract structural
facts, then compute metrics for every class using a project-wide index
instead of re-walking the whole project per class.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .analysis.cohesion import field_uses_by_method, lack_of_cohesion
from .analysis.complexity import cyclomatic_complexity
from .analysis.loc import lines_of_code
from .analysis.method_calls import remote_method_calls
from .config import AnalysisConfig
from .discovery import discover_files
from .extraction import ClassFacts, FileFacts, extract_classes
from .results import (
    ClassMetrics,
    CohesionMetrics,
    ComplexityMetrics,
    CouplingMetrics,
    FileMetrics,
    ProjectMetrics,
    SizeMetrics,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _ProjectIndex:
    classes: list[ClassFacts]
    classes_by_name: dict[str, list[ClassFacts]]
    files_with_method: dict[str, int]


def _build_index(files: list[FileFacts]) -> _ProjectIndex:
    classes: list[ClassFacts] = []
    classes_by_name: dict[str, list[ClassFacts]] = defaultdict(list)
    files_with_method: dict[str, int] = defaultdict(int)

    for file in files:
        method_names_in_file: set[str] = set()
        for class_facts in file.classes:
            classes.append(class_facts)
            classes_by_name[class_facts.name].append(class_facts)
            method_names_in_file.update(class_facts.methods)
        for name in method_names_in_file:
            files_with_method[name] += 1

    return _ProjectIndex(classes, dict(classes_by_name), dict(files_with_method))


def _children_of(target: ClassFacts, all_classes: list[ClassFacts]) -> list[ClassFacts]:
    return [c for c in all_classes if target.name in c.base_names]


def _resolve_parents(target: ClassFacts, index: _ProjectIndex) -> list[ClassFacts]:
    # Matches every project class whose simple name appears in this class's
    # declared bases -- including duplicates across files with clashing
    # names, a latent correctness gap that isn't in the Phase 5 bug list
    # and is preserved here rather than silently fixed.
    parents: list[ClassFacts] = []
    for base_name in target.base_names:
        parents.extend(index.classes_by_name.get(base_name, ()))
    return parents


def _compute_hierarchy(target: ClassFacts, index: _ProjectIndex, hierarchy: dict[int, int]) -> None:
    """Depth-of-inheritance-tree, keyed by `id(ClassFacts)`.

    This is a faithful, deliberately unfixed port of the original
    `MetricsCalculator.calc_dit` / `return_max_parent_depth`. It reproduces
    two known defects (see project brief Phase 5, items 1-2):

    - the final write can land on whichever ancestor was last recursed
      into (the `current` local below), rather than always being `target`;
    - a freshly-recursed ancestor's depth is never folded into
      `max_parent_depth` in the same pass.

    Fixing this is explicitly out of scope until Phase 5, where each
    defect gets its own commit with a snapshot diff. No cycle guard either,
    matching the original -- also a Phase 5 addition.
    """
    current = target
    children = _children_of(target, index.classes)

    if not target.base_names and not children:
        hierarchy[id(current)] = 0
        return
    if not target.base_names and children:
        hierarchy[id(current)] = 1
        return

    parents = _resolve_parents(target, index)
    max_parent_depth = -2
    for parent in parents:
        depth = hierarchy.get(id(parent))
        if depth is None:
            _compute_hierarchy(parent, index, hierarchy)
            current = parent
        elif depth > max_parent_depth:
            max_parent_depth = depth
    hierarchy[id(current)] = max_parent_depth + 1


def _compute_class_metrics(
    target: ClassFacts,
    index: _ProjectIndex,
    hierarchy: dict[int, int],
    file_lines: tuple[str, ...],
) -> ClassMetrics:
    nom = len(target.methods)
    param_count = sum(len(m.parameters) for m in target.methods.values())
    wac = len(target.fields)
    nocc = len(_children_of(target, index.classes))

    calls = remote_method_calls(target.ast_node, target.name, index.files_with_method)
    distinct_calls = {(c.instance_name, c.method_name) for c in calls}
    instance_names = {c.instance_name for c in calls}

    cc = cyclomatic_complexity(target.ast_node)
    uses_by_method = field_uses_by_method(target.ast_node, frozenset(target.fields))

    size = SizeMetrics(
        loc=lines_of_code(target.ast_node, file_lines),
        nom=nom,
        size2=nom + wac,
        wac=wac,
        nocc=nocc,
    )
    complexity = ComplexityMetrics(
        dit=hierarchy.get(id(target), 0),
        wmpc1=round(cc / nom, 2) if nom else 0.0,
        wmpc2=nom + param_count,
        rfc=nom + len(distinct_calls),
    )
    coupling = CouplingMetrics(
        cbo=len(instance_names | set(target.base_names)) + nocc,
        mpc=len(calls),
    )
    cohesion = CohesionMetrics(lcom=lack_of_cohesion(uses_by_method))

    return ClassMetrics(
        class_name=target.name,
        file_name=target.file_name,
        size=size,
        complexity=complexity,
        coupling=coupling,
        cohesion=cohesion,
    )


def analyze(
    root: str | Path,
    config: AnalysisConfig | None = None,
    *,
    on_progress: Callable[[int, int], None] | None = None,
) -> ProjectMetrics:
    """Analyzes every Python file under `root`.

    `on_progress`, if given, is called as `on_progress(completed, total)`
    once per file after its classes' metrics are computed -- e.g. for a
    CLI progress bar or a future GUI's progress signal. This is the only
    concession to a caller's UI; nothing here imports or assumes one.
    """
    root = Path(root)
    config = config if config is not None else AnalysisConfig.discover(root)

    files, diagnostics = discover_files(root, config)
    for file in files:
        file.classes = extract_classes(file)

    index = _build_index(files)

    hierarchy: dict[int, int] = {}
    for class_facts in index.classes:
        _compute_hierarchy(class_facts, index, hierarchy)

    file_metrics: list[FileMetrics] = []
    total = len(files)
    for completed, file in enumerate(files, start=1):
        metrics = FileMetrics(file_name=file.path.name, file_path=str(file.path))
        for class_facts in file.classes:
            metrics.classes.append(
                _compute_class_metrics(class_facts, index, hierarchy, file.source_lines)
            )
        file_metrics.append(metrics)
        if on_progress is not None:
            on_progress(completed, total)

    return ProjectMetrics(
        project_name=root.name,
        root_path=str(root),
        files=file_metrics,
        noc=len(index.classes),
        diagnostics=diagnostics,
    )
