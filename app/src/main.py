from metrics_calculator import MetricsCalculator
from project import Project
from generate_ast import ASTGenerator
from visitor import *

# project path to test the code
# C:/Users/User/Desktop/UoM/Parsers/ProjectForTesting (path for Minas' testing)
# C:/Users/John/Desktop/game-master-t (path for Panos' testing)
# C:/Users/Money Maker/Documents/ProjectForTesting (path for Dionisis' testing)
test_root_folder_path = "C:/Users/Money Maker/Documents/ProjectForTesting"

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
        for method in classObj.get_methods():
            print(f"  Method: {method}")
        for field in classObj.get_fields():
            print(f"  Field: {field}")

# Testing - print Metrics
print(f"Classes in Project: {MetricsCalculator.calcNOC(project.get_files())}")

for python_file in project.get_files():
    for classObj in python_file.getFileClasses():
        print(f"Class name: {classObj.getClassAstNode().name}")
        print(f"WMPC2: {classObj.getComplexityCategoryMetrics().getWMPC2()}")
        print(f"NOM: {classObj.getSizeCategoryMetrics().getNOM()}")
        print(f"SIZE2: {classObj.getSizeCategoryMetrics().getSIZE2()}")
        print(f"WAC: {classObj.getSizeCategoryMetrics().getWAC()}")
        print(f"LCOM: {classObj.getCohesionCategoryMetrics().get_LCOM()}")
        print(f"RFC: {classObj.getComplexityCategoryMetrics().getRFC()}")
        print(f"LOC: {classObj.getSizeCategoryMetrics().getLOC()}")
        print(f"NOCC: {classObj.getSizeCategoryMetrics().getNOCC()}")
