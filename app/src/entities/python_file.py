
class Python_File:

    def __init__(self, project, file_name, file_path, generated_ast):
        self.project = project
        self.file_name = file_name
        self.file_path = file_path
        self.generated_ast = generated_ast
        self.classes = []

    def get_generated_ast(self):
        return self.generated_ast

    def get_path(self):
        return self.file_name

    def getProject(self):
        return self.project

    def addClass(self, className):
        self.classes.append(className)

    def getFileClasses(self):
        return self.classes