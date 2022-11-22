
class SizeCategory:

    NOCC = 0
    NOM = 0
    LOC = 0
    SIZE2 = 0
    NDC = 0
    DSC = 0
    NOP = 0
    CIS = 0
    NPM = 0
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

    def getNDC(self):
        return self.NDC

    def getDSC(self):
        return self.DSC

    def getNOP(self):
        return self.NOP

    def getCIS(self):
        return self.CIS

    def getNPM(self):
        return self.NPM

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

    def setNDC(self, value):
        self.NDC = value

    def setDSC(self, value):
        self.DSC = value

    def setNOP(self, value):
        self.NOP = value

    def setCIS(self, value):
        self.CIS = value

    def setNPM(self, value):
        self.NPM = value

    def setWAC(self, value):
        self.WAC = value
