"""Proves the new `metrics_calculator` engine reproduces the legacy
engine's output exactly, bugs included, against the same golden snapshots
used for the legacy engine in test_golden_snapshots.py.

Unlike that file, this test never writes snapshots -- a mismatch here
means the Phase 1 rewrite changed behaviour, which is exactly what these
snapshots exist to catch. If a diff is expected here, it belongs in
Phase 5, deliberately, with the snapshot updated in its own commit.
"""

from __future__ import annotations

import json

import pytest
from _new_engine_harness import analyze_fixture
from _paths import FIXTURE_NAMES, FIXTURES_DIR, SNAPSHOTS_DIR


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_new_engine_matches_snapshot(fixture_name: str) -> None:
    result = analyze_fixture(FIXTURES_DIR / fixture_name)
    snapshot_path = SNAPSHOTS_DIR / f"{fixture_name}.json"
    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert result == expected
