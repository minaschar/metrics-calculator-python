"""Calls to methods of other objects, made from a class's own methods.

Computed once per class and shared by RFC, MPC and CBO -- the original
tool ran an equivalent walk three separate times per class.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RemoteCall:
    instance_name: str
    method_name: str


class _MethodCallVisitor(ast.NodeVisitor):
    """A call is only recorded if some class *somewhere* in the project
    defines a method of that name -- and, faithfully reproducing the
    original tool's defect, once per file that does so (see project brief
    Phase 5, item 3: `validate_remote_method`'s `break` only exits the
    inner per-file loop, so one call site is counted once per matching
    file). `files_with_method` maps a method name to the number of
    distinct files containing a class that defines it. Fixing the
    double-count is out of scope until Phase 5.
    """

    def __init__(self, class_name: str, files_with_method: Mapping[str, int]) -> None:
        self._class_name = class_name
        self._files_with_method = files_with_method
        self.calls: list[RemoteCall] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_FunctionDef(child)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self.generic_visit(child)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            self._record(node.attr, node.value.id)
        elif isinstance(node.value, ast.Call):
            # Nested exactly as the original: when the receiver is a call
            # whose callee is *not* a bare name (a chained call like
            # `formatter.getvalue().rstrip(...)`), the original does
            # nothing and does NOT recurse. Recursing here would let the
            # outer `ast.walk` loop and this descent both reach the inner
            # `formatter.getvalue`, double-counting it (MPC/CBO).
            if isinstance(node.value.func, ast.Name):
                self._record(node.attr, node.value.func.id)
        else:
            self.generic_visit(node)

    def _record(self, method_name: str, instance_name: str) -> None:
        if not method_name or instance_name in ("self", self._class_name):
            return
        file_count = self._files_with_method.get(method_name, 0)
        self.calls.extend(RemoteCall(instance_name, method_name) for _ in range(file_count))


def remote_method_calls(
    node: ast.ClassDef, class_name: str, files_with_method: Mapping[str, int]
) -> list[RemoteCall]:
    visitor = _MethodCallVisitor(class_name, files_with_method)
    visitor.visit_ClassDef(node)
    return visitor.calls
