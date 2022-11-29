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


class CC_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.cc = 0

    def visit_ClassDef(self, node):
        for child in node.body:
            if(isinstance(child, ast.FunctionDef)):
                # Need to increase every time because we use the type nodes with condition + 1 for each function
                self.visit_FunctionDef(child)
        return self.cc

    def visit_FunctionDef(self, node):
        self.cc += 1
        self.generic_visit(node)

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
        file_fullpath = self.classObj.getPyFileObj().get_fullpath()

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
