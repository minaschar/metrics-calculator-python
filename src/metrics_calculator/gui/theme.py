"""Palette and Qt stylesheet, light and dark.

Seeded from the original tool's colours -- deep blue ``#224562`` and
Python yellow ``#FFD43B`` -- but reworked into a full token set with
readable contrast in both modes instead of inline ``setStyleSheet``
strings repeated per widget.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Mode(StrEnum):
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True, slots=True)
class Palette:
    mode: Mode
    window: str
    surface: str
    surface_alt: str
    text: str
    text_muted: str
    border: str
    accent: str
    accent_text: str
    selection: str
    selection_text: str
    # Semantic fills for the results table and the histogram.
    over_threshold_bg: str
    over_threshold_fg: str
    outlier_bg: str
    outlier_fg: str
    bar: str
    bar_outlier: str
    threshold_line: str
    mean_line: str


_ACCENT = "#224562"
_ACCENT_LIGHT = "#3f7cad"
_YELLOW = "#FFD43B"

LIGHT = Palette(
    mode=Mode.LIGHT,
    window="#f4f5f7",
    surface="#ffffff",
    surface_alt="#eef1f4",
    text="#1c2733",
    text_muted="#5c6b7a",
    border="#d3d9df",
    accent=_ACCENT,
    accent_text="#ffffff",
    selection=_ACCENT_LIGHT,
    selection_text="#ffffff",
    over_threshold_bg="#fbe3e0",
    over_threshold_fg="#8a2a1f",
    outlier_bg="#fff4d6",
    outlier_fg="#7a5b06",
    bar=_ACCENT_LIGHT,
    bar_outlier="#e0a106",
    threshold_line="#c0392b",
    mean_line="#5c6b7a",
)

DARK = Palette(
    mode=Mode.DARK,
    window="#1b2027",
    surface="#232a33",
    surface_alt="#2b333d",
    text="#e6ebf0",
    text_muted="#9aa7b3",
    border="#3a444f",
    accent=_YELLOW,
    accent_text="#1c2733",
    selection="#3f7cad",
    selection_text="#ffffff",
    over_threshold_bg="#4a2521",
    over_threshold_fg="#f3b7ae",
    outlier_bg="#463c1c",
    outlier_fg="#f0d488",
    bar="#4f92c9",
    bar_outlier=_YELLOW,
    threshold_line="#e57368",
    mean_line="#9aa7b3",
)

PALETTES: dict[Mode, Palette] = {Mode.LIGHT: LIGHT, Mode.DARK: DARK}


def palette(mode: Mode) -> Palette:
    return PALETTES[mode]


def stylesheet(p: Palette) -> str:
    return f"""
    QWidget {{
        background: {p.window};
        color: {p.text};
        font-size: 10.5pt;
    }}
    QMainWindow, QDialog {{ background: {p.window}; }}
    QFrame#Card, QTabWidget::pane {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
    }}
    QLabel#Heading {{ font-size: 13pt; font-weight: 600; }}
    QLabel#Muted {{ color: {p.text_muted}; }}
    QTabBar::tab {{
        background: transparent;
        color: {p.text_muted};
        padding: 7px 16px;
        border: none;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{
        color: {p.text};
        border-bottom: 2px solid {p.accent};
    }}
    QPushButton {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 6px;
        padding: 6px 14px;
    }}
    QPushButton:hover {{ border-color: {p.accent}; }}
    QPushButton:disabled {{ color: {p.text_muted}; }}
    QPushButton#Primary {{
        background: {p.accent};
        color: {p.accent_text};
        border: none;
        font-weight: 600;
    }}
    QPushButton#Primary:disabled {{ background: {p.surface_alt}; color: {p.text_muted}; }}
    QLineEdit, QComboBox {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 6px;
        padding: 5px 8px;
    }}
    QLineEdit:focus, QComboBox:focus {{ border-color: {p.accent}; }}
    QTableView {{
        background: {p.surface};
        alternate-background-color: {p.surface_alt};
        gridline-color: {p.border};
        border: 1px solid {p.border};
        border-radius: 8px;
        selection-background-color: {p.selection};
        selection-color: {p.selection_text};
    }}
    QHeaderView::section {{
        background: {p.surface_alt};
        color: {p.text_muted};
        padding: 6px 8px;
        border: none;
        border-right: 1px solid {p.border};
        border-bottom: 1px solid {p.border};
        font-weight: 600;
    }}
    QProgressBar {{
        background: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 6px;
        text-align: center;
        height: 16px;
    }}
    QProgressBar::chunk {{ background: {p.accent}; border-radius: 5px; }}
    QStatusBar {{ background: {p.surface}; color: {p.text_muted}; }}
    QTextBrowser {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 8px;
    }}
    """
