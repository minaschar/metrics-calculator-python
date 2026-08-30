"""Lines-of-code counting."""

from __future__ import annotations

import ast
from collections.abc import Sequence


def lines_of_code(node: ast.ClassDef, file_lines: Sequence[str]) -> int:
    """Counts non-blank lines spanned by the class body.

    `file_lines` is the full source file split into lines, read once per
    file (during discovery) and shared across every class in it -- the
    original tool re-read the whole file from disk once per class.
    """
    assert node.end_lineno is not None  # guaranteed by ast.parse for real source
    total = node.end_lineno - node.lineno + 1
    body_lines = file_lines[node.lineno - 1 : node.end_lineno]
    blank = sum(1 for line in body_lines if not line.strip())
    return total - blank
