import ast


# Find the methods from other classes that are called from the methods body of the current class
class MethodsCalledNodeVisitor(ast.NodeVisitor):

    def __init__(self, class_obj):
        self.class_obj = class_obj
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
            method_name_called = node.attr
            instance_calling_name = node.value.id
            self.validate_remote_method(method_name_called, instance_calling_name)
        elif(isinstance(node.value, ast.Call)):
            if (isinstance(node.value.func, ast.Name)):
                method_name_called = node.attr
                instance_calling_name = node.value.func.id
                self.validate_remote_method(method_name_called, instance_calling_name)
        else:
            self.generic_visit(node)

    # Insure that the method that is called, exists in other class in the project
    def validate_remote_method(self, method_name_called, instance_calling_name):
        if (instance_calling_name != "self" and instance_calling_name != self.class_obj.get_class_name()):
            for python_file_obj in self.class_obj.get_python_file_obj().get_project_obj().get_files():
                for class_obj in python_file_obj.get_file_classes():
                    if (method_name_called and method_name_called in class_obj.get_methods().keys()):
                        self.called.append(instance_calling_name + "." + method_name_called)
                        break
