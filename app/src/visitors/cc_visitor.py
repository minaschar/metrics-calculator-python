import ast


class CCNodeVisitor(ast.NodeVisitor):

    def __init__(self, class_obj):
        self.class_obj = class_obj
        # The value of cc will increased for every node that can change the program flow
        self.cc = 0

    def visit_ClassDef(self, node):
        for child in node.body:
            if(isinstance(child, ast.FunctionDef)):
                # Need to increase every time because we use the type nodes with condition + 1 for each function
                self.visit_FunctionDef(child)
        return self.cc

    def visit_FunctionDef(self, node):
        self.cc += 1
        self.generic_visit(node)

    # We dont need to check for else in loop because from there the program will execute sequentially each time after the completion of the loop
    def visit_For(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.cc += 1
        self.generic_visit(node)

    # We dont need to add else because in else we havent check
    def visit_If(self, node):
        self.cc += 1
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.cc += 1
        self.generic_visit(node)

    # For SetComp, DictComp and ListComp
    def visit_comprehension(self, node):
        self.cc += 1  # For the loop
        self.cc += len(node.ifs)  # For the conditions in the comprehension
        self.generic_visit(node)

    # For each match statement add the cases to the cc
    def visit_Match(self, node):
        self.cc += len(node.cases)
        self.generic_visit(node)
