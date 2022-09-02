from classDecl import Class
from size_category import SizeCategory


# In this class exists methods that calculates metrics for each class
class MetricsCalculator:

    classes = []

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMC1()
        self.calcNOM()
        # self.calcNOC()

    # Count the number of methods for each class in the project
    def calcNOM(self):
        self.classObj.getSizeCategoryMetrics().setNOM(len(self.classObj.get_methods()))

    # Need changes
    def calcWMC1(self):
        self.classObj.getSizeCategoryMetrics().setWMC1(len(self.classObj.get_methods()))

    @staticmethod
    def calcNOC(classes, sc):
        sc.setNOC(len(classes))
