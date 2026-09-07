"""Per-method field usage and the LCOM (Lack of Cohesion in Methods) score."""

from __future__ import annotations

import ast
from collections.abc import Mapping

_FUNC_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)
_NESTED_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _method_field_uses(
    node: ast.FunctionDef | ast.AsyncFunctionDef, known: frozenset[str]
) -> frozenset[str]:
    """The known fields (`self.x`, `Klass.x`) referenced directly in this
    method's body. The walk stops at any nested function or class: their
    attribute use belongs to their own scope, not this method's cohesion.
    """
    used: set[str] = set()
    stack: list[ast.AST] = list(ast.iter_child_nodes(node))
    while stack:
        current = stack.pop()
        if isinstance(current, _NESTED_SCOPES):
            continue
        if isinstance(current, ast.Attribute) and isinstance(current.value, ast.Name):
            attr = f"{current.value.id}.{current.attr}"
            if attr in known:
                used.add(attr)
        stack.extend(ast.iter_child_nodes(current))
    return frozenset(used)


def field_uses_by_method(
    node: ast.ClassDef, known_fields: frozenset[str]
) -> dict[str, frozenset[str]]:
    return {
        child.name: _method_field_uses(child, known_fields)
        for child in node.body
        if isinstance(child, _FUNC_DEFS)
    }


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
