"""A method with functions nested in its body.

Nested `def`s count as methods, so `Widget` has NOM 4 (`build`, `_step`,
`_finish`, `run`). `_step`'s `self.total` use does not leak into `build`'s
cohesion set (LCOM 1), and `run`'s `helper.collect()` couples `Widget` to
`Registry`.
"""


class Registry:
    def collect(self):
        return []


class Widget:
    def build(self, items):
        self.total = 0

        def _step(value):
            self.total += value
            return value * 2

        def _finish():
            return self.total

        results = [_step(item) for item in items]
        return _finish(), results

    def run(self, helper):
        return helper.collect()
