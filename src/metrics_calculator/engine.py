"""Orchestrates a full analysis run: discover files, extract structural
facts, then compute metrics for every class using a project-wide index
instead of re-walking the whole project per class.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
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


def _count_children(target: ClassFacts, index: _ProjectIndex) -> int:
    """`return_children`: concatenate every class's simple base names
    across the whole project (duplicate class entries for a method-nested
    class included) and count how many equal this class's name."""
    return sum(1 for c in index.classes for name in c.base_names if name == target.name)


def _resolve_parents(target: ClassFacts, index: _ProjectIndex) -> list[ClassFacts]:
    """`convert_to_actual_parent_objects`: project discovery order, one
    entry per (class, matching base name) pair -- so a class listed under
    two of `target`'s bases, or a duplicate class entry, appears twice."""
    return [c for c in index.classes for name in target.base_names if c.name == name]


@dataclass(slots=True)
class _Hierarchy:
    """DIT-computation state, ported verbatim from the original.

    `hier` mirrors `Class.hierarchy` (instance default -1); `dit` mirrors
    `ComplexityCategory.dit` (class-attribute default 0). They usually hold
    the same number, but when a write is misdirected onto an ancestor
    (brief Phase 5, item 1) the class keeps each field's own default.
    """

    hier: dict[int, int] = field(default_factory=dict)
    dit: dict[int, int] = field(default_factory=dict)


def _calc_dit(
    target: ClassFacts, index: _ProjectIndex, state: _Hierarchy, current: list[ClassFacts]
) -> None:
    """Faithful, deliberately unfixed port of `MetricsCalculator.calc_dit`
    / `return_max_parent_depth` (brief Phase 5, items 1-2):

    - the final `set_dit` / `set_hierarchy` land on whichever ancestor the
      recursion last pointed `current` at, not necessarily `target`;
    - a just-recursed ancestor's depth is never folded into
      `max_parent_depth`, so an all-recursed parent list yields the
      sentinel `-2` and DIT `-1`;
    - `hier == -1` means "not computed", so a legitimate `-1` result is
      recomputed every time the class is seen as a parent.

    No cycle guard, matching the original -- a Phase 5 addition.
    """
    current[0] = target
    children = _count_children(target, index)

    if not target.base_names and children == 0:
        state.hier[id(target)] = 0
        state.dit[id(target)] = 0
        return
    if not target.base_names and children != 0:
        state.hier[id(target)] = 1
        state.dit[id(target)] = 1
        return

    max_parent_depth = -2
    for parent in _resolve_parents(target, index):
        if state.hier.get(id(parent), -1) == -1:
            _calc_dit(parent, index, state, current)
        elif state.hier[id(parent)] > max_parent_depth:
            max_parent_depth = state.hier[id(parent)]

    subject = current[0]
    state.hier[id(subject)] = max_parent_depth + 1
    state.dit[id(subject)] = max_parent_depth + 1


def _compute_class_metrics(
    target: ClassFacts,
    index: _ProjectIndex,
    state: _Hierarchy,
    file_lines: tuple[str, ...],
) -> ClassMetrics:
    nom = len(target.methods)
    param_count = sum(len(m.parameters) for m in target.methods.values())
    wac = len(target.fields)
    nocc = _count_children(target, index)

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
        dit=state.dit.get(id(target), 0),
        wmpc1=round(cc / nom, 2) if nom else 0.0,
        wmpc2=nom + param_count,
        rfc=nom + len(distinct_calls),
        hierarchy=state.hier.get(id(target), -1),
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

    # One `calc_dit` per class in discovery order, each with a fresh
    # `current` holder -- the original ran a new MetricsCalculator per
    # class, so its `self.curr_dit_class` reset between classes but not
    # within a class's own recursion.
    state = _Hierarchy()
    for class_facts in index.classes:
        _calc_dit(class_facts, index, state, [class_facts])

    file_metrics: list[FileMetrics] = []
    total = len(files)
    for completed, file in enumerate(files, start=1):
        metrics = FileMetrics(file_name=file.path.name, file_path=str(file.path))
        for class_facts in file.classes:
            metrics.classes.append(
                _compute_class_metrics(class_facts, index, state, file.source_lines)
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
