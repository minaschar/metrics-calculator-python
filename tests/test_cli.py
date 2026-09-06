"""CLI-level checks: exit codes, and that machine-readable output on
stdout is emitted verbatim (Rich must not treat a bracketed substring in
a name as a style tag)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from metrics_calculator.cli.app import app

runner = CliRunner()


@pytest.fixture
def project(tmp_path: Path) -> Path:
    # `[dim]` in the name is a valid Rich style tag: with markup enabled
    # `console.print` would silently strip it from stdout output.
    (tmp_path / "we[i-rd][dim].py").write_text(
        "class Sample:\n    def run(self):\n        return 1\n", encoding="utf-8"
    )
    return tmp_path


def test_analyze_json_stdout_is_verbatim_and_parseable(project: Path) -> None:
    result = runner.invoke(app, ["analyze", str(project), "-f", "json", "--no-progress"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1
    names = [c["file_name"] for f in payload["files"] for c in f["classes"]]
    assert names == ["we[i-rd][dim].py"]


def test_analyze_csv_stdout_is_verbatim(project: Path) -> None:
    result = runner.invoke(app, ["analyze", str(project), "-f", "csv", "--no-progress"])
    assert result.exit_code == 0
    assert "we[i-rd][dim].py" in result.stdout


def test_analyze_missing_path_exits_2(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", str(tmp_path / "nope"), "--no-progress"])
    assert result.exit_code == 2


def test_fail_under_gate(project: Path) -> None:
    ok = runner.invoke(app, ["analyze", str(project), "--fail-under", "NOM=99", "--no-progress"])
    assert ok.exit_code == 0
    bad = runner.invoke(app, ["analyze", str(project), "--fail-under", "NOM=0", "--no-progress"])
    assert bad.exit_code == 1
    unknown = runner.invoke(
        app, ["analyze", str(project), "--fail-under", "BOGUS=1", "--no-progress"]
    )
    assert unknown.exit_code == 2


def test_diff_same_project_is_clean(project: Path) -> None:
    result = runner.invoke(app, ["diff", str(project), str(project)])
    assert result.exit_code == 0
    assert "No differences" in result.stdout
