import ast


class Visitor(ast.NodeVisitor):

    # Visiting all nodes
    # def visit(self,node: ast.AST):
    #     print(node)
    #     self.generic_visit(node)

    # Visiting all Class Definitions
    def visit_ClassDef(self, node: ast.AST):
        print(node)
        self.generic_visit(node)


class ClassOrder(ast.NodeVisitor):
    
    identifiers = None

    def visit_ClassDef(self, node):
        self.identifiers = []
        for child in node.body:
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    self.visit(target)
            elif isinstance(child, ast.FunctionDef):
                self.identifiers.append(child.name)

    def visit_Name(self, node):
        if self.identifiers is not None:
            self.identifiers.append(node.id)