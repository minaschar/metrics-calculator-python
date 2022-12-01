from src.visitors.methods_called_outside_visitor import CBO_Visitor
from src.visitors.remote_methods_called_visitor import MethodsCalled_Visitor
from src.visitors.loc_counter import LOC_Visitor
from src.visitors.cc_visitor import CC_Visitor
from src.visitors.lcom_visitor import LCOM_Visitor
from src.visitors.hierarchy_visitor import Hierarchy_Visitor
from src.entities.classDecl import Class


# In this class exists methods that calculates metrics for the whole project
class MetricsCalculator:

    def __init__(self, classObj: Class):
        self.classObj = classObj
        self.calcWMPC2()
        self.calcWMPC1()
        self.calcNOM()
        self.calcSIZE2()
        self.calcWAC()
        self.calcMPC()
        self.calcLCOM()
        self.calcLOC()
        self.calcRFC()
        self.calcNOCC()
        self.calcDIT(classObj)
        self.calcCBO()

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
    def calcWMPC2(self):
        nop = 0

        # In args_size we have the count of parameters for each function in a class
        args_size = [len(args) for args in self.classObj.get_methods().values()]

        # We count all parameters in the class
        for size in args_size:
            nop += size

        self.classObj.getComplexityCategoryMetrics().setWMPC2(len(self.classObj.get_methods()) + nop)

    # Count the number of methods and fields for each class in the project
    def calcSIZE2(self):
        self.classObj.getSizeCategoryMetrics().setSIZE2(len(self.classObj.get_methods()) + len(self.classObj.get_fields()))

    # Count the number of fields for each class
    def calcWAC(self):
        self.classObj.getSizeCategoryMetrics().setWAC(len(self.classObj.get_fields()))

    # Calculate LCOM Metric
    def calcLCOM(self):
        cohesive = 0
        non_cohesive = 0

        uses_in_methods = LCOM_Visitor(self.classObj).visit(self.classObj.getClassAstNode())

        for i in range(0, len(uses_in_methods), 1):
            for j in range(i + 1, len(uses_in_methods), 1):
                if (len(list(set(list(uses_in_methods.values())[i]).intersection(list(uses_in_methods.values())[j])))) == 0:
                    non_cohesive += 1
                else:
                    cohesive += 1

        if (non_cohesive - cohesive < 0):
            self.classObj.getCohesionCategoryMetrics().set_LCOM(0)
        else:
            self.classObj.getCohesionCategoryMetrics().set_LCOM(non_cohesive - cohesive)

    # Calculate RFC Metric
    def calcRFC(self):
        # We convert to set because we want to remove common method calls. We sum the methods, not the calls
        remoteMethodsSum = len(set(MethodsCalled_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode())))
        self.classObj.getComplexityCategoryMetrics().setRFC(self.classObj.getSizeCategoryMetrics().getNOM() + remoteMethodsSum)

    # Calculate NOCC Metric
    def calcNOCC(self):

        myClassChildrenClasses = len(self.returnChildren(self.classObj))
        self.classObj.getSizeCategoryMetrics().setNOCC(myClassChildrenClasses)

    # Calculate DIT Metric
    def calcDIT(self, aParentClassObject):
        self.currDitClass = aParentClassObject
        # Class is not in any hierarchy
        if ((Hierarchy_Visitor(self.currDitClass).visit_ClassDef(self.currDitClass.getClassAstNode()) == []) and (len(self.returnChildren(self.currDitClass)) == 0)):
            self.currDitClass.getComplexityCategoryMetrics().setDIT(0)
            self.currDitClass.set_hierarchy(0)
        elif ((Hierarchy_Visitor(self.currDitClass).visit_ClassDef(self.currDitClass.getClassAstNode()) == []) and (len(self.returnChildren(self.currDitClass)) != 0)):
            self.currDitClass.getComplexityCategoryMetrics().setDIT(1)
            self.currDitClass.set_hierarchy(1)
        else:
            myParentClassesNamesOnly = Hierarchy_Visitor(self.currDitClass).visit_ClassDef(self.currDitClass.getClassAstNode())

            # Converting simple name pointers to actually object classes
            myParentClassesObjects = self.convertToActualParentObjects(self.currDitClass, myParentClassesNamesOnly)
            maxParentDepth = self.returnMaxParentDepth(myParentClassesObjects)
            self.currDitClass.getComplexityCategoryMetrics().setDIT(maxParentDepth + 1)
            self.currDitClass.set_hierarchy(maxParentDepth + 1)

    # Calculate LOC Metric
    def calcLOC(self):
        self.classObj.getSizeCategoryMetrics().setLOC(LOC_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode()))

    # Calculate MPC Metric
    def calcMPC(self):
        # We sum all the calls
        messages = len(MethodsCalled_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode()))

        self.classObj.getCouplingCategoryMetrics().set_MPC(messages)

    # Calculate CBO Metric
    def calcCBO(self):
        # We store all the methods that called, and belongs to other classes. Methods from libraries are not included
        methods_that_called = MethodsCalled_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode())
        # We store all the class name or instance names that used to call methods from other classes in the project. Classes and methods from libraries are not included
        class_uses = set()
        for method in methods_that_called:
            part1 = method.split(".", 2)
            class_uses.add(part1[0])

        self.classObj.getCouplingCategoryMetrics().set_CBO(len(class_uses) +
                                                           len(Hierarchy_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode())) +
                                                           self.classObj.getSizeCategoryMetrics().getNOCC())

    def calcWMPC1(self):
        class_nom = len(self.classObj.get_methods())
        if (class_nom > 0):
            class_cc = CC_Visitor(self.classObj).visit_ClassDef(self.classObj.getClassAstNode())
            self.classObj.getComplexityCategoryMetrics().setWMPC1(round(class_cc / class_nom, 2))
        else:
            self.classObj.getComplexityCategoryMetrics().setWMPC1(0.0)


##################### Methods necessary for NOCC and DIT calculation #####################


    def returnChildren(self, classInQuestion):
        allParentClasses = []
        myClassChildrenClasses = 0
        myClassChildrenClassesList = []
        for pythonFile in classInQuestion.getPyFileObj().getProject().get_files():
            for classObj in pythonFile.getFileClasses():
                allParentClasses = allParentClasses + Hierarchy_Visitor(classObj).visit_ClassDef(classObj.getClassAstNode())
        for myClass in allParentClasses:
            if (myClass == classInQuestion.name):
                myClassChildrenClasses = myClassChildrenClasses + 1
                myClassChildrenClassesList.append(myClass)
        return myClassChildrenClassesList

    def convertToActualParentObjects(self, classInQuestion, myParentClassesNamesOnly):
        myParentClassesObjects = []
        for pythonFile in classInQuestion.getPyFileObj().getProject().get_files():
            for classObj in pythonFile.getFileClasses():
                for classNameOnly in myParentClassesNamesOnly:
                    if (classObj.name == classNameOnly):
                        myParentClassesObjects.append(classObj)
        return myParentClassesObjects

    def returnMaxParentDepth(self, myParentClassesObjects):
        maxParentDIT = -2
        for aParentClassObject in myParentClassesObjects:
            if (aParentClassObject.get_hierarchy() == -1):
                self.calcDIT(aParentClassObject)
            else:
                if (aParentClassObject.get_hierarchy() > maxParentDIT):
                    maxParentDIT = aParentClassObject.get_hierarchy()
        return maxParentDIT
