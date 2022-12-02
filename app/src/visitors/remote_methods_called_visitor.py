import ast


# Find the methods from other classes that are called from the methods body of the current class
class MethodsCalled_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.called = list()

    def visit_ClassDef(self, node):
        for child in node.body:
            if (isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)
        return self.called

    def visit_FunctionDef(self, node):
        for child in ast.walk(node):
            if (isinstance(child, ast.Call)):
                self.visit_Call(child)

    def visit_Call(self, node):
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if (isinstance(node.value, ast.Name)):
            methodNameCalled = node.attr
            instanceCallingName = node.value.id
            self.validateRemoteMethod(methodNameCalled, instanceCallingName)
        elif(isinstance(node.value, ast.Call)):
            if (isinstance(node.value.func, ast.Name)):
                methodNameCalled = node.attr
                instanceCallingName = node.value.func.id
                self.validateRemoteMethod(methodNameCalled, instanceCallingName)
        else:
            self.generic_visit(node)

    def validateRemoteMethod(self, methodNameCalled, instanceCallingName):
        if (instanceCallingName != "self" and instanceCallingName != self.classObj.get_name()):
            for pythonFile in self.classObj.getPyFileObj().getProject().get_files():
                for classObj in pythonFile.getFileClasses():
                    if (methodNameCalled and methodNameCalled in classObj.get_methods().keys()):
                        self.called.append(instanceCallingName + "." + methodNameCalled)
                        break
