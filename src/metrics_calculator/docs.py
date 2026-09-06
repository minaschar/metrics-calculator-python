"""Generate ``docs/metrics.md`` from the metric registry.

Run ``python -m metrics_calculator.docs`` to (re)write it. A test checks
that the committed file is in sync, so a registry change that isn't
reflected in the docs fails CI.
"""

from __future__ import annotations

from pathlib import Path

from .registry import (
    METRIC_REGISTRY,
    PROJECT_METRIC_REGISTRY,
    UNIMPLEMENTED_METRICS,
)

_HEADER = """\
# Metrics

Every value this tool reports, with the formula **as implemented** -- which
is not always the textbook definition. This file is generated from
`metrics_calculator.registry`; run `python -m metrics_calculator.docs` to
refresh it.

Sources: Chidamber & Kemerer, *A Metrics Suite for Object Oriented Design*
(1994); Li & Henry, *Object-oriented metrics that predict maintainability*
(1993); Bansiya & Davis, *A hierarchical model for object-oriented design
quality assessment* (2002).
"""

_CATEGORY_ORDER = ["size", "complexity", "coupling", "cohesion", "project", "qmood"]
_CATEGORY_TITLES = {
    "size": "Size",
    "complexity": "Complexity",
    "coupling": "Coupling",
    "cohesion": "Cohesion",
    "project": "Project-level",
    "qmood": "QMOOD design attributes (not implemented)",
}


_Row = tuple[str, str, str, str, str, str, bool]


def _rows() -> list[_Row]:
    rows: list[_Row] = []
    for cm in METRIC_REGISTRY.values():
        rows.append(
            (cm.category, cm.abbreviation, cm.name, cm.description, cm.formula, cm.source, True)
        )
    for pm in PROJECT_METRIC_REGISTRY.values():
        rows.append(
            ("project", pm.abbreviation, pm.name, pm.description, pm.formula, pm.source, True)
        )
    for um in UNIMPLEMENTED_METRICS:
        rows.append((um.category, um.abbreviation, um.name, um.reason, "", um.source, False))
    return rows


def _notes_for(abbreviation: str) -> str:
    m = METRIC_REGISTRY.get(abbreviation)
    if m is not None:
        return m.notes
    pm = PROJECT_METRIC_REGISTRY.get(abbreviation)
    return pm.notes if pm is not None else ""


def render_metrics_markdown() -> str:
    rows = _rows()
    by_category: dict[str, list[tuple[str, str, str, str, str, str, bool]]] = {}
    for row in rows:
        by_category.setdefault(row[0], []).append(row)

    lines: list[str] = [_HEADER.rstrip()]
    for category in _CATEGORY_ORDER:
        items = by_category.get(category)
        if not items:
            continue
        lines.append("")
        lines.append(f"## {_CATEGORY_TITLES[category]}")
        for _, abbr, name, description, formula, source, computed in items:
            lines.append("")
            heading = name if category == "qmood" else f"{abbr} — {name}"
            lines.append(f"### {heading}")
            lines.append("")
            lines.append(description)
            lines.append("")
            if computed:
                lines.append(f"- **As implemented:** {formula}")
                notes = _notes_for(abbr)
                if notes:
                    lines.append(f"- **Approximation:** {notes}")
            else:
                lines.append("- **Status:** not computed by this release.")
            lines.append(f"- **Source:** {source}")
    return "\n".join(lines).rstrip() + "\n"


def _repo_docs_path() -> Path:
    """`<repo>/docs/metrics.md` when running from a source checkout."""
    repo_root = Path(__file__).resolve().parents[2]
    if not (repo_root / "pyproject.toml").is_file():
        raise RuntimeError(
            "docs/metrics.md can only be regenerated from a source checkout "
            "(no pyproject.toml found above this package)"
        )
    return repo_root / "docs" / "metrics.md"


def write() -> Path:
    path = _repo_docs_path()
    path.parent.mkdir(exist_ok=True)
    path.write_text(render_metrics_markdown(), encoding="utf-8")
    return path


if __name__ == "__main__":  # pragma: no cover
    print(f"wrote {write()}")
