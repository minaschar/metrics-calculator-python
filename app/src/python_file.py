
class Python_File:

    file_name = ""
    generated_ast = None
    classes = []
    methods = []
    fields = []

    def __init__(self, file_name, generated_ast):
        self.file_name = file_name
        self.generated_ast = generated_ast

    def get_generated_ast(self):
        return self.generated_ast

    def get_path(self):
        return self.file_name

    def addClass(self, className):
        self.classes.append(className)

    def addMethod(self, methodName):
        self.methods.append(methodName)

    def addField(self, fieldName):
        self.fields.append(fieldName)
