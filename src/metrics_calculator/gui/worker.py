"""Runs :func:`metrics_calculator.analyze` off the UI thread.

The work lives on a :class:`QObject` moved to a :class:`QThread`;
progress is reported per file and a cancel request is checked at the
same granularity.
"""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from ..config import AnalysisConfig
from ..engine import analyze
from ..results import ProjectMetrics


class _Cancelled(Exception):
    """Raised out of the progress callback to unwind a running analysis."""


class AnalysisWorker(QObject):
    """Move an instance to a ``QThread`` and connect ``run`` to
    ``QThread.started``.

    Signals:
        progress(completed, total): emitted once per analysed file.
        finished(ProjectMetrics, elapsed_seconds): analysis completed.
        failed(message): analysis raised before completing.
        cancelled(): a cancel request took effect.
    """

    progress = Signal(int, int)
    finished = Signal(object, float)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, root: Path, config: AnalysisConfig) -> None:
        super().__init__()
        self._root = root
        self._config = config
        self._cancel_requested = False

    def cancel(self) -> None:
        """Ask the run to stop. Thread-safe (a plain bool write); the
        request is picked up before the next file is reported."""
        self._cancel_requested = True

    def run(self) -> None:
        started = time.perf_counter()

        def on_progress(completed: int, total: int) -> None:
            if self._cancel_requested:
                raise _Cancelled
            self.progress.emit(completed, total)

        try:
            result: ProjectMetrics = analyze(self._root, self._config, on_progress=on_progress)
        except _Cancelled:
            self.cancelled.emit()
            return
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return

        self.finished.emit(result, time.perf_counter() - started)
