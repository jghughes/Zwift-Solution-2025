
import os
import json
import csv
from collections import OrderedDict
from typing import List, Dict, Any, Optional
import pandas as pd

# Configure logging
import logging

def is_valid_path(path: str) -> bool:
    """
    Checks if path is a string, contains at least one forward slash, and does not end with a forward slash.

    Args:
        path (str): The path to validate.

    Returns:
        bool: True if the path is valid, False otherwise.
    """
    return "/" in path and path.endswith("/")


def is_valid_filename(filename: str, required_extension: Optional[str]) -> bool:
    """
    Checks if filename is a string, optionally ends with the specified required_extension,
    and does not contain any forward slashes.

    Args:
        filename (str): The filename to validate.
        required_extension (Optional[str]): The required file extension. If None, the extension check is ignored.

    Returns:
        bool: True if the filename is valid, False otherwise.
    """
    if "/" in filename:
        return False
    if required_extension is None:
        return True
    return filename.endswith(required_extension)

def raise_exception_if_invalid(dirpath: str, filename: str, required_extension: str, must_read_not_write: bool) -> bool:
    """
    Validates the directory path and filename, ensuring they meet specified criteria.

    Args:
        dirpath (str): The directory path to validate.
        filename (str): The filename to validate.
        required_extension (str): The required file extension for the filename.
        must_read_not_write (bool): Flag indicating if the file must exist for reading.

    Returns:
        bool: True if the directory path and filename are valid.

    Raises:
        ValueError: If the directory path or filename format is invalid, or if the directory or file does not exist.
    """
    if not is_valid_path(dirpath):
        # Check directory format
        print("Invalid directory path.")
        raise ValueError(
            f"Error: Invalid directory path format. The dirpath is [{dirpath}]"
        )

    if not is_valid_filename(filename, required_extension):
        # Check filename format
        print("Invalid filename, or incorrect filename extension.")
        raise ValueError(
            f"Error: Invalid filename format, or incorrect filename extension. The filename is [{filename}]"
        )

    if not os.path.exists(dirpath):
        # Check if the directory path exists
        print(f"Directory path does not exist.")
        raise ValueError(f"Error: Directory path does not exist. [{dirpath}]")

    if must_read_not_write and not os.path.isfile(os.path.join(dirpath, filename)):
        # Check if the file exists for reading
        print(f"Read file does not exist.")
        raise ValueError(f"Error: Read file does not exist. [{os.path.join(dirpath, filename)}]")

    return True

def help_select_filepaths_in_folder(file_names: Optional[list[str]], file_extension: str, dir_path: str) -> list[str]:
    """
    Select file paths in a specified folder based on file names and file extension.

    This function retrieves all file paths in the given directory that match the specified file extension.
    If a list of file names is provided, it filters the file paths to include only those whose base names
    (excluding the extension) match the provided file names. If no file names are provided, all file paths
    with the specified extension are returned.

    Args:
    file_names (Optional[list[str]]): A list of file names (without extensions) to filter the file paths.
                                    If None or empty, all file paths with the specified extension are returned.
    file_extension (str): The file extension to filter by (e.g., ".json").
    dir_path (str): The directory path where the files are located.

    Returns:
    list[str]: A list of file paths that match the specified criteria.

    Raises:
    ValueError: If `dir_path` is not a valid non-empty string.
    FileNotFoundError: If the specified directory does not exist.

    Example:
    >>> help_select_filepaths_in_folder(["file1", "file2"], ".json", "/path/to/dir")
    ['/path/to/dir/file1.json', '/path/to/dir/file2.json']

    >>> help_select_filepaths_in_folder(None, ".json", "/path/to/dir")
    ['/path/to/dir/file1.json', '/path/to/dir/file2.json', '/path/to/dir/file3.json']
    """

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    all_file_paths = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(file_extension)]

    if file_names is None or not file_names:
        return all_file_paths

    filtered_file_paths : list[str] = []

    for file_path in all_file_paths:
        file_name = os.path.basename(file_path)
        if file_name[:-5] in file_names:
            filtered_file_paths.append(file_path)

    return filtered_file_paths



def read_text(dirpath: str, filename: str) -> str:
    """
    Reads the content of a file as text.

    Args:
        dirpath (str): The directory path where the file is located.
        filename (str): The name of the file to read.

    Returns:
        str: The content of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """
    input_filepath = os.path.join(dirpath, filename)
    try:
        with open(input_filepath, "r", encoding="utf-8") as my_file:
            return my_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {input_filepath}")
    except IOError as e:
        raise IOError(f"Error reading file {input_filepath}: {e}")

def read_filepath_as_text(filepath: str) -> str:
    """
    Reads the content of a file as text.
    Args:
        filepath (str): The path to the file to read.
    Returns:
        str: The content of the file as a string.
    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as my_file:
            return my_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except IOError as e:
        raise IOError(f"Error reading file {filepath}: {e}")

def write_csv(dirpath: str, filename: str, items: List[Dict[str, Any]]) -> None:
    """
    Writes a list of dictionaries to a CSV file.

    Args:
        dirpath (str): The directory path where the CSV file will be saved.
        filename (str): The name of the CSV file to write.
        items (List[Dict[str, Any]]): The items to write to the CSV file.

    Raises:
        ValueError: If there is no items to write to the CSV file.
    """
    try:
        if not items:
            raise ValueError("No items to write to CSV.")
        # Use the first dictionary in the List[Dict[str, Any]] to get the field names. Beware, this is very risky. The first record may not have all the keys, or they may be in the wrong order.
        keys = list(items[0].keys())
        output_file_path = os.path.join(dirpath, filename)
        with open(output_file_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=keys, dialect="excel")
            writer.writeheader()
            writer.writerows(items)
        print(f"Success. Work saved:-\r\nRows: {len(items)}\r\nColumns: {len(keys)}\r\nOutput CSV filepath: {output_file_path}")

    except Exception as e:
        error_message = (f"\r\nError: Exception raised. Something went wrong.\r\nError: Failed to write to csv file [{filename}].\r\nError: {e}")
        raise Exception(error_message)

def write_csv_with_fieldnames(
    dirpath: str, filename: str, items: List[Dict[str, Any]], fieldnames: List[str]
) -> None:
    """
    Writes a list of dictionaries to a CSV file with specified fieldnames.

    Args:
        dirpath (str): The directory path where the CSV file will be saved.
        filename (str): The name of the CSV file to write.
        items (List[Dict[str, Any]]): The items to write to the CSV file.
        fieldnames (List[str]): The list of fieldnames to use for the CSV file.

    Raises:
        ValueError: If any of the input parameters are of the wrong type or are None.
    """
    try:
        # Check input parameters
        if not items:
            raise ValueError("No items to write to CSV.")
        output_file_path = os.path.join(dirpath, filename)
        with open(output_file_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect="excel")
            writer.writeheader()
            writer.writerows(items)
        print(f"Success. Work saved:-\r\nRows: {len(items)}\r\nColumns: {len(fieldnames)}\r\nOutput CSV filepath: {output_file_path}")

    except Exception as e:
        error_message = (f"\r\nError: Exception raised. Something went wrong.\r\nError: Failed to write to csv file [{filename}] with specified fieldnames {fieldnames}.\r\nError: {e}")
        raise Exception(error_message)


def decode_json(text: str) -> Any:
    """
    Deserializes a JSON string into a Python object.

    Args:
        text (str): The JSON string to deserialize.

    Returns:
        Any: The deserialized Python object.

    Raises:
        ValueError: If the text cannot be deserialized into a JSON object.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")


def make_ready_for_csv(object_from_json: Any) -> List[Dict[str, Any]]:
    """
    Converts a JSON object to a list of dictionaries compatible with CSV conversion. Checks if the object is a dictionary.
    - If it is a dictionary with exactly one key-value pair, it assigns the value of that single key to the object.
    - If it is a dictionary with more than one key-value pair, it converts the dictionary values to a list of those values and assigns them to the object.
    _ Final if statement ensures that the resulting object is a list of dictionaries. If not, it raises an error.

    Args:
        object_from_json (Any): The JSON object to convert.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries converted from the JSON object.

    Raises:
        ValueError: If the JSON structure is not compatible for CSV conversion.
    """
    # if isinstance(object_from_json, dict):
    #     object_from_json = (
    #         next(iter(object_from_json.values()))
    #         if len(object_from_json) == 1
    #         else list(object_from_json.values())
    #     )

    if not isinstance(object_from_json, list) or not all(
        isinstance(item, dict) for item in object_from_json
    ):
        raise ValueError("JSON structure is not compatible with CSV conversion.")

    return object_from_json


def read_json_write_csv(
    input_dirpath: str, input_filename: str, output_dirpath: str, output_filename: str
) -> None:
    """
    Reads a JSON file, converts it to a list of dictionaries, and writes it to a CSV file.

    Args:
        input_dirpath (str): The directory path where the input JSON file is located.
        input_filename (str): The name of the input JSON file.
        output_dirpath (str): The directory path where the output CSV file will be saved.
        output_filename (str): The name of the output CSV file.

    Raises:
        Exception: If any error occurs during the process.
    """
    try:
        raise_exception_if_invalid(input_dirpath, input_filename, ".json", True)
        raise_exception_if_invalid(output_dirpath, output_filename, ".csv", False)
        jsontext = read_text(input_dirpath, input_filename)
        decoded_object = decode_json(jsontext)
        suitable_object = make_ready_for_csv(decoded_object)
        write_csv(output_dirpath, output_filename, suitable_object)
    except Exception as e:
        error_message = f"\r\nError: Exception raised. Something went wrong.\r\nError: Failed to read json file [{input_filename}] and write to csv file [{output_filename}].\r\nError: {e}"
        raise Exception(error_message)

def read_json_write_pretty_csv(
    input_dirpath: str,
    input_filename: str,
    output_dirpath: str,
    output_filename: str,
    your_excel_column_shortlist: Optional[List[str]],
    your_excel_column_headers: Optional[Dict[str, str]],
) -> None:
    """
    Reads a JSON file, converts it to a list of dictionaries, filters columns, replaces keys with headers, and writes it to a CSV file.

    Args:
        input_dirpath (str): The directory path where the input JSON file is located.
        input_filename (str): The name of the input JSON file.
        output_dirpath (str): The directory path where the output CSV file will be saved.
        output_filename (str): The name of the output CSV file.
        your_excel_column_headers (Dict[str, str], optional): A dictionary mapping old keys to new headers. Defaults to None.
        your_excel_column_shortlist (List[str], optional): A list of columns to include in the output CSV file. Defaults to None.

    Raises:
        Exception: If any error occurs during the process.
    """
    try:
        raise_exception_if_invalid(input_dirpath, input_filename, ".json", True)
        raise_exception_if_invalid(output_dirpath, output_filename, ".csv", False)
        jsontext = read_text(input_dirpath, input_filename)
        decoded_object = decode_json(jsontext)
        suitable_object = make_ready_for_csv(decoded_object)

        # Ensure your_excel_column_shortlist is a list
        if your_excel_column_shortlist is None:
            your_excel_column_shortlist = []

        # Use keys from the first dictionary as the default column list if your_excel_column_shortlist is empty
        if not your_excel_column_shortlist and suitable_object:
            your_excel_column_shortlist = list(suitable_object[0].keys())

        # Ensure your_excel_column_headers is a dictionary
        if your_excel_column_headers is None:
            your_excel_column_headers = {}

        # Filter columns and replace keys with headers if provided
        if your_excel_column_shortlist or your_excel_column_headers:
            suitable_object = [
                OrderedDict(
                    (your_excel_column_headers.get(key, key), item.get(key, ""))
                    for key in your_excel_column_shortlist
                )
                for item in suitable_object
            ]

        # Ensure the correct order of columns in the CSV output
        fieldnames = [
            your_excel_column_headers.get(key, key)
            for key in your_excel_column_shortlist
        ]

        write_csv_with_fieldnames(
            output_dirpath, output_filename, suitable_object, fieldnames
        )
    except Exception as e:
        error_message = (f"\r\nError: Exception raised. Something went wrong.\r\nError: Failed to read json file [{input_filename}] and write to csv file [{output_filename}].\r\nError: {e}"
        )
        raise Exception(error_message)

def write_pandas_dataframe_as_xlsx(df: pd.DataFrame, file_name: str, dir_path : str):
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")
    if not file_name or not file_name.endswith(".xlsx"):
        raise ValueError(f"Invalid file name: '{file_name}'. Ensure it ends with '.xlsx'.")

    raise_exception_if_invalid(dir_path, file_name, ".xlsx", must_read_not_write=False)
    output_file_path = os.path.join(dir_path, file_name)
    df.to_excel(output_file_path, index=False, engine="openpyxl")

def write_json_file(text: str, file_name: str, dir_path : str):
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")
    if not file_name or not file_name.endswith(".json"):
        raise ValueError(f"Invalid file name: '{file_name}'. Ensure it ends with '.json'.")

    raise_exception_if_invalid(dir_path, file_name, ".json", must_read_not_write=False)
    output_file_path = os.path.join(dir_path, file_name)
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(text)

def write_html_file(text: str, file_name: str, dir_path : str):
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")
    if not file_name or not file_name.endswith(".html"):
        raise ValueError(f"Invalid file name: '{file_name}'. Ensure it ends with '.html'.")

    raise_exception_if_invalid(dir_path, file_name, ".html", must_read_not_write=False)
    output_file_path = os.path.join(dir_path, file_name)
    with open(output_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write(text)
