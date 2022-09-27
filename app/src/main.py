from metrics_calculator import MetricsCalculator
from project import Project
from generate_ast import ASTGenerator
from visitor import *

# put here a project path to test the code
# C:/Users/User/Desktop/UoM/Parsers/ProjectForTesting (path for Minas's testing)
test_root_folder_path = "C:/Users/John/Desktop/game-master-t"

test_project_name = "Game"
project = Project(test_root_folder_path, test_project_name)

ASTGenerator(project).start_parsing()

# Init existing classes for each .py file of the project
for python_file in project.get_files():
    visit_Class().visit_ClassDef(python_file.get_generated_ast(), python_file)

# Calculate Metrics for each class
for python_file in project.get_files():
    for classObj in python_file.getFileClasses():
        MetricsCalculator(classObj)

# # Testing - print Data
# for python_file in project.get_files():
#     for classObj in python_file.getFileClasses():
#         print(f"Class: {classObj.get_name()}")
#         for method in classObj.get_methods():
#             print(f"  Method: {method}")
#         for field in classObj.get_fields():
#             print(f"  Fields: {field}")

# # Testing - print Metrics
# print(f"Classes in Project: {MetricsCalculator.calcNOC(project.get_files())}")

for python_file in project.get_files():
     for classObj in python_file.getFileClasses():
          print(f"Class name: {classObj.getClassAstNode().name}")
          print(classObj.getSizeCategoryMetrics().getWMC1())
          print(classObj.getSizeCategoryMetrics().getNOM())
          print(classObj.getSizeCategoryMetrics().getSIZE2())
          print(classObj.getSizeCategoryMetrics().getWAC())



        
