"""Structural facts pulled from a parsed module: classes, their methods,
fields and declared base names. The first pass the rest of the engine
builds on -- it computes no metric itself.

Scope notes, all reflected in ``docs/metrics.md``:

- A method is any ``def`` / ``async def`` whose name appears in the class,
  functions nested inside a method body included; same-named definitions
  collapse to one.
- A class defined inside a *method* body is recorded twice -- once while
  that method is walked, once by the module-level ``ast.walk`` -- and
  while its body is processed the "current class" is repointed at it, so
  attribute writes later in that method are attributed to the nested
  class. This is a deliberate, documented quirk, not a bug to fix here.
- Only ``ast.Name`` and ``ast.Attribute`` bases are recognised
  (``class Foo(pkg.Base)`` -> ``"Base"``); only positional parameters are
  counted per method; fields are found syntactically, from plain,
  annotated and augmented assignments only.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

_FUNC_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)
_FuncDef = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True, slots=True)
class MethodInfo:
    name: str
    parameters: tuple[str, ...]


@dataclass(slots=True)
class ClassFacts:
    name: str
    file_name: str
    ast_node: ast.ClassDef
    base_names: tuple[str, ...] = ()
    methods: dict[str, MethodInfo] = field(default_factory=dict)
    fields: set[str] = field(default_factory=set)


@dataclass(slots=True)
class FileFacts:
    path: Path
    module_ast: ast.Module
    source_lines: tuple[str, ...] = ()
    classes: list[ClassFacts] = field(default_factory=list)


def _base_names(node: ast.ClassDef) -> tuple[str, ...]:
    # `class Foo(Base)` -> "Base"; `class Foo(pkg.mod.Base)` -> "Base".
    # Anything more exotic (a subscript, a call) is skipped.
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return tuple(names)


class _ClassLevelFieldCollector(ast.NodeVisitor):
    """Every `Store` name anywhere under a class-body assignment becomes
    a `ClassName.<name>` field."""

    def __init__(self, class_name: str, fields: set[str]) -> None:
        self._class_name = class_name
        self._fields = fields

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self._fields.add(f"{self._class_name}.{node.id}")


class _StructureVisitor(ast.NodeVisitor):
    """Run once over a module. ``classes`` ends up with one ``ClassFacts``
    per ``visit_ClassDef`` call, in ``ast.walk`` order (a method-nested
    class therefore appears twice -- see the module docstring)."""

    def __init__(self, file_name: str) -> None:
        self._file_name = file_name
        self._current: ClassFacts | None = None
        self.classes: list[ClassFacts] = []

    def visit_Module(self, node: ast.Module) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                self.visit_ClassDef(child)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        facts = ClassFacts(
            name=node.name,
            file_name=self._file_name,
            ast_node=node,
            base_names=_base_names(node),
        )
        self._current = facts
        self.classes.append(facts)
        class_level = _ClassLevelFieldCollector(node.name, facts.fields)
        for child in node.body:
            if isinstance(child, _FUNC_DEFS):
                self._visit_func(child)
            elif isinstance(child, ast.Assign | ast.AnnAssign | ast.AugAssign):
                # `x = ...`, `x: int = 0`, `x += 1`
                class_level.generic_visit(child)

    def _visit_func(self, node: _FuncDef) -> None:
        assert self._current is not None
        params = tuple(arg.arg for arg in node.args.args)
        self._current.methods[node.name] = MethodInfo(node.name, params)
        # Descend: nested `def`s become methods too, a nested class
        # repoints `self._current`, and `self.x = ...` writes are picked
        # up by visit_Attribute.
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._current is None or not isinstance(node.ctx, ast.Store):
            return
        if not isinstance(node.value, ast.Name):
            return
        if node.value.id == "self":
            self._current.fields.add(f"self.{node.attr}")
        elif node.value.id == self._current.name:
            self._current.fields.add(f"{self._current.name}.{node.attr}")


def extract_classes(file_facts: FileFacts) -> list[ClassFacts]:
    """Every class in the module, nested ones included, in ``ast.walk``
    order (a method-nested class appears twice -- see the module
    docstring)."""
    visitor = _StructureVisitor(file_facts.path.name)
    visitor.visit_Module(file_facts.module_ast)
    return visitor.classes
