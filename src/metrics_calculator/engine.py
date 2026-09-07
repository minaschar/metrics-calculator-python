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
    defined_methods: set[str]


def _build_index(files: list[FileFacts]) -> _ProjectIndex:
    classes: list[ClassFacts] = []
    classes_by_name: dict[str, list[ClassFacts]] = defaultdict(list)
    defined_methods: set[str] = set()

    for file in files:
        for class_facts in file.classes:
            classes.append(class_facts)
            classes_by_name[class_facts.name].append(class_facts)
            defined_methods.update(class_facts.methods)

    return _ProjectIndex(classes, dict(classes_by_name), defined_methods)


def _count_children(target: ClassFacts, index: _ProjectIndex) -> int:
    """How many times this class's name appears as a base across the whole
    project. Counts each occurrence, so a class listing the same base
    twice (or a duplicated method-nested class entry) counts twice."""
    return sum(1 for c in index.classes for name in c.base_names if name == target.name)


def _resolve_parents(target: ClassFacts, index: _ProjectIndex) -> list[ClassFacts]:
    """Project classes matching this class's declared base names, in
    discovery order, one entry per (class, matching base) pair."""
    return [c for c in index.classes for name in target.base_names if c.name == name]


def _depth_of_inheritance(
    target: ClassFacts,
    index: _ProjectIndex,
    cache: dict[int, int],
    visiting: frozenset[int] = frozenset(),
) -> int:
    """DIT as a pure function of the class and its ancestors: 0 when no
    base resolves to a project class, otherwise ``1 + max(dit(p))`` over
    the project bases. Independent of iteration order and of whether the
    class has children; an inheritance cycle contributes 0.
    """
    cached = cache.get(id(target))
    if cached is not None:
        return cached
    if id(target) in visiting:
        return 0

    parents = _resolve_parents(target, index)
    if not parents:
        cache[id(target)] = 0
        return 0

    deeper = visiting | {id(target)}
    depth = 1 + max(_depth_of_inheritance(p, index, cache, deeper) for p in parents)
    cache[id(target)] = depth
    return depth


def _compute_class_metrics(
    target: ClassFacts,
    index: _ProjectIndex,
    dit_cache: dict[int, int],
    file_lines: tuple[str, ...],
) -> ClassMetrics:
    nom = len(target.methods)
    param_count = sum(len(m.parameters) for m in target.methods.values())
    wac = len(target.fields)
    nocc = _count_children(target, index)

    calls = remote_method_calls(target.ast_node, target.name, index.defined_methods)
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
        dit=_depth_of_inheritance(target, index, dit_cache),
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
    """Analyse every Python file under ``root`` and return the per-class
    metric table.

    ``on_progress``, if given, is called as ``on_progress(completed,
    total)`` once per file after its classes are computed -- for a CLI
    progress bar or the desktop app's progress signal. It is the only
    concession to a caller's UI; nothing here imports or assumes one.
    """
    root = Path(root)
    config = config if config is not None else AnalysisConfig.discover(root)

    files, diagnostics = discover_files(root, config)
    for file in files:
        file.classes = extract_classes(file)

    index = _build_index(files)
    dit_cache: dict[int, int] = {}

    file_metrics: list[FileMetrics] = []
    total = len(files)
    for completed, file in enumerate(files, start=1):
        metrics = FileMetrics(file_name=file.path.name, file_path=str(file.path))
        for class_facts in file.classes:
            metrics.classes.append(
                _compute_class_metrics(class_facts, index, dit_cache, file.source_lines)
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
