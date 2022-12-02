
class PythonFile:

    def __init__(self, project_obj, file_name, file_full_path, generated_ast):
        # The whole projects object that we scan
        self.project_obj = project_obj
        # The name of the specific .py file
        self.file_name = file_name
        # The full path of this .py file
        self.file_full_path = file_full_path
        # An ast node of the whole .py module
        self.generated_ast = generated_ast
        # A list tith all classes that exist in the specific .py file/module. We need it to can access all the classes of the scaned project
        self.classes = list()

    def get_project_obj(self):
        return self.project_obj

    def get_file_name(self):
        return self.file_name

    def get_file_full_path(self):
        return self.file_full_path

    def get_generated_ast(self):
        return self.generated_ast

    def get_file_classes(self):
        return self.classes

    def add_class(self, class_obj):
        self.classes.append(class_obj)
