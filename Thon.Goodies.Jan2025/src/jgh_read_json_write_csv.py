
import os
import json
import csv
from collections import OrderedDict
from typing import List, Dict, Any, Optional

def is_valid_path(path: str) -> bool:
    """
    Checks if path is a string, contains at least one forward slash, and does not end with a forward slash.

    Args:
        path (str): The path to validate.

    Returns:
        bool: True if the path is valid, False otherwise.
    """
    return "/" in path and not path.endswith("/")


def is_valid_filename(filename: str, required_extension: str) -> bool:
    """
    Checks if filename is a string, ends with the specified required_extension, and does not contain any forward slashes.

    Args:
        filename (str): The filename to validate.
        required_extension (str): The required file extension.

    Returns:
        bool: True if the filename is valid, False otherwise.
    """
    return filename.endswith(required_extension) and "/" not in filename


def raise_exception_if_invalid(
    dirpath: str, filename: str, required_extension: str, must_read_not_write: bool) -> bool:
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
        raise ValueError(
            f"Invalid directory path format.\nThe path must use forward slashes not backslashes and must not end with a slash.\nThe invalid dirpath is: [{dirpath}]"
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


def write_csv(dirpath:str, filename: str, items: Any) -> None:
    try:
        if not items:
            raise ValueError("No items to write to CSV.")
        
        # Determine all unique keys across all dictionaries
        keys : set[str] = set()
        for item in items:
            keys.update(item.keys())
        keys_list :list[str] = list(keys)
        output_file_path = os.path.join(dirpath, filename)
        with open(output_file_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=keys_list, dialect="excel")
            writer.writeheader()
            writer.writerows(items)
        print(f"Success. Work saved:-\r\nRows: {len(items)}\r\nColumns: {len(keys_list)}\r\nOutput CSV filepath: {output_file_path}")

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


def rinse_nested_elements(object_from_json: Any) -> List[Dict[str, Any]]:
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

    if not isinstance(object_from_json, list):
        raise ValueError("Object decoded from raw JSON is not compatible with CSV conversion. It is not an iterable type in python.")

    valid_items = [item for item in object_from_json if isinstance(item, dict)]

    if not valid_items:
        raise ValueError("Object decoded from raw JSON is not compatible with CSV conversion. No valid dictionary elements found.")
    
    return valid_items


def read_json_write_csv(
    input_dirpath: str, input_filename: str, output_dirpath: str, output_filename: str) -> None:
    """
    Reads a JSON file, converts it to a list of dictionaries, and writes it to a CSV file.

    This method performs the following steps:
    1. Validates the input and output directory paths and filenames to ensure they meet the required criteria.
    2. Reads the content of the input JSON file.
    3. Decodes the JSON content into a Python object.
    4. Converts the decoded JSON object into a list of dictionaries suitable for CSV conversion.
    5. Writes the list of dictionaries to the output CSV file.

    If the file contains non-dictionary elements at top level (i.e. non-key-value pairs), they are skipped 
    during the conversion process. Nested dictionaries are converted to their string representation. Keys or 
    values that contain special characters are reproduced without difficulty. A superset of all field names
    in the JSON file is used as the header row in the CSV file. Varying length records are thus handled correctly.

    Args:
        input_dirpath (str): The directory path where the input JSON file is located.
        input_filename (str): The name of the input JSON file.
        output_dirpath (str): The directory path where the output CSV file will be saved.
        output_filename (str): The name of the output CSV file.

    Raises:
        ValueError: If the directory path or filename format is invalid, or if the directory or file does not exist.
        FileNotFoundError: If the input JSON file does not exist.
        IOError: If there is an error reading the input JSON file.
        ValueError: If the JSON content is empty or not compatible with CSV conversion.
        Exception: If any other error occurs during the process.
    """
    try:
        raise_exception_if_invalid(input_dirpath, input_filename, ".json", True)
        raise_exception_if_invalid(output_dirpath, output_filename, ".csv", False)
        jsontext = read_text(input_dirpath, input_filename)
        decoded_object = decode_json(jsontext)
        if not decoded_object:  # Check if the JSON object is empty
            raise ValueError("Input JSON is empty. No data to convert to CSV.")
        suitable_object = rinse_nested_elements(decoded_object)
        write_csv(output_dirpath, output_filename, suitable_object)
    except Exception as e:
        error_message = f"\r\nError: Exception raised. Something went wrong.\r\nError: Failed to read json file [{input_filename}] and write to csv file [{output_filename}].\r\nError: {e}"
        raise Exception(error_message)


def read_json_write_abridged_csv(
    input_dirpath: str,
    input_filename: str,
    output_dirpath: str,
    output_filename: str,
    your_excel_column_shortlist: Optional[List[str]],
    your_excel_column_headers: Optional[Dict[str, str]],
) -> None:
    """
    Reads a JSON file, converts it to a list of dictionaries, filters columns, replaces keys with headers, 
    and writes it to a CSV file.

    This method performs the following steps:
    1. Validates the input and output directory paths and filenames to ensure they meet the required criteria.
    2. Reads the content of the input JSON file.
    3. Decodes the JSON content into a Python object.
    4. Converts the decoded JSON object into a list of dictionaries suitable for CSV conversion.
    5. Filters the list of dictionaries to include only specified columns.
    6. Replaces dictionary keys with specified headers if provided.
    7. Writes the filtered and transformed list of dictionaries to the output CSV file.

    If the file contains non-dictionary elements at the top level (i.e., non-key-value pairs), they are skipped 
    during the conversion process. Nested dictionaries are converted to their string representation. Keys or 
    values that contain special characters are reproduced without difficulty. A superset of all field names
    in the JSON file is used as the header row in the CSV file. Varying length records are thus handled correctly.

    This method enables the selection of a subset of columns from the JSON data, allowing for more focused 
    and relevant CSV output. This method allows for renaming columns in the output CSV file, providing more 
    meaningful or user-friendly headers.

    Args:
        input_dirpath (str): The directory path where the input JSON file is located.
        input_filename (str): The name of the input JSON file.
        output_dirpath (str): The directory path where the output CSV file will be saved.
        output_filename (str): The name of the output CSV file.
        your_excel_column_headers (Dict[str, str], optional): A dictionary mapping old keys to new headers. 
            Defaults to None.
        your_excel_column_shortlist (List[str], optional): A list of columns to include in the output CSV file. 
            Defaults to None.

    Raises:
        ValueError: If the directory path or filename format is invalid, or if the directory or file does not exist.
        FileNotFoundError: If the input JSON file does not exist.
        IOError: If there is an error reading the input JSON file.
        ValueError: If the JSON content is empty or not compatible with CSV conversion.
        Exception: If any other error occurs during the process.
    """
    try:

        raise_exception_if_invalid(input_dirpath, input_filename, ".json", True)
        raise_exception_if_invalid(output_dirpath, output_filename, ".csv", False)
        jsontext = read_text(input_dirpath, input_filename)
        decoded_object = decode_json(jsontext)
        if not decoded_object:  # Check if the JSON object is empty
            raise ValueError("Input JSON is empty. No data to convert to CSV.")
        suitable_object = rinse_nested_elements(decoded_object)
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