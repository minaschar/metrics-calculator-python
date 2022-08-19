

class Class:

    name = ""
    methods = []
    python_file = ""
    fields = []

    def __init__(self, className, classMethods, p_file, classFields):
        self.name = className
        self.methods = classMethods
        self.python_file = p_file
        self.fields = classFields

    def get_name(self):
        return self.name

    def get_methods(self):
        return self.methods

    def get_fields(self):
        return self.fields

    def add_method(self, method):
        self.methods.append(method)

    def add_field(self, field):
        self.fields.append(field)
