"""Single source of truth for every metric: abbreviation, full name,
category, description, source paper, the formula **as implemented**, and
how to read the value off a computed result.

UI headers, exports, the in-app manual and ``docs/metrics.md`` all read
from here. Adding a metric is a single entry in this file.

Each entry also carries ``formula`` (what the code actually computes, not
the textbook definition) and ``notes`` (where the implementation
approximates or departs from the source paper). For a research tool this
honesty is the point -- several of these are name-based approximations
with no type resolution.
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
    formula: str
    accessor: Callable[[ClassMetrics], int | float]
    notes: str = ""


@dataclass(frozen=True, slots=True)
class ProjectMetricDefinition:
    abbreviation: str
    name: str
    description: str
    source: str
    formula: str
    accessor: Callable[[ProjectMetrics], int | float]
    notes: str = ""


def _field(*path: str) -> Callable[[ClassMetrics], int | float]:
    def get(class_metrics: ClassMetrics) -> int | float:
        value: object = class_metrics
        for attr in path:
            value = getattr(value, attr)
        if not isinstance(value, (int, float)):
            raise TypeError(f"registry accessor path {path!r} did not resolve to a number")
        return value

    return get


_METHOD_NOTE = (
    "A method is any `def` or `async def` whose name appears in the class; "
    "functions nested inside a method body are counted too, and same-named "
    "definitions collapse to one."
)

METRIC_DEFINITIONS: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        "LOC",
        "Lines of Code",
        "size",
        "Non-blank lines spanned by the class body.",
        "Chidamber & Kemerer (1994)",
        "(last line - first line + 1) of the class node, minus blank lines in that span",
        _field("size", "loc"),
        notes="Counts the whole class span including decorators and docstring; comment-only "
        "lines are not treated as blank.",
    ),
    MetricDefinition(
        "NOM",
        "Number of Methods",
        "size",
        "Count of methods declared on the class.",
        "Chidamber & Kemerer (1994)",
        "number of distinct method names collected for the class",
        _field("size", "nom"),
        notes=_METHOD_NOTE,
    ),
    MetricDefinition(
        "SIZE2",
        "Number of Properties and Methods",
        "size",
        "NOM plus the number of distinct fields.",
        "Li & Henry (1993)",
        "NOM + WAC",
        _field("size", "size2"),
    ),
    MetricDefinition(
        "WAC",
        "Weighted Attributes per Class",
        "size",
        "Count of distinct class and instance fields.",
        "Li & Henry (1993)",
        "number of distinct `self.x` / `ClassName.x` targets assigned anywhere in the class "
        "(plain, annotated or augmented assignment) plus class-body names",
        _field("size", "wac"),
        notes="Field discovery is syntactic: only assignments are seen, not fields introduced "
        "only via `__slots__`, `setattr`, or a base class.",
    ),
    MetricDefinition(
        "NOCC",
        "Number of Children",
        "size",
        "Count of classes in the project that directly subclass this one.",
        "Chidamber & Kemerer (1994)",
        "number of project classes whose declared bases include this class's simple name",
        _field("size", "nocc"),
        notes="Bases are matched by simple name (`Foo`, or the last segment of `pkg.Foo`); a "
        "name clash between two unrelated classes will over-count.",
    ),
    MetricDefinition(
        "DIT",
        "Depth of Inheritance Tree",
        "complexity",
        "Longest inheritance chain above this class, counting only project classes.",
        "Chidamber & Kemerer (1994)",
        "0 if no base resolves to a project class, else 1 + max(DIT of resolved project bases); "
        "an inheritance cycle contributes 0",
        _field("complexity", "dit"),
        notes="Bases from outside the analysed project (stdlib, third-party) do not add depth.",
    ),
    MetricDefinition(
        "WMPC1",
        "Weighted Methods per Class (complexity)",
        "complexity",
        "Average cyclomatic complexity per method.",
        "Chidamber & Kemerer (1994)",
        "round(total cyclomatic complexity / NOM, 2), or 0.0 when NOM is 0",
        _field("complexity", "wmpc1"),
        notes="Cyclomatic complexity is approximated as 1 per method plus 1 for each "
        "`if`/`for`/`while`/conditional-expression/comprehension clause and one per `match` "
        "case; `and`/`or`, `except` and `assert` are not counted.",
    ),
    MetricDefinition(
        "WMPC2",
        "Weighted Methods per Class (parameters)",
        "complexity",
        "NOM plus the total parameter count across all methods.",
        "Chidamber & Kemerer (1994)",
        "NOM + sum of positional parameter counts over all methods (`self` included)",
        _field("complexity", "wmpc2"),
        notes="Only positional parameters are counted; `*args`, `**kwargs` and keyword-only "
        "parameters are ignored.",
    ),
    MetricDefinition(
        "RFC",
        "Response for a Class",
        "complexity",
        "NOM plus the number of distinct methods of other classes called from this one.",
        "Chidamber & Kemerer (1994)",
        "NOM + number of distinct (receiver name, method name) pairs called on other objects",
        _field("complexity", "rfc"),
        notes="Remote calls are matched by method name only (no type resolution); a call "
        "counts if any project class defines a method of that name.",
    ),
    MetricDefinition(
        "CBO",
        "Coupling Between Objects",
        "coupling",
        "Number of other classes this class is coupled to via method calls or inheritance.",
        "Chidamber & Kemerer (1994)",
        "count of distinct names in (receivers of remote calls) plus (declared base names), "
        "then + NOCC",
        _field("coupling", "cbo"),
        notes="Coupling partners are approximated by the *names* used at call sites and in "
        "`class Foo(Bar)` clauses, not by resolved classes, so a local variable and an "
        "unrelated class sharing a name are conflated.",
    ),
    MetricDefinition(
        "MPC",
        "Message-Passing Coupling",
        "coupling",
        "Count of calls this class makes to methods of other classes.",
        "Li & Henry (1993)",
        "number of `receiver.method(...)` call sites where `method` is defined by some "
        "project class and the receiver is not `self` or the class itself",
        _field("coupling", "mpc"),
        notes="Unlike RFC this is call sites, not distinct methods. Attribute reads that are "
        "not calls (`f(obj.attr)`) are not counted.",
    ),
    MetricDefinition(
        "LCOM",
        "Lack of Cohesion in Methods",
        "cohesion",
        "Non-cohesive minus cohesive method pairs (by shared field use), floored at zero.",
        "Chidamber & Kemerer (1994) / Sharble & Cohen",
        "max(P - Q, 0) where, over unordered method pairs, Q share at least one field and "
        "P share none",
        _field("cohesion", "lcom"),
        notes="Only fields already known for the class count as shared use, and only "
        "attribute accesses in the method's own body -- nested functions and classes are "
        "excluded.",
    ),
)

METRIC_REGISTRY: dict[str, MetricDefinition] = {m.abbreviation: m for m in METRIC_DEFINITIONS}

PROJECT_METRIC_DEFINITIONS: tuple[ProjectMetricDefinition, ...] = (
    ProjectMetricDefinition(
        "NOC",
        "Number of Classes",
        "Total number of classes found across the analyzed project.",
        "Chidamber & Kemerer (1994)",
        "count of class definitions discovered in all analysed files",
        lambda pm: pm.noc,
        notes="A class defined inside a method body is counted twice, matching the original "
        "tool's discovery.",
    ),
)

PROJECT_METRIC_REGISTRY: dict[str, ProjectMetricDefinition] = {
    m.abbreviation: m for m in PROJECT_METRIC_DEFINITIONS
}


_UNIMPLEMENTED_QMOOD: tuple[str, ...] = (
    "reusability",
    "flexibility",
    "understandability",
    "functionality",
    "extendability",
    "effectiveness",
)


@dataclass(frozen=True, slots=True)
class UnimplementedMetric:
    abbreviation: str
    name: str
    category: str
    source: str
    reason: str


UNIMPLEMENTED_METRICS: tuple[UnimplementedMetric, ...] = tuple(
    UnimplementedMetric(
        name,
        name.replace("_", " ").title(),
        "qmood",
        "Bansiya & Davis (2002)",
        "Declared by the original tool but never computed; kept here as documented future work.",
    )
    for name in _UNIMPLEMENTED_QMOOD
)
