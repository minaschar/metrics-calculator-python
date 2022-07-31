import ast


class Visitor(ast.NodeVisitor):

    classNames = []

    # Visiting all nodes

    # def visit(self, node: ast.AST):

    #     print(node)
    #     self.generic_visit(node)

    # Visiting all Class Definitions

    def visit_ClassDef(self, node: ast.AST):

        print(node)
        # add to classNames the names of the classes
        self.classNames.append(node.name)

        self.generic_visit(node)

        print(len(self.classNames))  # visualization of the number of classes
