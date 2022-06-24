
class Python_File:

    file_name = ""
    generated_ast = None

    def __init__(self, file_name, generated_ast):
        self.file_name = file_name
        self.generated_ast = generated_ast

    def get_generated_ast(self):
        return self.generated_ast

    def get_path(self):
        return self.file_name
