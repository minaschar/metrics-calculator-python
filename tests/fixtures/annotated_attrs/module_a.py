"""Class attributes declared with annotations / augmented assignment.

The pre-rewrite engine only inspected plain `ast.Assign`, so `limit`,
`name`, `seen` and the in-method `self.cache` annotation were all missed,
under-reporting WAC and SIZE2 (Phase 5, item 7).
"""


class Config:
    limit: int = 10
    name: str
    seen = 0

    def bump(self):
        self.seen += 1
        self.cache: dict = {}
        return self.limit
