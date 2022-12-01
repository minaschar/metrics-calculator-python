import ast


class Hierarchy_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.parent_classes_list = []

    def visit_ClassDef(self, node):
        if (len(node.bases)):
            for superClass in node.bases:
                if (isinstance(superClass, ast.Name)):
                    self.parent_classes_list.append(superClass.id)
                # elif (isinstance(superClass, ast.Attribute)):
                #     self.parent_classes_list.append(superClass.attr)
            return self.parent_classes_list
        else:
            return []
