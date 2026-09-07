"""Subclass declared before its base.

DIT must not depend on source or discovery order: `Leaf` has one project
ancestor so `Leaf` DIT is 1 and `Root` DIT is 0, regardless of `Leaf`
appearing first.
"""


class Leaf(Root):
    def describe(self):
        return "leaf"


class Root:
    def describe(self):
        return "root"
