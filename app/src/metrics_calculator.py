from classDecl import Class


# In this class exists methods that calculates metrics for each class
class MetricsCalculator:

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMC1()

    def calcWMC1(self):
        self.classObj.getSizeCategoryMetrics().setWMC(len(self.classObj.get_methods()))
