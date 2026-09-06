"""A class defined inside a method body.

The pre-rewrite engine processes `Cache` twice -- once while descending
`Outer.configure`, once from the module-level `ast.walk` -- so the
project ends up with two `Cache` entries, and while the first is being
processed `curr_class` is repointed at it and never restored, so
`self.dirty = True` (written after the nested class) lands on `Cache`
rather than `Outer`.
"""


class Outer:
    def configure(self, name):
        class Cache:
            def get(self, key):
                return None

        self.cache = Cache()
        self.dirty = True
        return self.cache
