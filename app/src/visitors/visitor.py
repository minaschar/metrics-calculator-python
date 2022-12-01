import ast


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
