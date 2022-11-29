import ast
from src.metrics.categories.cohesion_category import CohesionCategory
from src.metrics.categories.coupling_category import CouplingCategory
from src.metrics.categories.qmood_category import QMOODCategory
from src.metrics.categories.size_category import SizeCategory
from src.metrics.categories.complexity_category import ComplexityCategory
from src.entities.classDecl import Class
from src.visitors.class_attr_visitor import AttrVisitor


class Init_Visitor(ast.NodeVisitor):

    def __init__(self, python_file):
        self.python_file = python_file
        self.currClass = None

    # Visit the node of the whole .py file
    def visit_Module(self, node):
        # We need for loop because in one .py file can be more than one classes
        for child in ast.walk(node):
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
            # In else, we are outside of the methods, so we will visit this part
            elif (isinstance(child, ast.Assign)):
                AttrVisitor(classObj).generic_visit(child)

    # Visit the node of a method in a class
    def visit_FunctionDef(self, node):
        # Get method arguments
        arguments = [arg.arg for arg in node.args.args]
        self.currClass.add_method(node.name, arguments)
        # continue searching deeper in ast nodes
        self.generic_visit(node)

    # Visitor to get instance attributes and class attributes that declared in method's body!
    def visit_Attribute(self, node):
        if (isinstance(node.ctx, ast.Store)):
            if (isinstance(node.value, ast.Name)):
                # Instance attributes
                if (node.value.id == "self"):
                    self.currClass.add_field("self." + node.attr)
                # Class attributes that declared inside a method
                elif (node.value.id == self.currClass.get_name()):
                    self.currClass.add_field(self.currClass.get_name() + "." + node.attr)
