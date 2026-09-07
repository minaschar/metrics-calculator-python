"""Hand-painted visualisation widgets.

Only QtWidgets/QtGui are used -- no QtCharts, no matplotlib -- so the app
stays inside ``pyside6-essentials`` and renders identically headless. The
histogram shows a metric's distribution across the project, marks the
threshold, and picks out the outlier tail.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from .stats import ColumnStats, HistogramBin
from .theme import Palette


class HistogramWidget(QWidget):
    """Distribution of one metric column, with mean/median markers, an
    optional threshold line, and the outlier tail drawn in the accent
    colour."""

    def __init__(self, palette: Palette, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = palette
        self._bins: list[HistogramBin] = []
        self._stats: ColumnStats | None = None
        self._threshold: float | None = None
        self._title = ""
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(
        self,
        *,
        title: str,
        bins: list[HistogramBin],
        stats: ColumnStats,
        threshold: float | None,
    ) -> None:
        self._title = title
        self._bins = bins
        self._stats = stats
        self._threshold = threshold
        self.update()

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        self.update()

    # -- painting -------------------------------------------------------

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self._palette

        painter.fillRect(self.rect(), QColor(pal.surface))

        margin_left, margin_right = 44, 40
        margin_top, margin_bottom = 28, 34
        plot = QRectF(
            margin_left,
            margin_top,
            max(1.0, self.width() - margin_left - margin_right),
            max(1.0, self.height() - margin_top - margin_bottom),
        )

        painter.setPen(QColor(pal.text))
        painter.drawText(
            QRectF(0, 4, self.width(), 20),
            Qt.AlignmentFlag.AlignHCenter,
            self._title,
        )

        if not self._bins or self._stats is None or self._stats.count == 0:
            painter.setPen(QColor(pal.text_muted))
            painter.drawText(plot, Qt.AlignmentFlag.AlignCenter, "No data")
            painter.end()
            return

        max_count = max(b.count for b in self._bins) or 1
        low = self._bins[0].low
        high = self._bins[-1].high
        span = high - low or 1.0

        def x_for(value: float) -> float:
            return plot.left() + (value - low) / span * plot.width()

        # axes
        painter.setPen(QPen(QColor(pal.border), 1))
        painter.drawLine(plot.bottomLeft(), plot.bottomRight())
        painter.drawLine(plot.topLeft(), plot.bottomLeft())

        # y ticks (0 and max)
        painter.setPen(QColor(pal.text_muted))
        painter.drawText(
            QRectF(0, plot.top() - 8, margin_left - 6, 16),
            Qt.AlignmentFlag.AlignRight,
            str(max_count),
        )
        painter.drawText(
            QRectF(0, plot.bottom() - 8, margin_left - 6, 16),
            Qt.AlignmentFlag.AlignRight,
            "0",
        )

        # bars
        bar_gap = 2.0
        bar_width = plot.width() / len(self._bins)
        for hist_bin in self._bins:
            height = hist_bin.count / max_count * plot.height()
            left = x_for(hist_bin.low)
            rect = QRectF(
                left + bar_gap / 2,
                plot.bottom() - height,
                max(1.0, bar_width - bar_gap),
                height,
            )
            is_outlier_bin = self._stats.stdev > 0 and hist_bin.low >= self._stats.outlier_threshold
            painter.fillRect(rect, QColor(pal.bar_outlier if is_outlier_bin else pal.bar))
            if hist_bin.count:
                painter.setPen(QColor(pal.text_muted))
                painter.drawText(
                    QRectF(rect.left() - bar_width, plot.bottom() - height - 16, bar_width * 3, 14),
                    Qt.AlignmentFlag.AlignHCenter,
                    str(hist_bin.count),
                )

        # x labels (min / max)
        painter.setPen(QColor(pal.text_muted))
        painter.drawText(
            QRectF(plot.left() - 20, plot.bottom() + 6, 60, 16),
            Qt.AlignmentFlag.AlignLeft,
            f"{low:g}",
        )
        painter.drawText(
            QRectF(plot.right() - 40, plot.bottom() + 6, 60, 16),
            Qt.AlignmentFlag.AlignRight,
            f"{high:g}",
        )

        def vline(value: float, color: str, label: str) -> None:
            if not (low <= value <= high):
                return
            x = x_for(value)
            painter.setPen(QPen(QColor(color), 1.5, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
            painter.setPen(QColor(color))
            painter.drawText(QPointF(x + 3, plot.top() + 10), label)

        vline(self._stats.mean, pal.mean_line, f"mean {self._stats.mean:.1f}")
        vline(self._stats.median, pal.mean_line, f"median {self._stats.median:.1f}")
        if self._threshold is not None:
            vline(self._threshold, pal.threshold_line, f"threshold {self._threshold:g}")

        painter.end()
