
class Project:

    root_folder_path = ''  # The path that the project is in the local storage
    project_name = ''
    python_files = []

    def __init__(self, root_folder_path, project_name):
        self.root_folder_path = root_folder_path
        self.project_name = project_name

    def get_root_folder_path(self):
        return self.root_folder_path

    def get_name(self):
        return self.project_name

    def add_python_files(self, python_file_obj):
        self.python_files.append(python_file_obj)

    def get_files(self):
        return self.python_files
