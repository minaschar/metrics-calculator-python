import ast

class Visitor(ast.NodeVisitor):

    #Visiting all nodes
    # def visit(self,node: ast.AST):
    #     print(node)
    #     self.generic_visit(node)

    #Visiting all Class Definitions
    def visit_ClassDef(self, node: ast.AST):
        print(node)
        self.generic_visit(node)