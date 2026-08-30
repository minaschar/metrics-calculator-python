class Filterer:
    def even_numbers(self, values):
        return [v for v in values if v % 2 == 0]

    def squared_map(self, values):
        return {v: v * v for v in values}
