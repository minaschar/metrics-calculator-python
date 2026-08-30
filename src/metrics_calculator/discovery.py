"""File discovery and AST parsing, with skipped/unparseable files surfaced
as diagnostics instead of printed and dropped.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from .config import AnalysisConfig
from .diagnostics import Diagnostic
from .extraction import FileFacts

logger = logging.getLogger(__name__)


def _find_python_files(root: Path, config: AnalysisConfig) -> list[Path]:
    matched: set[Path] = set()
    for pattern in config.include:
        matched.update(p for p in root.glob(pattern) if p.is_file())

    if config.exclude:
        matched = {
            p
            for p in matched
            if not any(p.relative_to(root).match(pattern) for pattern in config.exclude)
        }

    # Sorted for deterministic, reproducible runs. The original tool relied
    # on os.walk's (OS-dependent, unspecified) directory order, which was
    # never a stable contract to begin with.
    return sorted(matched)


def discover_files(
    root: Path, config: AnalysisConfig | None = None
) -> tuple[list[FileFacts], list[Diagnostic]]:
    config = config or AnalysisConfig()
    files: list[FileFacts] = []
    diagnostics: list[Diagnostic] = []

    for path in _find_python_files(root, config):
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            message = f"could not read file: {exc}"
            logger.warning("%s: %s", path, message)
            diagnostics.append(Diagnostic(path, message))
            continue

        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            message = f"syntax error: {exc.msg} (line {exc.lineno})"
            logger.warning("%s: %s", path, message)
            diagnostics.append(Diagnostic(path, message))
            continue

        files.append(FileFacts(path=path, module_ast=tree, source_lines=tuple(source.splitlines())))

    return files, diagnostics
