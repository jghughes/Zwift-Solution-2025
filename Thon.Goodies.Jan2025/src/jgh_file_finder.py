import os
from typing import Optional

def find_path_to_file(filename: Optional[str] = None) -> str | None:
    """
    Searches the current folder, and then upwards in the folder hierarchy
    to locate the path to the specified file.
    
    Args:
        filename (str): The name of the file to search for.
    
    Returns:
        str | None: The path to the specified file if found, otherwise None.
    """

    if not filename:
        return None

    try:
        current_dir = os.path.abspath(os.path.dirname(__file__))
    except Exception:
        return None
    
   
    while True:
        
        try:
            # Search in the current directory
            potential_path = os.path.join(current_dir, filename)
            if os.path.isfile(potential_path):
                return potential_path.replace("\\", "/")

            # Move up to the parent directory if it exists
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached the root directory
                break
            current_dir = parent_dir
        except Exception:
            return None
    
    return None

# Example usage
if __name__ == "__main__":
    path_to_file = find_path_to_file("appsettings.json")
    if path_to_file:
        print(f"Found appsettings.json at: {path_to_file}")
    else:
        print("appsettings.json not found.")
