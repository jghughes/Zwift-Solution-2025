import os

def find_path_to_appsettings() -> str | None:
    current_dir = os.path.abspath(os.getcwd())
    while current_dir != os.path.dirname(current_dir):
        potential_path = os.path.join(current_dir, "appsettings.json")
        if os.path.isfile(potential_path):
            # Normalize the path separators
            return potential_path.replace("\\", "/")
        current_dir = os.path.dirname(current_dir)
    return None

# def find_path_to_appsettings() -> str | None:
#     """
#     Searches the current folder, sibling folders, and then upwards in the folder hierarchy
#     to locate the path to appsettings.json.
    
#     Returns:
#         str | None: The path to appsettings.json if found, otherwise None.
#     """
#     try:
#         current_dir = os.path.abspath(os.path.dirname(__file__))
#     except Exception:
#         return None
    
#     visited_dirs: set[str] = set()
    
#     while True:
#         # Search in the current directory
#         try:
#             potential_path = os.path.join(current_dir, 'appsettings.json')
#             if os.path.isfile(potential_path):
#                 return potential_path
#         except Exception:
#             return None
        
#         # Search in sibling directories
#         try:
#             parent_dir = os.path.dirname(current_dir)
#             if parent_dir == current_dir:  # Reached the root directory
#                 break
            
#             for sibling in os.listdir(parent_dir):
#                 sibling_path = os.path.join(parent_dir, sibling)
#                 if os.path.isdir(sibling_path) and sibling_path not in visited_dirs:
#                     potential_path = os.path.join(sibling_path, 'appsettings.json')
#                     if os.path.isfile(potential_path):
#                         return potential_path
#                     visited_dirs.add(sibling_path)
#         except Exception:
#             return None
        
#         # Move to the parent directory
#         try:
#             current_dir = parent_dir
#         except Exception:
#             return None
    
#     return None

# Example usage
if __name__ == "__main__":
    path_to_appsettings = find_path_to_appsettings()
    if path_to_appsettings:
        print(f"Found appsettings.json at: {path_to_appsettings}")
    else:
        print("appsettings.json not found.")
