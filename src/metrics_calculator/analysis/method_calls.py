"""Calls to methods of other objects, made from a class's own methods.

Computed once per class and shared by RFC, MPC and CBO -- the original
tool ran an equivalent walk three separate times per class.
"""

from __future__ import annotations

import ast
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

_FUNC_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)


@dataclass(frozen=True, slots=True)
class RemoteCall:
    instance_name: str
    method_name: str


def _call_of(node: ast.Call) -> RemoteCall | None:
    """The ``instance.method`` a call site invokes, or ``None`` if it is
    not an attribute call on a simple receiver.

    Phase 5, item 4: only attributes in *call position* count. The
    original walked every ``Call``'s whole subtree, so ``foo(bar.baz)``
    recorded ``bar.baz`` as a remote call even though it is just an
    argument read -- systematically inflating MPC and CBO.
    """
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None  # a bare name call, or a subscript/lambda callee
    receiver = func.value
    if isinstance(receiver, ast.Name):
        return RemoteCall(receiver.id, func.attr)
    if isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name):
        # `factory().method(...)` -- the original credited this to the
        # factory name; kept.
        return RemoteCall(receiver.func.id, func.attr)
    return None


class _MethodCallVisitor(ast.NodeVisitor):
    """Records a call ``obj.method(...)`` once per call site, when
    ``method`` is the name of a method defined by some class in the
    project (name-only matching -- no type resolution).

    Phase 5, item 3: the original appended the call once *per file* that
    contained a class defining that name (`validate_remote_method`'s
    `break` exited only the inner class loop), inflating MPC and CBO.
    `defined_methods` is now a flat set and each call site counts once.
    """

    def __init__(self, class_name: str, defined_methods: AbstractSet[str]) -> None:
        self._class_name = class_name
        self._defined_methods = defined_methods
        self.calls: list[RemoteCall] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.body:
            if isinstance(child, _FUNC_DEFS):
                self._visit_func(child)

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._record(_call_of(child))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    def _record(self, call: RemoteCall | None) -> None:
        if call is None or not call.method_name:
            return
        if call.instance_name in ("self", self._class_name):
            return
        if call.method_name in self._defined_methods:
            self.calls.append(call)


def remote_method_calls(
    node: ast.ClassDef, class_name: str, defined_methods: AbstractSet[str]
) -> list[RemoteCall]:
    visitor = _MethodCallVisitor(class_name, defined_methods)
    visitor.visit_ClassDef(node)
    return visitor.calls
