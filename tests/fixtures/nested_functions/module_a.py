"""A method with functions nested in its body.

The pre-rewrite engine's InitCommonsNodeVisitor descends into method
bodies and counts every nested `def` as a method of the class, so NOM for
`Widget` is 4 (`build`, `_step`, `_finish`, `run`), not 2. LCOM's shared
accumulator also leaks `self.total` out of `_step`, and the
`helper.collect()` call made from `run` couples Widget to Registry.
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
