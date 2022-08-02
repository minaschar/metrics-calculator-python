import ast
from dbm import dumb
from pprint import pprint


class Visitor(ast.NodeVisitor):

    classNames = []

    # Visiting all nodes

    # def visit(self, node: ast.AST):

    # Visiting all nodes
    # def visit(self,node: ast.AST):

    #     print(node)
    #     self.generic_visit(node)

    # Visiting all Class Definitions

    def visit_ClassDef(self, node: ast.AST):

        # add to classNames the names of the classes
        self.classNames.append(node.name)

        self.generic_visit(node)

        print(len(self.classNames))  # visualization of the number of classes


class visit_FunctionDef(ast.NodeVisitor):

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                print(child.name)


class visitor_ForFields(ast.NodeVisitor):

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, ast.Assign):
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
                    print(str(child.targets[0].id))


class visitor_ForFieldsInFunction(ast.NodeVisitor):

    def visit_ClassDef(self, node):
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                print('The name of fun:', child.name)
                self.visit_FunctionDef(child)

    def visit_FunctionDef(self, node):
        for child in node.body:
            if isinstance(child, ast.Assign):
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Attribute):
                    print(str(child.targets[0].attr))
                if len(child.targets) == 1 and isinstance(child.targets[0], ast.Name):
                    print(str(child.targets[0].id))
