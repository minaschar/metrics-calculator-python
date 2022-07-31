import ast
from pprint import pprint
from visitor import ClassOrder
from project import Project
from generate_ast import ASTGenerator
from visitor import Visitor

# put here a project path to test the code

test_root_folder_path = "C:/Users/John/Desktop/game-master-t/game-master"

test_project_name = "Game"

project = Project(test_root_folder_path, test_project_name)
ast_generator = ASTGenerator(project)
ast_generator.start_parsing()

# with open('') as f:
#     c = f.read()

# node = ast.parse(c)


# print(node.body[0].body[0]._fields)


# for python_file in project.get_files():
#     pprint(ast.dump(python_file.get_generated_ast(), indent=4))


# for python_file in project.get_files():
#     print(python_file.get_path())


for python_file in project.get_files():

    pprint("---------------")
    pprint(python_file.get_path())
    visitor = Visitor()
    visitor.visit(python_file.get_generated_ast())
