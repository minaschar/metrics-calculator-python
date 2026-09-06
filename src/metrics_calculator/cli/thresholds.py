"""`--fail-under METRIC=VALUE` parsing and evaluation, so a CI job can gate
on this tool's output instead of just reading it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..registry import METRIC_REGISTRY
from ..results import ProjectMetrics


@dataclass(frozen=True, slots=True)
class ThresholdViolation:
    file_name: str
    class_name: str
    metric: str
    value: float
    limit: float

    def __str__(self) -> str:
        return (
            f"{self.file_name}:{self.class_name}: {self.metric}={self.value} "
            f"exceeds limit {self.limit}"
        )


def parse_threshold_option(raw: str) -> tuple[str, float]:
    metric, separator, value = raw.partition("=")
    if not separator:
        raise ValueError(f"expected METRIC=VALUE, got {raw!r}")
    metric = metric.strip().upper()
    if metric not in METRIC_REGISTRY:
        known = ", ".join(sorted(METRIC_REGISTRY))
        raise ValueError(f"unknown metric {metric!r}; known metrics: {known}")
    try:
        limit = float(value)
    except ValueError as exc:
        raise ValueError(f"expected a number after '=', got {value!r}") from exc
    return metric, limit


def check_thresholds(
    project_metrics: ProjectMetrics, thresholds: Mapping[str, float]
) -> list[ThresholdViolation]:
    violations: list[ThresholdViolation] = []
    for file_metrics in project_metrics.files:
        for class_metrics in file_metrics.classes:
            for metric, limit in thresholds.items():
                definition = METRIC_REGISTRY[metric]
                value = float(definition.accessor(class_metrics))
                if value > limit:
                    violations.append(
                        ThresholdViolation(
                            class_metrics.file_name, class_metrics.class_name, metric, value, limit
                        )
                    )
    return violations
