"""The in-app metrics manual, generated from the registry.

The original tool hand-built a 624-line window from ``label_2`` through
``label_56`` with every metric description pasted into layout code. Here
the manual is derived from :data:`METRIC_REGISTRY`,
:data:`PROJECT_METRIC_REGISTRY` and :data:`UNIMPLEMENTED_METRICS` --
adding a metric to the registry adds it to the manual (and to
``docs/metrics.md``) with no further work. Qt-free so it can be tested
directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..registry import METRIC_REGISTRY, PROJECT_METRIC_REGISTRY, UNIMPLEMENTED_METRICS


@dataclass(frozen=True, slots=True)
class ManualEntry:
    abbreviation: str
    name: str
    category: str
    description: str
    formula: str
    source: str
    notes: str
    computed: bool


def manual_entries() -> list[ManualEntry]:
    entries = [
        ManualEntry(
            m.abbreviation, m.name, m.category, m.description, m.formula, m.source, m.notes, True
        )
        for m in METRIC_REGISTRY.values()
    ]
    entries += [
        ManualEntry(
            m.abbreviation, m.name, "project", m.description, m.formula, m.source, m.notes, True
        )
        for m in PROJECT_METRIC_REGISTRY.values()
    ]
    entries += [
        ManualEntry(m.abbreviation, m.name, m.category, m.reason, "", m.source, "", computed=False)
        for m in UNIMPLEMENTED_METRICS
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
        f".formula{{font-family:monospace;font-size:9pt}}"
        f".src{{color:{muted};font-size:9pt}}"
        f".notes,.todo{{color:{muted};font-size:9pt}}"
        f".todo{{font-style:italic}}"
        f"hr{{border:none;border-top:1px solid {rule}}}</style>"
    ]
    for category, items in by_category.items():
        parts.append(f"<h2>{category.title()}</h2>")
        for entry in items:
            parts.append(f"<p><b>{entry.abbreviation}</b> &mdash; {entry.name}<br>")
            parts.append(f"{entry.description}<br>")
            if entry.formula:
                parts.append(f"<span class='formula'>as implemented: {entry.formula}</span><br>")
            if entry.notes:
                parts.append(f"<span class='notes'>{entry.notes}</span><br>")
            if not entry.computed:
                parts.append("<span class='todo'>Not computed by this release.</span><br>")
            parts.append(f"<span class='src'>{entry.source}</span></p><hr>")
    return "".join(parts)
