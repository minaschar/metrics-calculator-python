from classDecl import Class


# In this class exists methods that calculates metrics for each class
class MetricsCalculator:

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMC1()
        self.calcNOM()
        self.calcSIZE2()

    # Count the number of methods for each class in the project
    def calcNOM(self):
        self.classObj.getSizeCategoryMetrics().setNOM(len(self.classObj.get_methods()))

    # Need changes
    def calcWMC1(self):
        self.classObj.getSizeCategoryMetrics().setWMC1(len(self.classObj.get_methods()))

    # Count the number of methods and fields for each class in the project
    def calcSIZE2(self):
        self.classObj.getSizeCategoryMetrics().setSIZE2(len(self.classObj.get_methods())+len(self.classObj.get_fields()))