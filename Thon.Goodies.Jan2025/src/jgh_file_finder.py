import os
from typing import Optional

# Configure logging
import logging
logger = logging.getLogger(__name__)


def find_directory_that_contains_file(filename: Optional[str] = None, parent_dir: Optional[str] = None) -> str | None:
    """
    Begins by searching the given parent directory and then traverse downwards in the directory tree
    to locate the full directory path of the folder containing the given file.
    If parent_dir is None, the current working directory is assumed to be as the parent directory.
    On many/most occasions this will be a false asumption, so it is recommended to provide the parent_dir.
    
    Args:
        filename (str): The name of the file to search for.
        parent_dir (str): The parent directory to start the search from.
    
    Returns:
        str | None: The directory path of the folder containing the given
            file if found, otherwise None.
    """
    if not filename:
        return None

    if parent_dir is None:
        parent_dir = os.getcwd()  # Use current working directory if parent_dir is not provided

    try:
        parent_dir = os.path.abspath(parent_dir)  # Normalize the base directory
    except Exception:
        return None

    for root, dirs, files in os.walk(parent_dir):
        if filename in files:
            return root.replace("\\", "/")

    return None

# Example usage
if __name__ == "__main__":
    # path_to_file = find_filepath("appsettings.json")
    # if path_to_file:
    #     print(f"Found appsettings.json at: {path_to_file}")
    # else:
    #     print("appsettings.json not found.")

    dir_path = find_directory_that_contains_file("appsettings.json")
    if dir_path:
        print(f"Found appsettings.json at: {dir_path}")
    else:
        print("appsettings.json not found.")

