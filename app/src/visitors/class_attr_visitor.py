import ast


class AttrVisitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj

    # Visitor to get ONLY class attributes that declared outside of methods!
    def visit_Name(self, node):
        if (isinstance(node.ctx, ast.Store)):
            self.classObj.add_field(self.classObj.get_name() + "." + node.id)
