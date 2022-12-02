
class PythonFile:

    def __init__(self, project_obj, file_name, file_full_path, generated_ast):
        self.project_obj = project_obj
        self.file_name = file_name
        self.file_full_path = file_full_path
        self.generated_ast = generated_ast
        self.classes = list()

    def get_project_obj(self):
        return self.project_obj

    def get_path(self):
        return self.file_name

    def get_file_full_path(self):
        return self.file_full_path

    def get_generated_ast(self):
        return self.generated_ast

    def get_file_classes(self):
        return self.classes

    def add_class(self, class_obj):
        self.classes.append(class_obj)
