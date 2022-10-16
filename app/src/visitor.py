import ast
from sys import orig_argv
from cohesion_category import CohesionCategory
from coupling_category import CouplingCategory
from qmood_category import QMOODCategory
from size_category import SizeCategory
from complexity_category import ComplexityCategory
from python_file import Python_File
from classDecl import *


class Init_Visitor(ast.NodeVisitor):

    # Visit the node of the whole .py file
    def visit_Module(self, node):
        # We need for loop because in one .py file can be more than one classes
        for child in node.body:
            # We want to start analyzing only for classes and no for non oop code
            if (isinstance(child, ast.ClassDef)):
                self.visit_ClassDef(child)

    # Visit the node of a class
    def visit_ClassDef(self, node):
        print(node.name)
        self.generic_visit(node)

    # Visit the node of a method in a class
    def visit_FunctionDef(self, node):
        print(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.generic_visit(node)

    # Visitor to get ONLY instance attributes!
    def visit_Attribute(self, node):
        if (node.value.id == "self"):
            print(node.attr)

    # Visitor to get ONLY class attributes!
    def visit_Name(self, node):
        if (isinstance(node.ctx, ast.Store)):
            print(node.id)


class visit_Class(ast.NodeVisitor):

    # Traverse the whole ast of the python file
    def visit_ClassDef(self, node: ast.AST, pythonFile: Python_File):
        for child in node.body:
            # We want only classes in python Files
            if (isinstance(child, ast.ClassDef)):
                # We found a class, so we create a Class object and we added it to the list of classes of the specific .py file
                classObj = Class(child.name, pythonFile, child, CohesionCategory(),
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
                # We want to visit only the constructor to take tha fields that declared there (instance fields)
                if (child.name == "__init__"):
                    for child in child.body:
                        if (isinstance(child, ast.Assign)):
                            if len(child.targets) == 1 and isinstance(child.targets[0], ast.Attribute):
                                self.classObj.add_field(
                                    str(child.targets[0].attr))
            elif (isinstance(child, ast.Assign)):
                # We add class fields that are declared outside the contructor (class fields)
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
                    self.classObj.add_field(str(child.targets[0].id))


class visit_methodsForLCOM(ast.NodeVisitor):

    def __init__(self, classObj: Class):
        # A dictionary with key the function name and with value a list with the fields/attrs that the function uses
        self.uses_in_method = {}
        self.classObj = classObj

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_FunctionDef(child)
        # return the dictionary after walk to all class node
        return self.uses_in_method

    def visit_FunctionDef(self, node):
        values = []
        for child in node.body:
            exp = ""
            if isinstance(child, ast.Assign):
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Attribute):
                    exp = str(child.targets[0].attr)
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
                    exp = str(child.targets[0].id)
            elif (isinstance(child, ast.AugAssign)):
                if isinstance(child.target, ast.Attribute):
                    exp = str(child.target.attr)
                if isinstance(child.target, ast.Name):
                    exp = str(child.target.id)
            elif (isinstance(child, ast.Expr)):
                for i in range(0, len(child.value.args), 1):
                    if (isinstance(child.value.args[i], ast.BinOp)):
                        exp = child.value.args[i].right.attr
                    elif (isinstance(child.value.args[i], ast.Attribute)):
                        exp = child.value.args[i].attr

            if (exp != "" and exp in self.classObj.get_fields()):
                values.append(exp)

        self.uses_in_method[node.name] = values
