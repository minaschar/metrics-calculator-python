import ast
# from sys import orig_argv
from cohesion_category import CohesionCategory
from coupling_category import CouplingCategory
from qmood_category import QMOODCategory
from size_category import SizeCategory
from complexity_category import ComplexityCategory
from python_file import Python_File
from classDecl import *


class Init_Visitor(ast.NodeVisitor):

    def __init__(self, python_file):
        self.python_file = python_file
        self.currClass = None

    # Visit the node of the whole .py file
    def visit_Module(self, node):
        # We need for loop because in one .py file can be more than one classes
        for child in node.body:
            # We want to start analyzing only for classes and no for non oop code
            if (isinstance(child, ast.ClassDef)):
                self.visit_ClassDef(child)

    # Visit the node of a class
    def visit_ClassDef(self, node):
        # Create class instance
        classObj = Class(node.name, self.python_file, node, CohesionCategory(), ComplexityCategory(), CouplingCategory(), QMOODCategory(), SizeCategory())
        self.currClass = classObj
        self.python_file.addClass(classObj)
        for child in node.body:
            # We will visit the whole node of a method
            if (isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)
            else:
                # In else, we are outside of the methods, so we will visit this part
                AttrVisitor(classObj).visit(child)

    # Visit the node of a method in a class
    def visit_FunctionDef(self, node):
        self.currClass.add_method(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.generic_visit(node)

    # Visitor to get instance attributes and class attributes that declared in method's body!
    def visit_Attribute(self, node):
        if (isinstance(node.ctx, ast.Store)):
            # Instance attributes
            if (node.value.id == "self"):
                self.currClass.add_field("self." + node.attr)
            # Class attributes that declared inside a method
            elif (node.value.id == self.currClass.get_name()):
                self.currClass.add_field(self.currClass.get_name() + "." + node.attr)


class AttrVisitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj

    # Visitor to get ONLY class attributes that declared outside of methods!
    def visit_Name(self, node):
        if (isinstance(node.ctx, ast.Store)):
            self.classObj.add_field(self.classObj.get_name() + "." + node.id)


class LCOM_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.uses_in_method = {}  # A dictionary with key the function name and with value a list with the fields/attrs that the func
        self.fields = set()  # Keeps class and instance attributes for the current method

    def visit_ClassDef(self, node):
        for child in node.body:
            if (isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)
        return self.uses_in_method

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        self.uses_in_method[node.name] = self.fields.copy()
        self.fields.clear()  # Clear the set to can be used from the next method

    def visit_Attribute(self, node):
        # Instance attributes
        if (node.value.id == "self"):
            self.fields.add("self." + node.attr)
        # Class attributes that declared inside a method
        elif (node.value.id == self.classObj.get_name()):
            self.fields.add(self.classObj.get_name() + "." + node.attr)


class MPC_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.messages = 0

    def visit_ClassDef(self, node):
        for child in node.body:
            if (isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)

        return self.messages

    def visit_FunctionDef(self, node):

        for child in node.body:
            self.generic_visit(child)

    def visit_Call(self, node):

        if(isinstance(node.func, ast.Attribute) and node.func.value.id != "self"):
            self.messages = self.messages + 1


class CBO_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.elements = set()

    def visit_ClassDef(self, node):
        for child in node.body:
            if(isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)

        return self.elements

    def visit_FunctionDef(self, node):

        for child in node.body:
            self.generic_visit(child)

    def visit_Call(self, node):
        print("iusfed")

    def visit_Attribute(self, node):
        if(node.value.id != "self"):
            self.elements.add(node.value.id)
