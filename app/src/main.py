from pprint import pprint
from project import Project
from generate_ast import ASTGenerator
from visitor import *

# put here a project path to test the code
test_root_folder_path = "C:/Users/User/Desktop/UoM/Parsers/game-master"

test_project_name = "Game"
project = Project(test_root_folder_path, test_project_name)

ast_generator = ASTGenerator(project)
ast_generator.start_parsing()

# Count classes in each module
for python_file in project.get_files():

    pprint("---------------")
    pprint(python_file.get_path())
    visitor = Visitor()
    visitor.visit(python_file.get_generated_ast())

# get methods for each class
for python_file in project.get_files():
    print(python_file.file_name + "::: methods")
    visit_FunctionDef().visit(python_file.get_generated_ast())

# get fields for each class
for python_file in project.get_files():
    print(python_file.file_name + "::: field")
    visitor_ForFields().visit(python_file.get_generated_ast())

for python_file in project.get_files():
    print(python_file.file_name + "::: field in function")
    visitor_ForFieldsInFunction().visit(python_file.get_generated_ast())
