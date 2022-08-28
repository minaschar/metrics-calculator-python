class CohesionCategory:

    LCOM = 0
    CAMC = 0
    NOT = 0

# Metrics getters
    def get_LCOM(self):
        return self.LCOM

    def get_CAMC(self):
        return self.CAMC

    def get_NOT(self):
        return self.NOT


# Calculating the Metrics

    def set_LCOM(self, value):
        self.LCOM = value

    def set_CAMC(self, value):
        self.CAMC = value

    def set_NOT(self, value):
        self.NOT = value
