"""Minimal placeholder entry point.

A full CLI (JSON/CSV/XLSX/HTML output, `--fail-under` thresholds, diff mode,
progress reporting) is Phase 2 of the modernization effort. This only
proves the package installs with a working console script.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .engine import analyze


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: metrics-calculator <path-to-project>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    result = analyze(root)
    print(f"{result.project_name}: {result.noc} classes across {len(result.files)} files")
    for diagnostic in result.diagnostics:
        print(diagnostic, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
