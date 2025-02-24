import os
from typing import Optional

# Configure logging
import logging
logger = logging.getLogger(__name__)

def find_filepath(filename: Optional[str] = None) -> str | None:
    """
    Searches the base directory and then downwards in the folder hierarchy
    to locate the full file path of the specified file. Use the obtained
    path for io read/write operations on the file.

    The base directory is determined by the BASE_DIR environment variable.
    If this has not been set, the current working directory is used as the base directory.
    
    Args:
        filename (str): The name of the file to search for.
    
    Returns:
        str | None: The full file path (inclusive of filename) of the 
            specified file if found, otherwise None.
    """
    base_dir = os.getenv('BASE_DIR', os.getcwd())  # Use BASE_DIR environment variable or current working directory
    dirpath = find_dirpath(filename, base_dir)
    if dirpath and isinstance(filename, str):
        return os.path.join(dirpath, filename).replace("\\", "/")
    return None

def find_dirpath(filename: Optional[str] = None, base_dir: Optional[str] = None) -> str | None:
    """
    Searches the specified base directory and then downwards in the folder hierarchy
    to locate the full directory path of the folder containing the specified file.
    If base_dir is not provided, the current working directory is used as the base directory.
    
    Args:
        filename (str): The name of the file to search for.
        base_dir (str): The base directory to start the search from.
    
    Returns:
        str | None: The directory path of the folder containing the specified
            file if found, otherwise None.
    """
    if not filename:
        return None

    if base_dir is None:
        base_dir = os.getcwd()  # Use current working directory if base_dir is not provided

    try:
        base_dir = os.path.abspath(base_dir)  # Normalize the base directory
    except Exception:
        return None

    for root, dirs, files in os.walk(base_dir):
        if filename in files:
            return root.replace("\\", "/")

    return None

# Example usage
if __name__ == "__main__":
    path_to_file = find_filepath("appsettings.json")
    if path_to_file:
        print(f"Found appsettings.json at: {path_to_file}")
    else:
        print("appsettings.json not found.")

    dir_path = find_dirpath("appsettings.json")
    if dir_path:
        print(f"Found appsettings.json at: {dir_path}")
    else:
        print("appsettings.json not found.")

