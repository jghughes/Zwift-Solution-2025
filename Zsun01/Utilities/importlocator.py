import sys
import os
from typing import List, Tuple
from pydantic import BaseModel, DirectoryPath, validate_call

class FolderConfig(BaseModel):
    name: str
    path: DirectoryPath

class FileClassConfig(BaseModel):
    folder: str
    file_class_pairs: List[Tuple[str, str]]

class ImportLocator:
    @validate_call
    def __init__(self, base_dir: DirectoryPath, folders: List[FolderConfig], files_classes: List[FileClassConfig]):
        self.base_dir = base_dir
        self.folders = folders
        self.files_classes = files_classes
        self.add_folders_to_path()
        self.check_files_exist()
        self.import_classes()

    def add_folders_to_path(self):
        for folder in self.folders:
            folder_path = os.path.abspath(os.path.join(self.base_dir, folder.name))
            print(f"Adding {folder.name} directory to path: {folder_path}")
            sys.path.append(folder_path)

        # Print sys.path list to verify, sorted in alphabetical order
        print("sys.path (sorted):")
        for path in sorted(sys.path):
            if path.startswith(str(self.base_dir)):
                print(f"  Program path: {path}")
            else:
                print(f"  Local path: {path}")

    def check_files_exist(self):
        self.files_exist = {}
        for file_class_config in self.files_classes:
            for file_class in file_class_config.file_class_pairs:
                file_path = os.path.join(self.base_dir, file_class_config.folder, f"{file_class[0]}.py")
                file_exists = os.path.exists(file_path)
                self.files_exist[file_class[0]] = file_exists
                print(f"{file_class[0]}.py exists: {file_exists}")

    def import_classes(self):
        for file_class_config in self.files_classes:
            for file_class in file_class_config.file_class_pairs:
                file_name = file_class[0]
                if self.files_exist[file_name]:
                    try:
                        module = __import__(file_class[0], fromlist=[file_class[1]])
                        globals()[file_class[1]] = getattr(module, file_class[1])
                        print(f"Successfully imported {file_class[1]} from {file_class[0]}")
                    except ImportError as e:
                        print(f"Error importing {file_class[1]} from {file_class[0]}: {e}")
                else:
                    print(f"Cannot import {file_class[1]} from {file_class[0]} as it does not exist.")

    @validate_call
    def import_specific_function(self, module_name: str, function_name: str):
        try:
            module = __import__(module_name, fromlist=[function_name])
            globals()[function_name] = getattr(module, function_name)
            print(f"Successfully imported {function_name} from {module_name}")
        except ImportError as e:
            print(f"Error importing {function_name} from {module_name}: {e}")

    @validate_call
    def import_nested_module(self, parent_module: str, nested_module: str):
        try:
            module = __import__(f"{parent_module}.{nested_module}", fromlist=[nested_module])
            globals()[nested_module] = module
            print(f"Successfully imported {nested_module} from {parent_module}")
        except ImportError as e:
            print(f"Error importing {nested_module} from {parent_module}: {e}")

# Example usage
if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    folders = [
        FolderConfig(name='utilities', path=os.path.abspath(os.path.join(base_dir, 'utilities'))),
        FolderConfig(name='classes', path=os.path.abspath(os.path.join(base_dir, 'classes'))),
        FolderConfig(name='repositories', path=os.path.abspath(os.path.join(base_dir, 'repositories')))
    ]
    files_classes = [
        FileClassConfig(folder='classes', file_class_pairs=[('PersonDataClass', 'PersonDataTransferObject')]),
        FileClassConfig(folder='utilities', file_class_pairs=[('JghSerialization', 'JghSerialization')])
    ]

    import_locator = ImportLocator(base_dir=base_dir, folders=folders, files_classes=files_classes)
    import_locator.import_specific_function('utilities.some_module', 'some_function')
    import_locator.import_nested_module('utilities', 'nested_module')

