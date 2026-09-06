"""The four result tabs plus the source drill-down panel.

Each is a self-contained ``QWidget`` fed by :class:`MetricsTableModel` (or
the raw :class:`ProjectMetrics` for things the table doesn't carry, like
diagnostics and source text). None of them holds analysis logic.
"""

from __future__ import annotations

import ast
from functools import partial
from pathlib import Path

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..diagnostics import Diagnostic
from ..reporting import rows_to_csv, rows_to_xlsx, to_html, to_json
from ..results import ProjectMetrics
from .manual import manual_html
from .models import ClassRow, MetricsFilterProxyModel, MetricsTableModel
from .stats import histogram
from .theme import Mode, Palette
from .widgets import HistogramWidget

_EXPORT_FORMATS = {
    "CSV (*.csv)": ("csv", "csv"),
    "JSON (*.json)": ("json", "json"),
    "HTML (*.html)": ("html", "html"),
    "Excel (*.xlsx)": ("xlsx", "xlsx"),
}


class ResultsView(QWidget):
    classActivated = Signal(object)  # ClassRow

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project: ProjectMetrics | None = None
        self._proxy: MetricsFilterProxyModel | None = None

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filter by class or file name...")
        self._filter.setClearButtonEnabled(True)
        self._filter.textChanged.connect(self._on_filter_changed)

        self._violations = QCheckBox("Threshold violations only")
        self._violations.toggled.connect(self._on_violations_toggled)

        self._export = QToolButton()
        self._export.setText("Export...")
        self._export.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self._export)
        for label in _EXPORT_FORMATS:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._export_as, label))
        self._export.setMenu(menu)
        self._export.setEnabled(False)

        self._table = QTableView()
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.doubleClicked.connect(self._on_activated)

        top = QHBoxLayout()
        top.addWidget(self._filter, 1)
        top.addWidget(self._violations)
        top.addWidget(self._export)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._table)

    def set_model(self, model: MetricsTableModel, project: ProjectMetrics) -> None:
        self._project = project
        self._proxy = MetricsFilterProxyModel(self)
        self._proxy.setSourceModel(model)
        self._proxy.set_text_filter(self._filter.text())
        self._proxy.set_violations_only(self._violations.isChecked())
        self._table.setModel(self._proxy)
        self._table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self._export.setEnabled(True)

    def clear(self) -> None:
        self._table.setModel(None)
        self._proxy = None
        self._project = None
        self._export.setEnabled(False)

    def export_visible(self) -> None:
        """Menu / Ctrl+E entry point: export the visible rows as CSV."""
        self._export_as("CSV (*.csv)")

    # -- slots --------------------------------------------------------

    def _on_filter_changed(self, text: str) -> None:
        if self._proxy is not None:
            self._proxy.set_text_filter(text)

    def _on_violations_toggled(self, checked: bool) -> None:
        if self._proxy is not None:
            self._proxy.set_violations_only(checked)

    def _on_activated(self, index: QModelIndex) -> None:
        if self._proxy is None:
            return
        source = self._proxy.mapToSource(index)
        model = self._proxy.sourceModel()
        if isinstance(model, MetricsTableModel):
            self.classActivated.emit(model.class_row(source.row()))

    def _export_as(self, menu_label: str, _checked: bool = False) -> None:
        # `_checked` absorbs the bool QAction.triggered passes positionally.
        if self._proxy is None or self._project is None:
            return
        fmt, extension = _EXPORT_FORMATS[menu_label]
        default_name = f"{self._project.project_name}-metrics.{extension}"
        path_str, _ = QFileDialog.getSaveFileName(self, "Export results", default_name, menu_label)
        if not path_str:
            return
        path = Path(path_str)
        try:
            if fmt == "csv":
                path.write_text(rows_to_csv(self._proxy.visible_export_rows()), encoding="utf-8")
            elif fmt == "json":
                path.write_text(to_json(self._project), encoding="utf-8")
            elif fmt == "html":
                path.write_text(to_html(self._project), encoding="utf-8")
            else:
                rows_to_xlsx(self._proxy.visible_export_rows(), path)
        except ImportError:
            QMessageBox.warning(
                self,
                "Excel export unavailable",
                "Writing .xlsx needs pandas and openpyxl:\n"
                "    pip install 'metrics-calculator-python[cli]'",
            )
            return
        except OSError as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
            return
        QMessageBox.information(self, "Export complete", f"Wrote {path}")


class DistributionView(QWidget):
    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._model: MetricsTableModel | None = None

        self._picker = QComboBox()
        self._picker.currentTextChanged.connect(self._refresh)
        self._histogram = HistogramWidget(palette)
        self._caption = QLabel()
        self._caption.setObjectName("Muted")

        row = QHBoxLayout()
        row.addWidget(QLabel("Metric"))
        row.addWidget(self._picker)
        row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(row)
        layout.addWidget(self._histogram, 1)
        layout.addWidget(self._caption)

    def set_model(self, model: MetricsTableModel) -> None:
        self._model = model
        self._picker.blockSignals(True)
        self._picker.clear()
        self._picker.addItems(model.metric_abbreviations())
        self._picker.blockSignals(False)
        self._picker.setCurrentIndex(0)
        self._refresh(self._picker.currentText())

    def clear(self) -> None:
        self._model = None
        self._picker.clear()
        self._caption.clear()

    def set_palette(self, palette: Palette) -> None:
        self._histogram.set_palette(palette)

    def _refresh(self, abbreviation: str) -> None:
        if self._model is None or not abbreviation:
            return
        values = self._model.column_values(abbreviation)
        stats = self._model.stats(abbreviation)
        threshold = self._model.threshold(abbreviation)
        self._histogram.set_data(
            title=abbreviation,
            bins=histogram(values),
            stats=stats,
            threshold=threshold,
        )
        outliers = sum(1 for value in values if stats.is_outlier(value))
        self._caption.setText(
            f"n={stats.count}   min {stats.minimum:g}   max {stats.maximum:g}   "
            f"mean {stats.mean:.2f}   median {stats.median:.2f}   outliers {outliers}"
        )


class DiagnosticsView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._empty = QLabel("No files were skipped.")
        self._empty.setObjectName("Muted")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Severity", "File", "Message"])
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self._empty)
        layout.addWidget(self._table)

    def set_diagnostics(self, diagnostics: list[Diagnostic]) -> None:
        self._table.setRowCount(len(diagnostics))
        for row, diagnostic in enumerate(diagnostics):
            self._table.setItem(row, 0, QTableWidgetItem(diagnostic.severity))
            self._table.setItem(row, 1, QTableWidgetItem(str(diagnostic.path)))
            self._table.setItem(row, 2, QTableWidgetItem(diagnostic.message))
        has_rows = bool(diagnostics)
        self._table.setVisible(has_rows)
        self._empty.setVisible(not has_rows)

    def clear(self) -> None:
        self._table.setRowCount(0)
        self._table.setVisible(False)
        self._empty.setVisible(True)


class ManualView(QWidget):
    def __init__(self, mode: Mode, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self._browser)
        self.set_mode(mode)

    def set_mode(self, mode: Mode) -> None:
        self._browser.setHtml(manual_html(dark=mode is Mode.DARK))


class SourceView(QWidget):
    """Read-only source of the double-clicked class, with its body
    highlighted. Re-parses the file on demand -- the result types don't
    carry line spans, and adding them would change nothing the metrics
    see."""

    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._heading = QLabel("Double-click a class in Results to view its source.")
        self._heading.setObjectName("Muted")

        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._editor.setFont(font)

        layout = QVBoxLayout(self)
        layout.addWidget(self._heading)
        layout.addWidget(self._editor)

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette

    def show_class(self, row: ClassRow) -> None:
        path = Path(row.file_path)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            self._heading.setText(f"{row.class_name} - could not read {path}: {exc}")
            self._editor.clear()
            return

        span = _class_line_span(source, row.class_name)
        self._heading.setText(
            f"{row.class_name}   -   {path}" + (f"   (lines {span[0]}-{span[1]})" if span else "")
        )
        self._editor.setPlainText(source)
        if span:
            self._highlight(span)

    def _highlight(self, span: tuple[int, int]) -> None:
        start_line, end_line = span
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(self._palette.outlier_bg))
        fmt.setProperty(QTextCharFormat.Property.FullWidthSelection, True)

        selections = []
        document = self._editor.document()
        for line_number in range(start_line, end_line + 1):
            block = document.findBlockByNumber(line_number - 1)
            if not block.isValid():
                break
            selection = QTextEdit.ExtraSelection()
            selection.cursor = QTextCursor(block)
            selection.format = fmt
            selections.append(selection)
        self._editor.setExtraSelections(selections)

        cursor = QTextCursor(document.findBlockByNumber(start_line - 1))
        self._editor.setTextCursor(cursor)
        self._editor.centerCursor()

    def clear(self) -> None:
        self._editor.clear()
        self._heading.setText("Double-click a class in Results to view its source.")


def _class_line_span(source: str, class_name: str) -> tuple[int, int] | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    best: tuple[int, int] | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            end = node.end_lineno or node.lineno
            # Prefer the outermost match if the name repeats.
            if best is None or node.lineno < best[0]:
                best = (node.lineno, end)
    return best
