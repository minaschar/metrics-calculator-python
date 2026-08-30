class Fetcher:
    def __init__(self, url):
        self.url = url

    async def fetch(self):
        self.result = await self._get(self.url)
        return self.result

    async def _get(self, url):
        return url
