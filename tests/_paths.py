"""Shared locations for the fixture projects and their committed
golden snapshots."""

from __future__ import annotations

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
FIXTURE_NAMES = sorted(p.name for p in FIXTURES_DIR.iterdir() if p.is_dir())
