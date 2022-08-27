
class Python_File:

    file_name = ""
    file_path = ""
    generated_ast = None
    classes = []

    def __init__(self, file_name, generated_ast):
        self.file_name = file_name
        self.generated_ast = generated_ast

    def get_generated_ast(self):
        return self.generated_ast

    def get_path(self):
        return self.file_name

    def addClass(self, className):
        self.classes.append(className)

    def getFileClasses(self):
        return self.classes
