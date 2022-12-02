import ast


class HierarchyNodeVisitor(ast.NodeVisitor):

    def __init__(self, class_obj):
        self.class_obj = class_obj
        self.parent_classes_list = list()

    def visit_ClassDef(self, node):
        if (len(node.bases)):
            for super_class in node.bases:
                if (isinstance(super_class, ast.Name)):
                    self.parent_classes_list.append(super_class.id)
                # to can cover the case of set parent like this: packageName.ClassName (like ast.NodeVisitor)
                # elif (isinstance(superClass, ast.Attribute)):
                #     self.parent_classes_list.append(superClass.attr)
            return self.parent_classes_list
        else:
            return []
