class Client:
    def persist(self, store, blob):
        store.save(blob)
        return store.save(blob)
