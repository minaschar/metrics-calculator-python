"""Dotted base classes.

`abc.ABC` -> "ABC" and the project-local `base.Component` -> "Component",
so `Handler` is a child of `Component`: `Handler` DIT is 1 and
`Component` NOCC is 1.
"""
import abc


class Component:
    def render(self):
        return ""


class Handler(abc.ABC, base.Component):
    def handle(self, event):
        return event
