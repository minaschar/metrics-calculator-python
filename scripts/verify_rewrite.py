"""Phase 4 verification: run the legacy engine and the new engine over the
same real-world project and prove they produce identical metrics, then
report how long each took.

Usage:
    python scripts/verify_rewrite.py <path-to-python-project> [<path> ...]

With no arguments it uses whatever `rich` resolves to in this environment.
Exits non-zero if any metric differs.
"""

from __future__ import annotations

import io
import os
import sys
import time
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
else:  # pragma: no cover
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "app"))  # legacy engine imports `src.*` from app/
sys.path.insert(0, str(_ROOT / "tests"))  # the two analyze_fixture harnesses

from _analysis_harness import analyze_fixture as legacy_analyze  # noqa: E402
from _engine_snapshot import analyze_fixture as new_analyze  # noqa: E402


def _flatten(payload: dict[str, Any]) -> dict[tuple[str, str, str], object]:
    flat: dict[tuple[str, str, str], object] = {}
    flat[("", "", "noc")] = payload["noc"]
    for file_entry in payload["files"]:
        fname = file_entry["file_name"]
        for cls in file_entry["classes"]:
            cname = cls["class_name"]
            for metric, value in cls.items():
                if metric == "class_name":
                    continue
                flat[(fname, cname, metric)] = value
    return flat


def _timed(fn, path: Path) -> tuple[dict[str, Any], float]:
    start = time.perf_counter()
    result = fn(path)
    return result, time.perf_counter() - start


def compare(path: Path) -> bool:
    print(f"\n=== {path} ===")
    n_files = sum(1 for _ in path.rglob("*.py"))
    print(f"{n_files} .py files")

    legacy_result, legacy_secs = _timed(legacy_analyze, path)
    new_result, new_secs = _timed(new_analyze, path)

    legacy_flat = _flatten(legacy_result)
    new_flat = _flatten(new_result)

    n_classes = sum(len(f["classes"]) for f in new_result["files"])
    print(f"{n_classes} classes, {len(new_flat)} metric values compared")
    print(f"legacy engine : {legacy_secs:8.3f} s")
    print(f"new engine    : {new_secs:8.3f} s")
    if new_secs > 0:
        print(f"speed-up      : {legacy_secs / new_secs:8.2f}x")

    if legacy_flat == new_flat:
        print("RESULT: identical ✓")
        return True

    only_legacy = legacy_flat.keys() - new_flat.keys()
    only_new = new_flat.keys() - legacy_flat.keys()
    differing = [k for k in legacy_flat.keys() & new_flat.keys() if legacy_flat[k] != new_flat[k]]

    print(
        f"RESULT: MISMATCH ✗  "
        f"{len(differing)} differing values, "
        f"{len(only_legacy)} only-legacy keys, {len(only_new)} only-new keys"
    )
    for key in sorted(only_legacy)[:20]:
        print(f"  only legacy: {key} = {legacy_flat[key]!r}")
    for key in sorted(only_new)[:20]:
        print(f"  only new   : {key} = {new_flat[key]!r}")
    for key in sorted(differing)[:40]:
        print(f"  {key}: legacy={legacy_flat[key]!r}  new={new_flat[key]!r}")
    return False


def _default_target() -> Path:
    import rich

    return Path(rich.__file__).parent


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or [_default_target()]
    all_ok = True
    for target in targets:
        if not target.is_dir():
            print(f"skip (not a directory): {target}")
            all_ok = False
            continue
        all_ok &= compare(target)
    print()
    print("ALL IDENTICAL" if all_ok else "DIVERGENCE FOUND")
    return 0 if all_ok else 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONHASHSEED", "0")
    raise SystemExit(main(sys.argv))
