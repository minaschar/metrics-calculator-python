"""Cyclomatic complexity, summed across a class's methods (feeds WMPC1)."""

from __future__ import annotations

import ast

_FUNC_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)


class _CyclomaticComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.complexity = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.body:
            if isinstance(child, _FUNC_DEFS):
                self._visit_func(child)

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.complexity += 1 + len(node.ifs)
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        self.complexity += len(node.cases)
        self.generic_visit(node)


def cyclomatic_complexity(node: ast.ClassDef) -> int:
    """Sum of an approximate per-method cyclomatic complexity across the
    class: 1 per method (``def`` or ``async def``, nested ones included)
    plus 1 for each branch/loop/comprehension clause and one per ``match``
    case. Boolean operators, ``except`` and ``assert`` are not counted."""
    visitor = _CyclomaticComplexityVisitor()
    visitor.visit_ClassDef(node)
    return visitor.complexity
