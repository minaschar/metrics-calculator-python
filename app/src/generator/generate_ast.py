import ast
import os
from entities.project import Project
from entities.python_file import Python_File


class ASTGenerator:

    def __init__(self, project):
        self.project = project

    def start_parsing(self):
        self.readFolder()

    def readFolder(self):
        for root, dirs, files in os.walk(self.project.get_root_folder_path()):
            for file in files:  # Traverse all the directories
                if file.endswith(".py"):  # we want only .py files
                    full_file_path = os.path.join(root, file)
                    # fix the path format
                    full_file_path = full_file_path.replace("\\", "/")
                    # open text file in read mode
                    python_file = open(full_file_path, "r", encoding='UTF8')
                    data_from_python_file_str = python_file.read()  # read whole file to a string
                    python_file.close()
                    # This is not inside a try except since the Try except is moved inside the createAST method
                    self.createAST(data_from_python_file_str,
                                   file, full_file_path)

    def createAST(self, python_file_str, file, full_file_path):
        python_file = None
        try:
            tree = ast.parse(python_file_str, filename=file,
                             mode='exec', type_comments=False, feature_version=None)
            python_file = Python_File(self.project, file, full_file_path, tree)
        except SyntaxError:
            # Here we can first convert code from python 2.0 to python 3.0
            print("not parsed")
        if python_file != None:
            self.project.add_python_file(python_file)
