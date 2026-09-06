"""Table model and proxy for the per-class metric table.

Everything the results view needs -- values, formatting, alignment,
threshold and outlier colouring, tooltips, and the rows to export --
comes from here. The view is a plain ``QTableView``; sorting, filtering
and "Save as..." all read the model, never the widget's cells.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QSortFilterProxyModel,
    Qt,
)
from PySide6.QtGui import QColor

from ..registry import METRIC_REGISTRY, MetricDefinition
from ..reporting import Row
from ..results import ProjectMetrics
from .stats import ColumnStats, summarise
from .theme import Palette

_FIXED_COLUMNS: tuple[str, ...] = ("File", "Class")
_Index = QModelIndex | QPersistentModelIndex


@dataclass(slots=True)
class ClassRow:
    file_name: str
    file_path: str
    class_name: str
    values: dict[str, float]


def _format(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}"


class MetricsTableModel(QAbstractTableModel):
    """Rows are classes, columns are ``File``, ``Class`` then one per
    registry metric (in registry order)."""

    def __init__(
        self,
        project: ProjectMetrics,
        thresholds: Mapping[str, float],
        palette: Palette,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._metrics: list[MetricDefinition] = list(METRIC_REGISTRY.values())
        self._thresholds = dict(thresholds)
        self._palette = palette

        self._rows: list[ClassRow] = []
        for file_metrics in project.files:
            for class_metrics in file_metrics.classes:
                values = {
                    definition.abbreviation: float(definition.accessor(class_metrics))
                    for definition in self._metrics
                }
                self._rows.append(
                    ClassRow(
                        file_name=class_metrics.file_name,
                        file_path=file_metrics.file_path,
                        class_name=class_metrics.class_name,
                        values=values,
                    )
                )

        self._stats: dict[str, ColumnStats] = {
            definition.abbreviation: summarise(
                [row.values[definition.abbreviation] for row in self._rows]
            )
            for definition in self._metrics
        }

    # -- Qt model interface ------------------------------------------------

    def rowCount(self, parent: _Index = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: _Index = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(_FIXED_COLUMNS) + len(self._metrics)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object:
        if orientation != Qt.Orientation.Horizontal:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            if section < len(_FIXED_COLUMNS):
                return _FIXED_COLUMNS[section]
            return self._metrics[section - len(_FIXED_COLUMNS)].abbreviation
        if role == Qt.ItemDataRole.ToolTipRole and section >= len(_FIXED_COLUMNS):
            m = self._metrics[section - len(_FIXED_COLUMNS)]
            return f"{m.name}\n{m.description}\nSource: {m.source}"
        return None

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        column = index.column()

        if column < len(_FIXED_COLUMNS):
            if role == Qt.ItemDataRole.DisplayRole:
                return row.file_name if column == 0 else row.class_name
            if role == Qt.ItemDataRole.ToolTipRole and column == 0:
                return row.file_path
            return None

        definition = self._metrics[column - len(_FIXED_COLUMNS)]
        value = row.values[definition.abbreviation]

        if role == Qt.ItemDataRole.DisplayRole:
            return _format(value)
        if role == Qt.ItemDataRole.EditRole:
            return value
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        over = self._exceeds_threshold(definition.abbreviation, value)
        outlier = self._stats[definition.abbreviation].is_outlier(value)
        if role == Qt.ItemDataRole.BackgroundRole:
            if over:
                return QColor(self._palette.over_threshold_bg)
            if outlier:
                return QColor(self._palette.outlier_bg)
        if role == Qt.ItemDataRole.ForegroundRole:
            if over:
                return QColor(self._palette.over_threshold_fg)
            if outlier:
                return QColor(self._palette.outlier_fg)
        if role == Qt.ItemDataRole.ToolTipRole:
            if over:
                limit = self._thresholds[definition.abbreviation]
                return f"{definition.abbreviation} = {_format(value)} exceeds threshold {limit:g}"
            if outlier:
                stats = self._stats[definition.abbreviation]
                return (
                    f"{definition.abbreviation} = {_format(value)} is an outlier "
                    f"(mean {stats.mean:.2f}, sd {stats.stdev:.2f})"
                )
        return None

    def flags(self, index: _Index) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # -- helpers used by the views --------------------------------------

    def _exceeds_threshold(self, abbreviation: str, value: float) -> bool:
        limit = self._thresholds.get(abbreviation)
        return limit is not None and value > limit

    def row_has_violation(self, source_row: int) -> bool:
        values = self._rows[source_row].values
        return any(self._exceeds_threshold(abbr, val) for abbr, val in values.items())

    def metric_abbreviations(self) -> list[str]:
        return [definition.abbreviation for definition in self._metrics]

    def column_values(self, abbreviation: str) -> list[float]:
        return [row.values[abbreviation] for row in self._rows]

    def stats(self, abbreviation: str) -> ColumnStats:
        return self._stats[abbreviation]

    def threshold(self, abbreviation: str) -> float | None:
        return self._thresholds.get(abbreviation)

    def class_row(self, source_row: int) -> ClassRow:
        return self._rows[source_row]

    def export_row(self, source_row: int) -> Row:
        row = self._rows[source_row]
        exported: Row = {"file_name": row.file_name, "class_name": row.class_name}
        for definition in self._metrics:
            raw = row.values[definition.abbreviation]
            exported[definition.abbreviation] = int(raw) if raw == int(raw) else raw
        return exported

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        if self._rows:
            top_left = self.index(0, len(_FIXED_COLUMNS))
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(
                top_left,
                bottom_right,
                [Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole],
            )


class MetricsFilterProxyModel(QSortFilterProxyModel):
    """Substring filter on File/Class plus an optional "violations only"
    switch. Numeric columns sort by value, not by their formatted text."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.setSortRole(Qt.ItemDataRole.EditRole)
        self._text = ""
        self._violations_only = False

    def set_text_filter(self, text: str) -> None:
        self._text = text.strip().lower()
        self.invalidate()

    def set_violations_only(self, enabled: bool) -> None:
        self._violations_only = enabled
        self.invalidate()

    def filterAcceptsRow(self, source_row: int, source_parent: _Index) -> bool:
        model = self.sourceModel()
        if not isinstance(model, MetricsTableModel):
            return True
        row = model.class_row(source_row)
        if (
            self._text
            and self._text not in row.file_name.lower()
            and (self._text not in row.class_name.lower())
        ):
            return False
        if self._violations_only:
            return model.row_has_violation(source_row)
        return True

    def visible_export_rows(self) -> list[Row]:
        model = self.sourceModel()
        if not isinstance(model, MetricsTableModel):
            return []
        rows: list[Row] = []
        for proxy_row in range(self.rowCount()):
            source_row = self.mapToSource(self.index(proxy_row, 0)).row()
            rows.append(model.export_row(source_row))
        return rows
