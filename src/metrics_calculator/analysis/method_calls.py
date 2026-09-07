"""Calls to methods of other objects, made from a class's own methods.

Computed once per class and shared by RFC, MPC and CBO. Matching is by
method name only -- no type resolution -- so a call counts when *some*
class in the project defines a method of that name.
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
    """The ``receiver.method`` a call site invokes, or ``None`` when it is
    not an attribute call on a simple receiver.

    Only the callee attribute counts -- an attribute merely *read* as an
    argument (``foo(bar.baz)``) is not a call and must not inflate MPC or
    CBO.
    """
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None  # a bare-name call, or a subscript/lambda callee
    receiver = func.value
    if isinstance(receiver, ast.Name):
        return RemoteCall(receiver.id, func.attr)
    if isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name):
        # `factory().method(...)` is credited to the factory name.
        return RemoteCall(receiver.func.id, func.attr)
    return None


class _MethodCallVisitor(ast.NodeVisitor):
    """Records ``receiver.method(...)`` once per call site, when
    ``method`` is in ``defined_methods`` (the set of method names declared
    by any class in the project) and the receiver is not ``self`` or the
    class itself. Calls inside nested functions count for the class.
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
