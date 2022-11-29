import ast
# from sys import orig_argv
from src.metrics.categories.cohesion_category import CohesionCategory
from src.metrics.categories.coupling_category import CouplingCategory
from src.metrics.categories.qmood_category import QMOODCategory
from src.metrics.categories.size_category import SizeCategory
from src.metrics.categories.complexity_category import ComplexityCategory
from src.entities.python_file import Python_File
from src.entities.classDecl import Class


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
            elif (isinstance(child, ast.ClassDef)):
                self.visit_ClassDef(child)
            else:
                # In else, we are outside of the methods, so we will visit this part
                AttrVisitor(classObj).visit(child)

    # Visit the node of a method in a class
    def visit_FunctionDef(self, node):
        # Get method arguments
        arguments = [arg.arg for arg in node.args.args]
        self.currClass.add_method(node.name, arguments)
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
        if (isinstance(node.value, ast.Name)):
            self.fields.add(node.value.id + "." + node.attr)
        elif(isinstance(node.value, ast.Call)):
            self.fields.add(node.value.func.id + "." + node.attr)


class MethodsCalled_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.called = set()

    def visit_ClassDef(self, node):
        for child in ast.walk(node):
            if (isinstance(child, ast.Call)):
                self.visit_Call(child)
        return self.called

    def visit_Call(self, node):
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if (isinstance(node.value, ast.Name)):
            methodCalled = node.value.id + "." + node.attr
            for pythonFile in self.classObj.getPyFileObj().getProject().get_files():
                for classObj in pythonFile.getFileClasses():
                    if (methodCalled and node.attr in classObj.get_methods().keys()):
                        self.called.add(methodCalled)
        else:
            self.generic_visit(node)


class Hierarchy_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.parent_classes = 0
        self.parent_classes_list = []

    def visit_ClassDef(self, node):
        if (len(node.bases)):
            for superClass in node.bases:
                self.parent_classes_list.append(superClass.id)
            return self.parent_classes_list
        else:
            return []


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

        for child in ast.walk(node):
            if (isinstance(child, ast.Call)):
                self.visit_Call(child)

    def visit_Call(self, node):
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if (isinstance(node.value, ast.Name)):
            if (node.value.id != "self"):
                self.messages += 1
        else:
            self.generic_visit(node)


class CBO_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.elements = {}

    def visit_ClassDef(self, node):
        for child in node.body:
            if(isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)

        return self.elements

    def visit_FunctionDef(self, node):
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if (isinstance(node.value, ast.Name)):
            if(node.value.id != "self"):
                self.elements[node.value.id] = node.attr


class CC_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.cc = 0

    def visit_ClassDef(self, node):
        for child in node.body:
            if(isinstance(child, ast.FunctionDef)):
                # Need to increase every time because we use the type nodes with condition + 1 for each function
                self.cc += 1
                self.generic_visit(child)
        return self.cc

    # We dont need to check for else in loop because from there the program will execute sequentially each time after the completion of the loop
    def visit_For(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.cc += 1
        self.generic_visit(node)

    # We dont need to add else because in else we havent check
    def visit_If(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.cc += 1
        self.generic_visit(node)

    # For SetComp, DictComp and ListComp
    def visit_comprehension(self, node):
        self.cc += 1  # For the loop
        self.cc += len(node.ifs)  # For the conditions in the comprehension
        self.generic_visit(node)

    # For each match statement add the cases to the cc
    def visit_Match(self, node):
        self.cc += len(node.cases)
        self.generic_visit(node)


class LOC_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.loc = 0

    def visit_ClassDef(self, node):
        file_fullpath = self.classObj.getPyFileObj().getProject().get_root_folder_path() + "/" + self.classObj.getPyFileObj().get_path()

        self.loc += (node.end_lineno - node.lineno + 1)
        self.loc -= self.removeEmptyLines(file_fullpath, node.lineno, node.end_lineno)

        return self.loc

    def removeEmptyLines(self, file, classStart, classEnd):
        lineCount = 0
        emptyLines = 0

        with open(file) as file:
            lines = file.readlines()
            for line in lines:
                lineCount += 1
                if (lineCount >= classStart and lineCount <= classEnd):
                    if (len(line.strip()) == 0):
                        emptyLines += 1

        return emptyLines
