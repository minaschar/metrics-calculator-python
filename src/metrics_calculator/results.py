"""Public output types: the per-class metric table and its project wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field

from .diagnostics import Diagnostic


@dataclass(slots=True)
class SizeMetrics:
    loc: int = 0
    nom: int = 0
    size2: int = 0
    wac: int = 0
    nocc: int = 0


@dataclass(slots=True)
class ComplexityMetrics:
    dit: int = 0
    wmpc1: float = 0.0
    wmpc2: int = 0
    rfc: int = 0
    # Internal DIT-computation state carried over verbatim from the
    # original tool, where `hierarchy` and `dit` were stored separately and
    # usually -- but not always -- held the same number: when the original's
    # `calc_dit` misdirects its write onto an ancestor (project brief Phase
    # 5, item 1), the class keeps `hierarchy = -1` (its instance default)
    # while `dit` keeps `0` (a class-attribute default). Not a published
    # metric, not in the registry, not exported; kept only so the
    # golden-snapshot check stays exact through Phase 4. Phase 5 collapses
    # this back into `dit`.
    hierarchy: int = -1


@dataclass(slots=True)
class CouplingMetrics:
    cbo: int = 0
    mpc: int = 0


@dataclass(slots=True)
class CohesionMetrics:
    lcom: int = 0


@dataclass(slots=True)
class QmoodMetrics:
    """Bansiya & Davis (2002) design-quality attributes.

    Declared for API completeness but never computed -- carried over
    unimplemented from the original tool pending a Phase 5 decision on
    whether to implement them properly or drop them (see project brief).
    """

    reusability: float = 0.0
    flexibility: float = 0.0
    understandability: float = 0.0
    functionality: float = 0.0
    extendability: float = 0.0
    effectiveness: float = 0.0


@dataclass(slots=True)
class ClassMetrics:
    class_name: str
    file_name: str
    size: SizeMetrics = field(default_factory=SizeMetrics)
    complexity: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    coupling: CouplingMetrics = field(default_factory=CouplingMetrics)
    cohesion: CohesionMetrics = field(default_factory=CohesionMetrics)
    qmood: QmoodMetrics = field(default_factory=QmoodMetrics)


@dataclass(slots=True)
class FileMetrics:
    file_name: str
    file_path: str
    classes: list[ClassMetrics] = field(default_factory=list)


@dataclass(slots=True)
class ProjectMetrics:
    project_name: str
    root_path: str
    files: list[FileMetrics] = field(default_factory=list)
    noc: int = 0
    diagnostics: list[Diagnostic] = field(default_factory=list)
