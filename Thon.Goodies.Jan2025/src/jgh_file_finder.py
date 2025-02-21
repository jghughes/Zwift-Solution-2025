import os
from typing import Optional

# Configure logging
import logging
logger = logging.getLogger(__name__)

def find_filepath(filename: Optional[str] = None) -> str | None:
    """
    Searches the current folder, and then upwards in the folder hierarchy
    to locate the full file path of the specified file. Use the obtained
    path for io read/write operations on the file.
    
    Args:
        filename (str): The name of the file to search for.
    
    Returns:
        str | None: The the full file path (inclusive of filename) of the 
            specified file if found, otherwise None.
    """
    dirpath = find_dirpath(filename)
    if dirpath and isinstance(filename, str):
        return os.path.join(dirpath, filename).replace("\\", "/")
    return None


def find_dirpath(filename: Optional[str] = None) -> str | None:
    """
    Searches the current folder, and then upwards in the folder hierarchy
    to locate the directory path of the folder containing the specified file.
    
    Args:
        filename (str): The name of the file to search for.
    
    Returns:
        str | None: The directory path of the folder containing the specified
            file if found, otherwise None.
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
            candidate_full_filepath = os.path.join(current_dir, filename)
            if os.path.isfile(candidate_full_filepath):
                return current_dir.replace("\\", "/")

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
    path_to_file = find_filepath("appsettings.json")
    if path_to_file:
        print(f"Found appsettings.json at: {path_to_file}")
    else:
        print("appsettings.json not found.")
