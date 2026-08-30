"""Cyclomatic complexity, summed across a class's methods (feeds WMPC1)."""

from __future__ import annotations

import ast


class _CyclomaticComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.complexity = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_FunctionDef(child)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.complexity += 1
        self.generic_visit(node)

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
    """Sums a rough per-method cyclomatic complexity across the class.

    `async def` methods are invisible here, matching the original tool
    (see project brief Phase 5, item 5).
    """
    visitor = _CyclomaticComplexityVisitor()
    visitor.visit_ClassDef(node)
    return visitor.complexity
