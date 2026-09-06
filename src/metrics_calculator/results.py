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


@dataclass(slots=True)
class CouplingMetrics:
    cbo: int = 0
    mpc: int = 0


@dataclass(slots=True)
class CohesionMetrics:
    lcom: int = 0


# Phase 5, item 10: the original declared a QMOOD category with six
# Bansiya & Davis (2002) design attributes (reusability, flexibility,
# understandability, functionality, extendability, effectiveness) that
# nothing ever computed -- always 0.0, never displayed. They are dropped
# here rather than carried as dead fields; implementing QMOOD properly is
# recorded as future work (see the roadmap / CHANGELOG).


@dataclass(slots=True)
class ClassMetrics:
    class_name: str
    file_name: str
    size: SizeMetrics = field(default_factory=SizeMetrics)
    complexity: ComplexityMetrics = field(default_factory=ComplexityMetrics)
    coupling: CouplingMetrics = field(default_factory=CouplingMetrics)
    cohesion: CohesionMetrics = field(default_factory=CohesionMetrics)


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
