
class Project:

    def __init__(self, root_folder_path, project_name):
        # The path of the project in the local storage
        self.root_folder_path = root_folder_path
        # The name of the scaned project
        self.project_name = project_name
        # A list with all the python files that exists in the root folder. We need it, so we can access all the .py files and the classes in them
        self.python_files = list()

    def get_root_folder_path(self):
        return self.root_folder_path

    def get_project_name(self):
        return self.project_name

    def add_python_file(self, python_file_obj):
        self.python_files.append(python_file_obj)

    def get_files(self):
        return self.python_files
