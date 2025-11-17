import os

ROOT_DIR = r"C:\Users\johng\source\repos\Zwift-Solution-2025"

def delete_bak_files(root_dir):
    deleted = []
    for dirpath, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".bak"):
                bak_path = os.path.join(dirpath, file)
                try:
                    os.remove(bak_path)
                    deleted.append(bak_path)
                    print(f"Deleted: {bak_path}")
                except Exception as e:
                    print(f"Failed to delete {bak_path}: {e}")
    print(f"Deleted {len(deleted)} .bak files.")

if __name__ == "__main__":
    delete_bak_files(ROOT_DIR)
