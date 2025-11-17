import os

ROOT_DIR = r"C:\Users\johng\source\repos\Zwift-Solution-2025"

def revert_bak_files(root_dir):
    reverted = []
    for dirpath, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py.bak"):
                py_file = file[:-4]  # Remove '.bak'
                bak_path = os.path.join(dirpath, file)
                py_path = os.path.join(dirpath, py_file)
                # Replace .py with .bak
                try:
                    os.replace(bak_path, py_path)
                    reverted.append(py_path)
                    print(f"Reverted: {py_path}")
                except Exception as e:
                    print(f"Failed to revert {py_path}: {e}")
    print(f"Reverted {len(reverted)} files.")

if __name__ == "__main__":
    revert_bak_files(ROOT_DIR)
