"""The application window: pick a project, analyse it off-thread, and
browse the results across the tabs."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QSettings, QThread
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..config import AnalysisConfig
from ..results import ProjectMetrics
from .models import ClassRow, MetricsTableModel
from .theme import Mode, palette, stylesheet
from .views import (
    DiagnosticsView,
    DistributionView,
    ManualView,
    ResultsView,
    SourceView,
)
from .worker import AnalysisWorker

_ORG = "metrics-calculator-python"
_APP = "Metrics Calculator"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(_APP)
        self.resize(1100, 720)

        self._settings = QSettings(_ORG, _APP)
        self._mode = Mode(str(self._settings.value("theme", Mode.LIGHT.value)))
        self._project_dir: Path | None = None
        self._config = AnalysisConfig()
        self._project: ProjectMetrics | None = None
        self._model: MetricsTableModel | None = None
        self._thread: QThread | None = None
        self._worker: AnalysisWorker | None = None

        self._build_ui()
        self._build_menus()
        self._apply_mode(self._mode)

    # -- construction ------------------------------------------------

    def _build_ui(self) -> None:
        self._path_label = QLabel("No project selected")
        self._path_label.setObjectName("Muted")

        self._open_button = QPushButton("Open project...")
        self._open_button.clicked.connect(self.choose_project)

        self._analyze_button = QPushButton("Analyze")
        self._analyze_button.setObjectName("Primary")
        self._analyze_button.setEnabled(False)
        self._analyze_button.clicked.connect(self._start_analysis)

        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.setEnabled(False)
        self._cancel_button.clicked.connect(self._cancel_analysis)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setTextVisible(True)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self._open_button)
        top_bar.addWidget(self._path_label, 1)
        top_bar.addWidget(self._progress, 1)
        top_bar.addWidget(self._analyze_button)
        top_bar.addWidget(self._cancel_button)

        self._results = ResultsView()
        self._results.classActivated.connect(self._show_source)
        self._distribution = DistributionView(palette(self._mode))
        self._source = SourceView(palette(self._mode))
        self._diagnostics = DiagnosticsView()
        self._manual = ManualView(self._mode)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._results, "Results")
        self._tabs.addTab(self._distribution, "Distribution")
        self._tabs.addTab(self._source, "Source")
        self._tabs.addTab(self._diagnostics, "Diagnostics")
        self._tabs.addTab(self._manual, "Manual")

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(self._tabs)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(top_bar)
        layout.addWidget(card, 1)
        self.setCentralWidget(central)

        self.statusBar().showMessage("Open a project to begin.")

    def _action(
        self, text: str, slot: Callable[..., object], shortcut: str | None = None
    ) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        return action

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self._action("&Open project...", self.choose_project, "Ctrl+O"))
        self._export_action = self._action(
            "&Export results...", self._results.export_visible, "Ctrl+E"
        )
        self._export_action.setEnabled(False)
        file_menu.addAction(self._export_action)
        file_menu.addSeparator()
        file_menu.addAction(self._action("&Quit", self.close, "Ctrl+Q"))

        view_menu = self.menuBar().addMenu("&View")
        self._theme_action = self._action("Toggle &dark mode", self._toggle_theme, "Ctrl+D")
        self._theme_action.setCheckable(True)
        self._theme_action.setChecked(self._mode is Mode.DARK)
        view_menu.addAction(self._theme_action)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self._action("&About", self._about))

    # -- project selection -----------------------------------------

    def choose_project(self) -> None:
        start_dir = str(self._project_dir or self._settings.value("last_dir", str(Path.home())))
        chosen = QFileDialog.getExistingDirectory(self, "Select a Python project", start_dir)
        if chosen:
            self.open_project(Path(chosen))

    def open_project(self, path: Path) -> None:
        self._project_dir = path
        self._settings.setValue("last_dir", str(path))
        self._path_label.setText(str(path))
        self._path_label.setObjectName("")
        self._analyze_button.setEnabled(True)
        self.statusBar().showMessage(f"Ready to analyze {path.name}.")

    # -- analysis lifecycle --------------------------------------

    def _start_analysis(self) -> None:
        if self._project_dir is None or self._thread is not None:
            return
        self._config = AnalysisConfig.discover(self._project_dir)

        self._thread = QThread(self)
        self._worker = AnalysisWorker(self._project_dir, self._config)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.cancelled.connect(self._on_cancelled)

        self._analyze_button.setEnabled(False)
        self._open_button.setEnabled(False)
        self._cancel_button.setEnabled(True)
        self._progress.setVisible(True)
        self._progress.setRange(0, 0)
        self.statusBar().showMessage("Analyzing...")
        self._thread.start()

    def _on_progress(self, completed: int, total: int) -> None:
        self._progress.setRange(0, total)
        self._progress.setValue(completed)
        self.statusBar().showMessage(f"Analyzing... {completed}/{total} files")

    def _on_finished(self, project: ProjectMetrics, elapsed: float) -> None:
        self._teardown_thread()
        self._project = project
        thresholds = self._config.thresholds
        self._model = MetricsTableModel(project, thresholds, palette(self._mode), self)

        self._results.set_model(self._model, project)
        self._distribution.set_model(self._model)
        self._diagnostics.set_diagnostics(project.diagnostics)
        self._source.clear()
        self._export_action.setEnabled(True)
        self._tabs.setCurrentWidget(self._results)

        classes = sum(len(f.classes) for f in project.files)
        self.statusBar().showMessage(
            f"{classes} classes in {len(project.files)} files - "
            f"NOC {project.noc} - {len(project.diagnostics)} diagnostics - "
            f"{elapsed:.2f}s"
        )

    def _on_failed(self, message: str) -> None:
        self._teardown_thread()
        QMessageBox.critical(self, "Analysis failed", message)
        self.statusBar().showMessage("Analysis failed.")

    def _on_cancelled(self) -> None:
        self._teardown_thread()
        self.statusBar().showMessage("Analysis cancelled.")

    def _cancel_analysis(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            self._cancel_button.setEnabled(False)
            self.statusBar().showMessage("Cancelling...")

    def _teardown_thread(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
            self._thread.deleteLater()
        self._thread = None
        self._worker = None
        self._progress.setVisible(False)
        self._analyze_button.setEnabled(self._project_dir is not None)
        self._open_button.setEnabled(True)
        self._cancel_button.setEnabled(False)

    # -- drill-down + theming --------------------------------------

    def _show_source(self, row: ClassRow) -> None:
        self._source.show_class(row)
        self._tabs.setCurrentWidget(self._source)

    def _toggle_theme(self) -> None:
        self._apply_mode(Mode.DARK if self._mode is Mode.LIGHT else Mode.LIGHT)

    def _apply_mode(self, mode: Mode) -> None:
        self._mode = mode
        self._settings.setValue("theme", mode.value)
        active = palette(mode)
        self.setStyleSheet(stylesheet(active))
        if self._model is not None:
            self._model.set_palette(active)
        self._distribution.set_palette(active)
        self._source.set_palette(active)
        self._manual.set_mode(mode)
        if hasattr(self, "_theme_action"):
            self._theme_action.setChecked(mode is Mode.DARK)

    def _about(self) -> None:
        QMessageBox.about(
            self,
            "About Metrics Calculator",
            f"<b>{_APP}</b> {__version__}<br>"
            "Object-oriented software quality metrics for Python, computed from the AST.<br>"
            "Chidamber &amp; Kemerer (1994), Li &amp; Henry (1993), Bansiya &amp; Davis (2002).",
        )

    def closeEvent(self, event: object) -> None:
        if self._worker is not None:
            self._worker.cancel()
        self._teardown_thread()
        super().closeEvent(event)  # type: ignore[arg-type]
