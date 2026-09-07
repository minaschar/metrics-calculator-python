"""Class attributes declared with annotations and augmented assignment.

`limit` (annotated), `name` (bare annotation), `seen` (plain), `Config.seen`
and `self.cache` (annotated, in a method) are all fields, so `Config` has
WAC 5 / SIZE2 6.
"""


class Config:
    limit: int = 10
    name: str
    seen = 0

    def bump(self):
        self.seen += 1
        self.cache: dict = {}
        return self.limit
