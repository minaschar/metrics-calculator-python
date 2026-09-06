"""Diff mode: compare two analysis runs and report what moved.

A "run" is either a project directory (analyzed on the spot) or a JSON
file previously produced by `metrics-calculator analyze --format json`.
This is what turns the tool from a one-off measurement into something a
CI job can watch over time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..config import AnalysisConfig
from ..engine import analyze
from ..registry import METRIC_REGISTRY
from ..reporting import to_rows

ClassKey = tuple[str, str]  # (file_name, class_name)
MetricRow = dict[str, float]


@dataclass(frozen=True, slots=True)
class MetricChange:
    file_name: str
    class_name: str
    metric: str
    old: float
    new: float

    @property
    def delta(self) -> float:
        return self.new - self.old


@dataclass(frozen=True, slots=True)
class MetricsDiff:
    added_classes: tuple[ClassKey, ...]
    removed_classes: tuple[ClassKey, ...]
    changed: tuple[MetricChange, ...]

    @property
    def is_empty(self) -> bool:
        return not self.added_classes and not self.removed_classes and not self.changed


def _coerce_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"expected a number, got {value!r}")


def _flatten(rows: list[dict[str, object]]) -> dict[ClassKey, MetricRow]:
    flattened: dict[ClassKey, MetricRow] = {}
    for row in rows:
        key = (str(row["file_name"]), str(row["class_name"]))
        flattened[key] = {abbr: _coerce_float(row[abbr]) for abbr in METRIC_REGISTRY}
    return flattened


def load_metric_rows(source: Path, config: AnalysisConfig) -> dict[ClassKey, MetricRow]:
    if source.is_dir():
        return _flatten(to_rows(analyze(source, config)))

    data = json.loads(source.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = [
        class_row for file_entry in data["files"] for class_row in file_entry["classes"]
    ]
    return _flatten(rows)


def diff_metric_rows(old: dict[ClassKey, MetricRow], new: dict[ClassKey, MetricRow]) -> MetricsDiff:
    added = tuple(key for key in new if key not in old)
    removed = tuple(key for key in old if key not in new)

    changed: list[MetricChange] = []
    for key, new_row in new.items():
        old_row = old.get(key)
        if old_row is None:
            continue
        for metric, new_value in new_row.items():
            old_value = old_row[metric]
            if old_value != new_value:
                changed.append(MetricChange(key[0], key[1], metric, old_value, new_value))

    return MetricsDiff(added, removed, tuple(changed))
