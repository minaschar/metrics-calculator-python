import ast
from cohesion_category import CohesionCategory
from coupling_category import CouplingCategory
from qmood_category import QMOODCategory
from size_category import SizeCategory
from complexity_category import ComplexityCategory
from python_file import Python_File
from classDecl import *


class visit_Class(ast.NodeVisitor):

    # Traverse the whole ast of the python file
    def visit_ClassDef(self, node: ast.AST, pythonFile: Python_File):
        for child in node.body:
            # We want only classes in python Files
            if (isinstance(child, ast.ClassDef)):
                # We found a class, so we create a Class object and we added it to the list of classes of the specific .py file
                classObj = Class(child.name, pythonFile, CohesionCategory(),
                                 ComplexityCategory(), CouplingCategory(), QMOODCategory(), SizeCategory())
                pythonFile.addClass(classObj)
                # For this class, we want to find it's methods, so we call the other visitor to traverse the method,
                # passing as argument the instance and the node of the current class to the constructor and to the visitor method respectively
                visit_FunctionDef(classObj).visit(child)
                # Here we call visitor to add class fields
                visit_FieldsInClass(classObj).visit(child)


class visit_FunctionDef(ast.NodeVisitor):

    def __init__(self, classObj: Class):
        self.classObj = classObj

    # With this visitor we will traverse the node of the body of the class
    def visit_ClassDef(self, node):
        for child in node.body:
            # We want only methods
            if isinstance(child, ast.FunctionDef):
                # Add method name to the list of methods of the current class we traverse
                self.classObj.add_method(child.name)


class visit_FieldsInClass(ast.NodeVisitor):

    def __init__(self, classObj: Class):
        self.classObj = classObj

    # With this visitor we traverse the currect class node to find:
    # 1. The constructor and then the fields that are declared into it for instance fields and
    # 2. assignments that are class fields and declared outside the constructor
    def visit_ClassDef(self, node):
        for child in node.body:
            if (isinstance(child, ast.FunctionDef)):
                # We want to visit only the constructor to take tha fields that declared there
                if (child.name == "__init__"):
                    for child in child.body:
                        if (isinstance(child, ast.Assign)):
                            if len(child.targets) == 1 and isinstance(child.targets[0], ast.Attribute):
                                self.classObj.add_field(
                                    str(child.targets[0].attr))
            elif (isinstance(child, ast.Assign)):
                # We add class fields that are declared outside the contructor
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
                    self.classObj.add_field(str(child.targets[0].id))

# class visitor_ForFieldsInFunction(ast.NodeVisitor):

#     def visit_ClassDef(self, node):
#         for child in node.body:
#             if isinstance(child, ast.FunctionDef):
#                 print('The name of fun:', child.name)
#                 self.visit_FunctionDef(child)

#     def visit_FunctionDef(self, node):
#         for child in node.body:
#             if isinstance(child, ast.Assign):
#                 if len(child.targets) == 1 and isinstance(child.targets[0], ast.Attribute):
#                     print(str(child.targets[0].attr))
#                 if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
#                     print(str(child.targets[0].id))
