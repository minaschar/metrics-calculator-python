"""A class defined inside a method body.

`Cache` is recorded twice (NOC 3 for two source classes), and because the
"current class" is repointed at `Cache` while its body is walked, the
`self.cache` / `self.dirty` writes after it are attributed to `Cache`,
not `Outer`. A deliberate, documented quirk of the extraction pass.
"""


class Outer:
    def configure(self, name):
        class Cache:
            def get(self, key):
                return None

        self.cache = Cache()
        self.dirty = True
        return self.cache
