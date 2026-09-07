"""Golden-snapshot regression net for `metrics_calculator.analyze()`.

Each fixture under ``tests/fixtures/<name>/`` is analysed and its full
per-class metric table compared against ``tests/snapshots/<name>.json``.
A deliberate change to what a metric counts regenerates the affected
snapshots in the same commit, so its diff shows exactly which measured
values moved and why.

Run with ``SNAPSHOT_UPDATE=1`` to (re)write snapshots after a reviewed
change. Never hand-edit a snapshot file.
"""

from __future__ import annotations

import json
import os

import pytest
from _engine_snapshot import analyze_fixture
from _paths import FIXTURE_NAMES, FIXTURES_DIR, SNAPSHOTS_DIR


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_engine_matches_snapshot(fixture_name: str) -> None:
    result = analyze_fixture(FIXTURES_DIR / fixture_name)
    snapshot_path = SNAPSHOTS_DIR / f"{fixture_name}.json"

    if os.environ.get("SNAPSHOT_UPDATE") == "1":
        snapshot_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        pytest.skip(f"snapshot for {fixture_name!r} (re)written; rerun without SNAPSHOT_UPDATE")

    assert snapshot_path.exists(), (
        f"no golden snapshot for {fixture_name!r}; run with SNAPSHOT_UPDATE=1 to create one"
    )
    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert result == expected
