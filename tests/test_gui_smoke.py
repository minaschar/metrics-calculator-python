"""Headless smoke tests for the PySide6 front-end.

These run on the offscreen Qt platform (see conftest.py). They exercise
the model, proxy, exporters, visualisation and the full analyse-off-thread
path -- enough to catch an import error, a broken signal wiring or a
regressed export, which is what a display-less CI can check.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest
from _paths import FIXTURES_DIR
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from metrics_calculator import AnalysisConfig, analyze
from metrics_calculator.gui.main_window import MainWindow
from metrics_calculator.gui.manual import manual_entries, manual_html
from metrics_calculator.gui.models import MetricsFilterProxyModel, MetricsTableModel
from metrics_calculator.gui.stats import histogram, summarise
from metrics_calculator.gui.theme import LIGHT
from metrics_calculator.gui.views import (
    DiagnosticsView,
    DistributionView,
    ManualView,
    ResultsView,
    SourceView,
)
from metrics_calculator.reporting import FIELDNAMES, rows_to_csv
from metrics_calculator.results import ProjectMetrics


@pytest.fixture(autouse=True)
def _ensure_qapp(qapp: QApplication) -> QApplication:
    """pytest-qt's `qapp` -- a process-wide QApplication every widget in
    this module needs (constructing a QWidget without one crashes)."""
    return qapp


@pytest.fixture
def deep_project() -> ProjectMetrics:
    return analyze(FIXTURES_DIR / "deep_inheritance", AnalysisConfig())


def test_stats_and_histogram_are_qt_free() -> None:
    stats = summarise([1.0] * 9 + [20.0])
    assert stats.count == 10
    assert stats.maximum == 20.0
    assert stats.is_outlier(20.0)
    assert not stats.is_outlier(1.0)
    bins = histogram([1.0, 1.0, 2.0, 9.0], bins=4)
    assert sum(b.count for b in bins) == 4


def test_model_shape_and_roles(deep_project: ProjectMetrics) -> None:
    model = MetricsTableModel(deep_project, {"DIT": 1.0}, LIGHT)
    assert model.rowCount() == 4
    assert model.columnCount() == 2 + len(model.metric_abbreviations())

    dit_column = 2 + model.metric_abbreviations().index("DIT")
    display = model.data(model.index(0, dit_column), Qt.ItemDataRole.DisplayRole)
    edit = model.data(model.index(0, dit_column), Qt.ItemDataRole.EditRole)
    assert isinstance(display, str)
    assert isinstance(edit, float)

    header = model.headerData(dit_column, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
    assert header == "DIT"

    # The deepest class in a 3-deep chain has DIT over the threshold of 1.
    violating_rows = [r for r in range(model.rowCount()) if model.row_has_violation(r)]
    assert violating_rows
    bg = model.data(model.index(violating_rows[0], dit_column), Qt.ItemDataRole.BackgroundRole)
    assert bg is not None


def test_proxy_filters_and_exports_visible_rows(deep_project: ProjectMetrics) -> None:
    model = MetricsTableModel(deep_project, {"DIT": 1.0}, LIGHT)
    proxy = MetricsFilterProxyModel()
    proxy.setSourceModel(model)

    assert proxy.rowCount() == 4

    proxy.set_violations_only(True)
    assert 0 < proxy.rowCount() < 4

    proxy.set_violations_only(False)
    proxy.set_text_filter("does-not-exist")
    assert proxy.rowCount() == 0
    proxy.set_text_filter("")

    rows = proxy.visible_export_rows()
    assert len(rows) == 4
    assert set(rows[0]) == set(FIELDNAMES)

    parsed = list(csv.DictReader(io.StringIO(rows_to_csv(rows))))
    assert len(parsed) == 4
    assert parsed[0]["class_name"]


def test_results_view_exports_to_file(
    deep_project: ProjectMetrics, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    view = ResultsView()
    model = MetricsTableModel(deep_project, {}, LIGHT)
    view.set_model(model, deep_project)

    target = tmp_path / "out.csv"
    monkeypatch.setattr(
        "metrics_calculator.gui.views.QFileDialog.getSaveFileName",
        lambda *a, **k: (str(target), "CSV (*.csv)"),
    )
    monkeypatch.setattr(
        "metrics_calculator.gui.views.QMessageBox.information", lambda *a, **k: None
    )
    view.export_visible()
    assert target.exists()
    assert "class_name" in target.read_text(encoding="utf-8")


def test_distribution_view_populates(deep_project: ProjectMetrics) -> None:
    view = DistributionView(LIGHT)
    model = MetricsTableModel(deep_project, {}, LIGHT)
    view.set_model(model)
    assert view._picker.count() == len(model.metric_abbreviations())
    assert view._histogram._bins  # a metric is selected and its bins built


def test_diagnostics_view_shows_syntax_errors() -> None:
    project = analyze(FIXTURES_DIR / "syntax_error", AnalysisConfig())
    assert project.diagnostics
    view = DiagnosticsView()
    view.set_diagnostics(project.diagnostics)
    assert view._table.isVisibleTo(view)
    assert not view._empty.isVisibleTo(view)
    assert view._table.rowCount() == len(project.diagnostics)


def test_manual_is_registry_generated() -> None:
    entries = manual_entries()
    abbreviations = {e.abbreviation for e in entries}
    assert {"LCOM", "RFC", "NOC"} <= abbreviations
    assert any(not e.computed for e in entries)  # QMOOD attributes
    html = manual_html()
    assert "LCOM" in html
    assert "Reusability" in html

    ManualView(LIGHT.mode)  # constructs and renders without error


def test_source_view_highlights_class(deep_project: ProjectMetrics) -> None:
    model = MetricsTableModel(deep_project, {}, LIGHT)
    view = SourceView(LIGHT)
    view.show_class(model.class_row(0))
    assert view._editor.toPlainText()
    assert "lines" in view._heading.text()


def test_app_main_wires_up_without_blocking(monkeypatch: pytest.MonkeyPatch) -> None:
    from metrics_calculator.gui import app as app_module

    monkeypatch.setattr(QApplication, "exec", lambda self=None: 0)
    rc = app_module.main(["metrics-calculator-gui", str(FIXTURES_DIR / "deep_inheritance")])
    assert rc == 0


def test_app_version_flag_exits_without_a_window(capsys: pytest.CaptureFixture[str]) -> None:
    from metrics_calculator import __version__
    from metrics_calculator.gui import app as app_module

    assert app_module.main(["metrics-calculator-gui", "--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_app_selftest_env_builds_window_and_returns(monkeypatch: pytest.MonkeyPatch) -> None:
    """The path CI uses to prove the frozen (windowed, no-stdout) binary
    starts: build the window, pump the queue once, exit 0."""
    from metrics_calculator.gui import app as app_module

    monkeypatch.setenv("MC_GUI_SELFTEST", "1")
    monkeypatch.setattr(QApplication, "exec", lambda self=None: pytest.fail("event loop entered"))
    assert app_module.main(["metrics-calculator-gui"]) == 0


def test_main_window_runs_analysis_off_thread(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_project(FIXTURES_DIR / "deep_inheritance")
    window._start_analysis()
    qtbot.waitUntil(lambda: window._model is not None, timeout=5000)

    assert window._model is not None
    assert window._model.rowCount() == 4
    assert "classes" in window.statusBar().currentMessage()
