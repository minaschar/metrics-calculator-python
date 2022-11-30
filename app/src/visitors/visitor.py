import ast


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
        self.parent_classes_list = []

    def visit_ClassDef(self, node):
        if (len(node.bases)):
            for superClass in node.bases:
                if (isinstance(superClass, ast.Name)):
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
