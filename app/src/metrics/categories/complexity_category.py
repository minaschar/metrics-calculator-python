class ComplexityCategory:

    DIT = 0
    RFC = 0
    WMPC1 = 0.0
    WMPC2 = 0

# Metrics getters
    def getDIT(self):
        return self.DIT

    def getRFC(self):
        return self.RFC

    def getWMPC1(self):
        return self.WMPC1

    def getWMPC2(self):
        return self.WMPC2

# Set value to the Metrics
    def setDIT(self, value):
        self.DIT = value

    def setRFC(self, value):
        self.RFC = value

    def setWMPC1(self, value):
        self.WMPC1 = value

    def setWMPC2(self, value):
        self.WMPC2 = value
