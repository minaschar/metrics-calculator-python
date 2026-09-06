"""`docs/metrics.md` is generated from the registry -- fail if it drifted."""

from __future__ import annotations

from pathlib import Path

from metrics_calculator.docs import render_metrics_markdown

_DOCS = Path(__file__).resolve().parent.parent / "docs" / "metrics.md"


def test_metrics_doc_is_in_sync_with_registry() -> None:
    assert _DOCS.is_file(), "run `python -m metrics_calculator.docs`"
    assert _DOCS.read_text(encoding="utf-8") == render_metrics_markdown(), (
        "docs/metrics.md is stale; run `python -m metrics_calculator.docs`"
    )


def test_every_registry_metric_documents_its_formula() -> None:
    from metrics_calculator.registry import METRIC_REGISTRY, PROJECT_METRIC_REGISTRY

    for cm in METRIC_REGISTRY.values():
        assert cm.formula.strip(), f"{cm.abbreviation} has no 'formula' text"
    for pm in PROJECT_METRIC_REGISTRY.values():
        assert pm.formula.strip(), f"{pm.abbreviation} has no 'formula' text"
