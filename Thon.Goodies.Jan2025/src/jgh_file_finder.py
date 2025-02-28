import os
from typing import Optional

# Configure logging
import logging
logger = logging.getLogger(__name__)


def find_directory_that_contains_file(filename: Optional[str] = None, directory: Optional[str] = None) -> str | None:
    """
    Searches for the named file everywhere in the given directory, including all subdirectories. 
    Returns the directory path of the folder containing the file. The method tries its best to 
    find the file even if the caller chooses not to specify a directory. In this case, the method 
    searches everywhere in the current working directory of the system. This is helpful
    in circumstances where the caller wishes to search the working directory but doesn't know 
    where/what it is.
    
    Args:
        filename (str): The name of the file to search for.
        directory (str): The parent directory to start the search in.
    
    Returns:
        str | None: The directory path of the folder containing the given
            file if found, otherwise None.
    """
    if not filename:
        return None

    if directory is None:
        directory = os.getcwd()  # Use current working directory if directory is not provided

    try:
        directory = os.path.abspath(directory)  # Normalize the base directory
    except Exception:
        return None

    for root, dirs, files in os.walk(directory):
        if filename in files:
            return root.replace("\\", "/")

    return None

def main():
    dir_path = find_directory_that_contains_file("appsettings.json")
    if dir_path:
        print(f"Found appsettings.json at: {dir_path}")
    else:
        print("appsettings.json not found.")


# Example usage
if __name__ == "__main__":
    main()
