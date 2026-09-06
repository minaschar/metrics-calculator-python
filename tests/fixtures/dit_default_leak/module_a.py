"""Subclass declared before its base, exercising the DIT misdirection.

`Leaf` is analysed before `Root`. `calc_dit(Leaf)` recurses into
`calc_dit(Root)` (Root's hierarchy is still the -1 default), which
repoints `curr_dit_class` at Root; when the recursion unwinds the write
lands on Root, and `Leaf` is never assigned. So `Leaf` keeps both
defaults -- `dit == 0` (a class attribute) and `hierarchy == -1` (an
instance attribute) -- which is why the two fields disagree here.
"""


class Leaf(Root):
    def describe(self):
        return "leaf"


class Root:
    def describe(self):
        return "root"
