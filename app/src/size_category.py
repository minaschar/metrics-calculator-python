
class SizeCategory:

    NOCC = 0
    NOM = 0
    LOC = 0
    SIZE2 = 0
    WAC = 0

# Metrics getters
    def getNOCC(self):
        return self.NOCC

    def getNOM(self):
        return self.NOM

    def getLOC(self):
        return self.LOC

    def getSIZE2(self):
        return self.SIZE2

    def getWAC(self):
        return self.WAC

# Set value to the Metrics
    def setNOCC(self, value):
        self.NOCC = value

    def setNOM(self, value):
        self.NOM = value

    def setLOC(self, value):
        self.LOC = value

    def setSIZE2(self, value):
        self.SIZE2 = value

    def setWAC(self, value):
        self.WAC = value
