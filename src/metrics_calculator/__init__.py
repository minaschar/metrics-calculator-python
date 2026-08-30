"""AST-based object-oriented software quality metrics for Python projects.

Public entry point: `analyze(path, config) -> ProjectMetrics`. This package
imports no UI code and has no runtime dependencies beyond the standard
library.
"""

from __future__ import annotations

import logging

from .config import AnalysisConfig
from .diagnostics import Diagnostic
from .engine import analyze
from .registry import (
    METRIC_REGISTRY,
    PROJECT_METRIC_REGISTRY,
    MetricDefinition,
    ProjectMetricDefinition,
)
from .results import (
    ClassMetrics,
    CohesionMetrics,
    ComplexityMetrics,
    CouplingMetrics,
    FileMetrics,
    ProjectMetrics,
    QmoodMetrics,
    SizeMetrics,
)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "METRIC_REGISTRY",
    "PROJECT_METRIC_REGISTRY",
    "AnalysisConfig",
    "ClassMetrics",
    "CohesionMetrics",
    "ComplexityMetrics",
    "CouplingMetrics",
    "Diagnostic",
    "FileMetrics",
    "MetricDefinition",
    "ProjectMetricDefinition",
    "ProjectMetrics",
    "QmoodMetrics",
    "SizeMetrics",
    "analyze",
]
