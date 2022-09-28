from os import listdir
from os.path import isfile, join
from classDecl import Class


# In this class exists methods that calculates metrics for the whole project
class MetricsCalculator:

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMC1()
        self.calcNOM()
        self.calcSIZE2()
        self.calcWAC()
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

    def calcLOC(self):
        # project path to test the code
        # C:/Users/User/Desktop/UoM/Parsers/ProjectForTesting (path for Minas' testing)
        # C:/Users/John/Desktop/game-master-t (path for Panos' testing)
        # C:/Users/Money Maker/Documents/ProjectForTesting (path for Dionisis' testing)
        return self.countIn("C:/Users/Money Maker/Documents/ProjectForTesting")

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
