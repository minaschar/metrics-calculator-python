import sys
from src.metrics.calculator.metrics_calculator import MetricsCalculator
from src.entities.project import Project
from src.generator.generate_ast import ASTGenerator
from src.visitors.visitor import *
from src.visitors.init_visitor import *
from gui.mainWindow import Ui_MainWindow
from PyQt5 import QtWidgets

# project path to test the code
# C:/Users/User/Desktop/UoM/Parsers/ProjectForTesting (path for Minas' testing)
# C:/Users/John/Desktop/game-master-t (path for Panos' testing)
# C:/Users/Money Maker/Documents/ProjectForTesting (path for Dionisis' testing)

test_root_folder_path = "C:/Users/User/Desktop/UoM/Parsers/ProjectForTesting"

test_project_name = "Game"
project = Project(test_root_folder_path, test_project_name)

ASTGenerator(project).start_parsing()

# Init existing classes for each .py file of the project
for python_file in project.get_files():
    Init_Visitor(python_file).visit_Module(python_file.get_generated_ast())

# Calculate Metrics for each class
for python_file in project.get_files():
    for classObj in python_file.getFileClasses():
        MetricsCalculator(classObj)

# # Testing - print Data
for python_file in project.get_files():
    for classObj in python_file.getFileClasses():
        print(f"Class: {classObj.get_name()}")
        for method in classObj.get_methods().keys():
            print(f"  Method: {method}")
        for field in classObj.get_fields():
            print(f"  Field: {field}")


# Testing - print Metrics
print(f"Classes in Project: {MetricsCalculator.calcNOC(project.get_files())}")

# for python_file in project.get_files():
#     for classObj in python_file.getFileClasses():
#         print(f"Class name: {classObj.getClassAstNode().name}")
#         print(f"WMPC2: {classObj.getComplexityCategoryMetrics().getWMPC2()}")
#         print(f"WMPC1: {classObj.getComplexityCategoryMetrics().getWMPC1()}")
#         print(f"NOM: {classObj.getSizeCategoryMetrics().getNOM()}")
#         print(f"MPC: {classObj.getCouplingCategoryMetrics().get_MPC()}")
#         print(f"SIZE2: {classObj.getSizeCategoryMetrics().getSIZE2()}")
#         print(f"WAC: {classObj.getSizeCategoryMetrics().getWAC()}")
#         print(f"LCOM: {classObj.getCohesionCategoryMetrics().get_LCOM()}")
#         print(f"RFC: {classObj.getComplexityCategoryMetrics().getRFC()}")
#         print(f"CBO: {classObj.getCouplingCategoryMetrics().get_CBO()}")
#         print(f"LOC: {classObj.getSizeCategoryMetrics().getLOC()}")
#         print(f"NOCC: {classObj.getSizeCategoryMetrics().getNOCC()}")
#         print(f"DIT: {classObj.getComplexityCategoryMetrics().getDIT()}")


import sys
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec_())
