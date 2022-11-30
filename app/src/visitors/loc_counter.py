import ast


class LOC_Visitor(ast.NodeVisitor):

    def __init__(self, classObj):
        self.classObj = classObj
        self.loc = 0

    def visit_ClassDef(self, node):
        file_fullpath = self.classObj.getPyFileObj().get_fullpath()

        self.loc += (node.end_lineno - node.lineno + 1)
        self.loc -= self.removeEmptyLines(file_fullpath, node.lineno, node.end_lineno)

        return self.loc

    def removeEmptyLines(self, file, classStart, classEnd):
        lineCount = 0
        emptyLines = 0

        with open(file) as file:
            lines = file.readlines()
            for line in lines:
                lineCount += 1
                if (lineCount >= classStart and lineCount <= classEnd):
                    if (len(line.strip()) == 0):
                        emptyLines += 1

        return emptyLines
