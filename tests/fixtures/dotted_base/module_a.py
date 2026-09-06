"""Dotted base class.

`Handler` inherits from `abc.ABC` and from the project-local
`base.Component`. The pre-rewrite HierarchyNodeVisitor ignored
`ast.Attribute` bases entirely, so `Handler` looked like a root (Phase 5,
item 9). Now `abc.ABC` -> "ABC" and `base.Component` -> "Component", so
Handler is a child of the project's Component and DIT/NOCC follow.
"""
import abc


class Component:
    def render(self):
        return ""


class Handler(abc.ABC, base.Component):
    def handle(self, event):
        return event
