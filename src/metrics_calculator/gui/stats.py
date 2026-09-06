"""Small, Qt-free descriptive statistics for one metric column.

Used by the results table (outlier highlighting) and the distribution
view (histogram, mean/median markers). Kept separate from the widgets so
it can be unit-tested without a display.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColumnStats:
    count: int
    minimum: float
    maximum: float
    mean: float
    median: float
    stdev: float
    # Values strictly above this are flagged as outliers: mean + 2*stdev.
    outlier_threshold: float

    def is_outlier(self, value: float) -> bool:
        return self.stdev > 0 and value > self.outlier_threshold


def summarise(values: list[float]) -> ColumnStats:
    if not values:
        return ColumnStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, math.inf)

    ordered = sorted(values)
    n = len(ordered)
    mean = sum(ordered) / n
    mid = n // 2
    median = ordered[mid] if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    variance = sum((v - mean) ** 2 for v in ordered) / n
    stdev = math.sqrt(variance)
    return ColumnStats(
        count=n,
        minimum=ordered[0],
        maximum=ordered[-1],
        mean=mean,
        median=median,
        stdev=stdev,
        outlier_threshold=mean + 2 * stdev if stdev > 0 else math.inf,
    )


@dataclass(frozen=True, slots=True)
class HistogramBin:
    low: float
    high: float
    count: int


def histogram(values: list[float], bins: int = 12) -> list[HistogramBin]:
    """Equal-width bins across ``[min, max]``. The final bin is closed on
    the right so the maximum value lands in it."""
    if not values:
        return []
    low = min(values)
    high = max(values)
    if low == high:
        return [HistogramBin(low, high, len(values))]

    width = (high - low) / bins
    counts = [0] * bins
    for value in values:
        index = int((value - low) / width)
        if index >= bins:  # the maximum
            index = bins - 1
        counts[index] += 1
    return [HistogramBin(low + i * width, low + (i + 1) * width, counts[i]) for i in range(bins)]
