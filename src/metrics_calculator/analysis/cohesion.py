"""Per-method field usage and the LCOM (Lack of Cohesion in Methods) score."""

from __future__ import annotations

import ast
from collections.abc import Mapping


class _FieldUseVisitor(ast.NodeVisitor):
    """Mirrors the original LCOMNodeVisitor, including its known scoping
    defect: a single accumulator set is shared and merely cleared between
    methods, so attribute uses inside a nested function or nested class
    leak into the enclosing method's usage set (see project brief Phase 5,
    item 6). Fixing that is out of scope until Phase 5.
    """

    def __init__(self, known_fields: frozenset[str]) -> None:
        self._known_fields = known_fields
        self._current: set[str] = set()
        self.uses_by_method: dict[str, frozenset[str]] = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_FunctionDef(child)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.generic_visit(node)
        self.uses_by_method[node.name] = frozenset(self._current)
        self._current.clear()

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            attr = f"{node.value.id}.{node.attr}"
            if attr in self._known_fields:
                self._current.add(attr)


def field_uses_by_method(
    node: ast.ClassDef, known_fields: frozenset[str]
) -> dict[str, frozenset[str]]:
    visitor = _FieldUseVisitor(known_fields)
    visitor.visit_ClassDef(node)
    return visitor.uses_by_method


def lack_of_cohesion(uses_by_method: Mapping[str, frozenset[str]]) -> int:
    method_field_sets = list(uses_by_method.values())
    cohesive = 0
    non_cohesive = 0
    for i in range(len(method_field_sets)):
        for j in range(i + 1, len(method_field_sets)):
            if method_field_sets[i] & method_field_sets[j]:
                cohesive += 1
            else:
                non_cohesive += 1
    return max(non_cohesive - cohesive, 0)
