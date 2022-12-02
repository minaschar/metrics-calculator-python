import ast


class LOCNodeVisitor(ast.NodeVisitor):

    def __init__(self, class_obj):
        self.class_obj = class_obj
        self.lines_of_code = 0

    def visit_ClassDef(self, node):
        file_full_path = self.class_obj.get_python_file_obj().get_file_full_path()

        self.lines_of_code += (node.end_lineno - node.lineno + 1)
        self.lines_of_code -= self.remove_empty_lines(file_full_path, node.lineno, node.end_lineno)

        return self.lines_of_code

    def remove_empty_lines(self, file_full_path, class_start_line, class_last_line):
        line_count = 0
        empty_lines = 0

        with open(file_full_path, "r", encoding='utf-8') as file:
            try:
                lines = file.readlines()
                for line in lines:
                    line_count += 1
                    # This if will check if we are in the class block. We want to remove empty lines that exists in the current class block, not in the whole .py file
                    if (line_count >= class_start_line and line_count <= class_last_line):
                        if (len(line.strip()) == 0):
                            empty_lines += 1
            except ValueError as error:
                print(error)
            except:
                print("Can't read file")

        return empty_lines
