import ast


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
