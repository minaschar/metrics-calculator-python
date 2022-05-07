import ast
import os
from pprint import pprint

all_trees = []
all_parsed_files = []
root_folder_path = "C:/Users/User/Desktop/UoM/Parsers/game-master" #root folder path for testing

for root, dirs, files in os.walk(root_folder_path):
    for file in files: #Traverse all the directories
        if file.endswith(".py"): #we want only .py files
            full_file_path = os.path.join(root, file)
            full_file_path = full_file_path.replace("\\", "/")
            python_file = open(full_file_path, "r", encoding='UTF8') #open text file in read mode
            data_from_python_file_str = python_file.read() #read whole file to a string
            python_file.close()
            #If the program cannot be compiled then an error occurs in the console and parsing stops
            try: 
                tree = ast.parse(data_from_python_file_str, filename=file, mode='exec', type_comments=False, feature_version=None)
                #tree = compile(data_from_python_file_str, filename=file, mode="exec", flags=ast.PyCF_ONLY_AST, dont_inherit=False, optimize=- 1) #Alternative
                all_trees.append(tree)
            except SyntaxError: 
                all_trees.append(tree) #Here we can first convert code from python 2.0 to python 3.0
            all_parsed_files.append(file) #to know for which file the ast is for

#Just for testing
pprint(ast.dump(all_trees[4], indent=4))
print(all_parsed_files[4])
