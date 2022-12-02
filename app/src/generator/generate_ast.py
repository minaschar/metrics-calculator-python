import ast
import os
from src.entities.python_file import PythonFile


class AstGenerator:

    def __init__(self, project_obj):
        self.project_obj = project_obj

    def start_parsing(self):
        self.read_root_project_folder()

    def read_root_project_folder(self):
        for root, dirs, files in os.walk(self.project_obj.get_root_folder_path()):
            for file in files:  # Traverse all the directories
                if file.endswith(".py"):  # we want only .py files
                    full_file_path = os.path.join(root, file)
                    # fix the path format
                    full_file_path = full_file_path.replace("\\", "/")
                    # open text file in read mode
                    python_file = open(full_file_path, "r", encoding='UTF8')
                    data_from_python_file_str = python_file.read()  # read whole file to a string
                    python_file.close()
                    self.create_ast(data_from_python_file_str, file, full_file_path)

    def create_ast(self, python_file_str, file, full_file_path):
        python_file_obj = None
        try:
            generated_ast_tree = ast.parse(python_file_str, filename=file, mode='exec', type_comments=False, feature_version=None)
            python_file_obj = PythonFile(self.project_obj, file, full_file_path, generated_ast_tree)
        except SyntaxError:
            # Here we can first convert code from python 2.0 to python 3.0
            print("not parsed")
        if python_file_obj != None:
            self.project_obj.add_python_file(python_file_obj)
