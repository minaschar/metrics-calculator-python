from os import listdir
from os.path import isfile, join
from classDecl import Class
from visitor import visit_methodsForLCOM


# In this class exists methods that calculates metrics for the whole project
class MetricsCalculator:

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMC1()
        self.calcNOM()
        self.calcSIZE2()
        self.calcWAC()
        self.calcLCOM()
        # Testing that that the LOC counter works
        print(self.calcLOC())

    # Count the Classes that exists in the whole project.
    # The method will called only once time when we want to print the results
    @staticmethod
    def calcNOC(files):
        noc = 0
        for python_file in files:
            noc += len(python_file.getFileClasses())

        return noc

    # Count the number of methods for each class in the project
    def calcNOM(self):
        self.classObj.getSizeCategoryMetrics().setNOM(len(self.classObj.get_methods()))

    # Count the number of methods for each class in the project
    def calcWMC1(self):
        self.classObj.getSizeCategoryMetrics().setWMC1(len(self.classObj.get_methods()))

    # Count the number of methods and fields for each class in the project
    def calcSIZE2(self):
        self.classObj.getSizeCategoryMetrics().setSIZE2(
            len(self.classObj.get_methods()) + len(self.classObj.get_fields()))

    # Count the number of fields for each class
    def calcWAC(self):
        self.classObj.getSizeCategoryMetrics().setWAC(len(self.classObj.get_fields()))

    # Calculate LCOM Metric
    def calcLCOM(self):
        cohesive = 0
        non_cohesive = 0

        uses_in_methods = visit_methodsForLCOM(
            self.classObj).visit(self.classObj.getClassAstNode())

        for i in range(0, len(uses_in_methods), 1):
            for j in range(i + 1, len(uses_in_methods), 1):
                if (len(list(set(list(uses_in_methods.values())[i]).intersection(
                        list(uses_in_methods.values())[j])))) == 0:
                    non_cohesive += 1
                else:
                    cohesive += 1

        if (non_cohesive - cohesive < 0):
            self.classObj.getCohesionCategoryMetrics().set_LCOM(0)
        else:
            self.classObj.getCohesionCategoryMetrics().set_LCOM(non_cohesive - cohesive)

    def calcLOC(self):
        return self.countIn(self.classObj.getPyFileObj().getProject().get_root_folder_path())

##################### Methods necessary for LOC calculation #####################
    def countLinesInPath(self, path, directory):
        count = 0
        for line in open(join(directory, path), encoding="utf8"):
            count += 1
        return count

    def countLines(self, paths, directory):
        count = 0
        for path in paths:
            count = count + self.countLinesInPath(path, directory)
        return count

    def getPaths(self, directory):
        return [f for f in listdir(directory) if isfile(join(directory, f))]

    def countIn(self, directory):
        return self.countLines(self.getPaths(directory), directory)
