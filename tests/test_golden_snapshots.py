"""Golden-snapshot regression net for the pre-rewrite analysis engine.

Each fixture under ``tests/fixtures/<name>/`` is run through today's engine
and the resulting per-class metric table is compared against a committed
JSON snapshot in ``tests/snapshots/<name>.json``.

These snapshots intentionally capture *current* behaviour, bugs included --
see the project brief's Phase 5 for the list of known defects (e.g. DIT/NOCC
miscalculation, MPC/CBO double-counting, async methods being invisible).
They exist to prove Phases 1-4 don't silently change behaviour while the
code is restructured; Phase 5 will update them deliberately, one fix at a
time, with the diff shown.

Run with ``SNAPSHOT_UPDATE=1`` to (re)write snapshots after a deliberate,
reviewed behaviour change. Never hand-edit a snapshot file.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from _analysis_harness import analyze_fixture

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"

FIXTURE_NAMES = sorted(p.name for p in FIXTURES_DIR.iterdir() if p.is_dir())


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_golden_snapshot(fixture_name: str) -> None:
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
