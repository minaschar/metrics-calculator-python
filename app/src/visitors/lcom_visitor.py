import ast


class LCOMNodeVisitor(ast.NodeVisitor):

    def __init__(self, class_obj):
        self.class_obj = class_obj
        self.uses_in_method = dict()  # A dictionary with key the function name and with value a list with the fields/attrs in that function
        self.fields = set()  # Keeps class and instance attributes for the current method

    def visit_ClassDef(self, node):
        for child in node.body:
            if (isinstance(child, ast.FunctionDef)):
                self.visit_FunctionDef(child)
        return self.uses_in_method

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        # In the key node.name we add a copy of the list that keeps the fields for the current method.
        # We add a copy because we will clear after the list that keep the fields
        self.uses_in_method[node.name] = self.fields.copy()
        self.fields.clear()  # Clear the set to can be used from the next method

    def visit_Attribute(self, node):
        if (isinstance(node.value, ast.Name)):
            attr = node.value.id + "." + node.attr
            # Check if the attribute we fould belongs in the class we analyze. For LCOM we want only attributes of that class
            if (attr in self.class_obj.get_fields()):
                self.fields.add(attr)
