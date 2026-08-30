"""Single source of truth for every metric: abbreviation, full name,
category, description, source paper and how to read its value off a
computed result. UI headers, exports, docs and the in-app manual are all
meant to read from this instead of hardcoding their own copies (today's
tool has four independent hardcoded lists that have already drifted --
e.g. one UI header reads "WPMC1" instead of "WMPC1").
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .results import ClassMetrics, ProjectMetrics


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    abbreviation: str
    name: str
    category: str
    description: str
    source: str
    accessor: Callable[[ClassMetrics], int | float]


@dataclass(frozen=True, slots=True)
class ProjectMetricDefinition:
    abbreviation: str
    name: str
    description: str
    source: str
    accessor: Callable[[ProjectMetrics], int | float]


def _field(*path: str) -> Callable[[ClassMetrics], int | float]:
    def get(class_metrics: ClassMetrics) -> int | float:
        value: object = class_metrics
        for attr in path:
            value = getattr(value, attr)
        if not isinstance(value, (int, float)):
            raise TypeError(f"registry accessor path {path!r} did not resolve to a number")
        return value

    return get


METRIC_DEFINITIONS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        "LOC",
        "Lines of Code",
        "size",
        "Non-blank lines spanned by the class body.",
        "Chidamber & Kemerer (1994)",
        _field("size", "loc"),
    ),
    MetricDefinition(
        "NOM",
        "Number of Methods",
        "size",
        "Count of methods declared directly on the class.",
        "Chidamber & Kemerer (1994)",
        _field("size", "nom"),
    ),
    MetricDefinition(
        "SIZE2",
        "Number of Properties and Methods",
        "size",
        "NOM plus the number of distinct fields.",
        "Li & Henry (1993)",
        _field("size", "size2"),
    ),
    MetricDefinition(
        "WAC",
        "Weighted Attributes per Class",
        "size",
        "Count of distinct class and instance fields.",
        "Li & Henry (1993)",
        _field("size", "wac"),
    ),
    MetricDefinition(
        "NOCC",
        "Number of Children",
        "size",
        "Count of classes in the project that directly subclass this one.",
        "Chidamber & Kemerer (1994)",
        _field("size", "nocc"),
    ),
    MetricDefinition(
        "DIT",
        "Depth of Inheritance Tree",
        "complexity",
        "Longest inheritance chain above this class.",
        "Chidamber & Kemerer (1994)",
        _field("complexity", "dit"),
    ),
    MetricDefinition(
        "WMPC1",
        "Weighted Methods per Class (complexity)",
        "complexity",
        "Average cyclomatic complexity per method.",
        "Chidamber & Kemerer (1994)",
        _field("complexity", "wmpc1"),
    ),
    MetricDefinition(
        "WMPC2",
        "Weighted Methods per Class (parameters)",
        "complexity",
        "NOM plus the total parameter count across all methods.",
        "Chidamber & Kemerer (1994)",
        _field("complexity", "wmpc2"),
    ),
    MetricDefinition(
        "RFC",
        "Response for a Class",
        "complexity",
        "NOM plus the number of distinct methods of other classes called from this one.",
        "Chidamber & Kemerer (1994)",
        _field("complexity", "rfc"),
    ),
    MetricDefinition(
        "CBO",
        "Coupling Between Objects",
        "coupling",
        "Number of other classes this class is coupled to via method calls or inheritance.",
        "Chidamber & Kemerer (1994)",
        _field("coupling", "cbo"),
    ),
    MetricDefinition(
        "MPC",
        "Message-Passing Coupling",
        "coupling",
        "Count of calls this class makes to methods of other classes.",
        "Li & Henry (1993)",
        _field("coupling", "mpc"),
    ),
    MetricDefinition(
        "LCOM",
        "Lack of Cohesion in Methods",
        "cohesion",
        "Non-cohesive minus cohesive method pairs (by shared field use), floored at zero.",
        "Chidamber & Kemerer (1994) / Sharble & Cohen",
        _field("cohesion", "lcom"),
    ),
)

METRIC_REGISTRY: dict[str, MetricDefinition] = {m.abbreviation: m for m in METRIC_DEFINITIONS}

PROJECT_METRIC_DEFINITIONS: tuple[ProjectMetricDefinition, ...] = (
    ProjectMetricDefinition(
        "NOC",
        "Number of Classes",
        "Total number of classes found across the analyzed project.",
        "Chidamber & Kemerer (1994)",
        lambda pm: pm.noc,
    ),
)

PROJECT_METRIC_REGISTRY: dict[str, ProjectMetricDefinition] = {
    m.abbreviation: m for m in PROJECT_METRIC_DEFINITIONS
}
