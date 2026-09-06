"""The in-app metrics manual, generated from the registry.

The original tool hand-built a 624-line window from ``label_2`` through
``label_56`` with every metric description pasted into layout code. Here
the manual is derived from :data:`METRIC_REGISTRY` and
:data:`PROJECT_METRIC_REGISTRY` -- adding a metric to the registry adds it
to the manual with no further work. Qt-free so it can be tested directly.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from ..registry import METRIC_REGISTRY, PROJECT_METRIC_REGISTRY
from ..results import QmoodMetrics


@dataclass(frozen=True, slots=True)
class ManualEntry:
    abbreviation: str
    name: str
    category: str
    description: str
    source: str
    computed: bool


def manual_entries() -> list[ManualEntry]:
    entries = [
        ManualEntry(m.abbreviation, m.name, m.category, m.description, m.source, computed=True)
        for m in METRIC_REGISTRY.values()
    ]
    entries += [
        ManualEntry(m.abbreviation, m.name, "project", m.description, m.source, computed=True)
        for m in PROJECT_METRIC_REGISTRY.values()
    ]
    # QMOOD design-quality attributes are declared on the result type but
    # never computed (carried over from the original tool, pending a Phase
    # 5 decision). Surface them here as explicitly unimplemented rather
    # than dropping them silently.
    entries += [
        ManualEntry(
            field.name,
            field.name.replace("_", " ").title(),
            "qmood",
            "Bansiya & Davis design-quality attribute. Declared for API "
            "completeness but not yet computed by this tool.",
            "Bansiya & Davis (2002)",
            computed=False,
        )
        for field in dataclasses.fields(QmoodMetrics)
    ]
    return entries


def manual_html(*, dark: bool = False) -> str:
    """Render the manual as a standalone HTML fragment for ``QTextBrowser``."""
    muted = "#9aa7b3" if dark else "#5c6b7a"
    rule = "#3a444f" if dark else "#d3d9df"
    accent = "#FFD43B" if dark else "#224562"

    by_category: dict[str, list[ManualEntry]] = {}
    for entry in manual_entries():
        by_category.setdefault(entry.category, []).append(entry)

    parts = [
        f"<style>h2{{color:{accent};margin-top:1.2em}}"
        f".src{{color:{muted};font-size:9pt}}"
        f".todo{{color:{muted};font-style:italic}}"
        f"hr{{border:none;border-top:1px solid {rule}}}</style>"
    ]
    for category, items in by_category.items():
        parts.append(f"<h2>{category.title()}</h2>")
        for entry in items:
            parts.append(f"<p><b>{entry.abbreviation}</b> &mdash; {entry.name}<br>")
            parts.append(f"{entry.description}<br>")
            if not entry.computed:
                parts.append("<span class='todo'>Not computed by this release.</span><br>")
            parts.append(f"<span class='src'>{entry.source}</span></p><hr>")
    return "".join(parts)
