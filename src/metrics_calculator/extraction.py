"""Structural facts pulled from a parsed module: classes, their methods,
fields and declared base names. This is the "first pass" the rest of the
engine builds on -- it does not compute any metric itself.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


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
    # Only simple names (`class Foo(Base):`) are recognised. Dotted bases
    # (`class Foo(module.Base):`) are invisible to this tool -- see project
    # brief Phase 5, item 9; preserved here rather than fixed early.
    return tuple(base.id for base in node.bases if isinstance(base, ast.Name))


class _MethodBodyFieldCollector(ast.NodeVisitor):
    """Finds `self.x = ...` / `ClassName.x = ...` writes inside a method
    body. Only plain `ast.Assign` targets are recognised -- annotated
    (`x: int = 0`) and augmented (`x += 1`) assignments are missed, matching
    the original tool (see project brief Phase 5, item 7).
    """

    def __init__(self, class_name: str, fields: set[str]) -> None:
        self._class_name = class_name
        self._fields = fields

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if not isinstance(node.ctx, ast.Store) or not isinstance(node.value, ast.Name):
            return
        if node.value.id == "self":
            self._fields.add(f"self.{node.attr}")
        elif node.value.id == self._class_name:
            self._fields.add(f"{self._class_name}.{node.attr}")


class _ClassLevelFieldCollector(ast.NodeVisitor):
    """Finds class-level `x = ...` writes, including tuple/list unpacking
    targets (`a, b = 1, 2`)."""

    def __init__(self, class_name: str, fields: set[str]) -> None:
        self._class_name = class_name
        self._fields = fields

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self._fields.add(f"{self._class_name}.{node.id}")


def _extract_class(node: ast.ClassDef, file_name: str) -> ClassFacts:
    facts = ClassFacts(
        name=node.name, file_name=file_name, ast_node=node, base_names=_base_names(node)
    )
    method_collector = _MethodBodyFieldCollector(node.name, facts.fields)
    class_level_collector = _ClassLevelFieldCollector(node.name, facts.fields)

    for child in node.body:
        # Only plain `def` methods are recognised; `async def` methods are
        # invisible here, matching the original tool (see project brief
        # Phase 5, item 5).
        if isinstance(child, ast.FunctionDef):
            params = tuple(arg.arg for arg in child.args.args)
            facts.methods[child.name] = MethodInfo(child.name, params)
            method_collector.generic_visit(child)
        elif isinstance(child, ast.Assign):
            class_level_collector.generic_visit(child)

    return facts


def extract_classes(file_facts: FileFacts) -> list[ClassFacts]:
    """Flattens every class in the module, including nested ones, into a
    single list -- mirrors the original tool's `ast.walk`-based discovery,
    which does not distinguish nesting depth. Whether that flattening is
    the right taxonomy is an open question for Phase 3+, not addressed
    here.
    """
    return [
        _extract_class(node, file_facts.path.name)
        for node in ast.walk(file_facts.module_ast)
        if isinstance(node, ast.ClassDef)
    ]
