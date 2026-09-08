import json
import csv
import logging
from typing import List, Dict, Any, Union
from pathlib import Path
import pandas as pd
from jgh_path_helpers import throw_if_file_path_invalid_or_not_exists, throw_if_dirpath_invalid_or_not_exists, throw_if_file_path_ingredients_invalid_or_not_exists
from jgh_string import cleanup_name_string, sanitise_string

logger = logging.getLogger(__name__)

# ===========================
# Parsing Utilities
# ===========================

def parse_json(text: str) -> Any:
    """
    Deserializes a JSON string into a Python object.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")

# ===========================
# Directory Listing Utilities
# ===========================

def list_files_in_directory(dirpath: Path, pattern: str) -> List[Path]:
    """
    List files in a directory matching a given wildcard pattern (e.g., "*.json").

    Raises ValueError if the directory is invalid or does not exist.
    Raises IOError if listing files fails.
    """
    throw_if_dirpath_invalid_or_not_exists(dirpath)
    try:
        return [f for f in dirpath.glob(pattern) if f.is_file()]
    except Exception as e:
        raise IOError(f"Error listing files in directory {dirpath}: {e}")

# ===========================
# File Reading Utilities
# ===========================

def read_text_from_path(filepath: Path) -> str:
    """
    Reads the content of a file as text, given a single Path object.

    Validates that the path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.
    """
    throw_if_file_path_invalid_or_not_exists(filepath)
    try:
        with filepath.open("r", encoding="utf-8") as my_file:
            return my_file.read()
    except Exception as err:
        raise IOError(f"Error reading file {filepath}: {err}")

def read_text(dirpath: Path, filename: str) -> str:
    """
    Reads the content of a file as text.

    Validates that the file path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        Path(filename).suffix,
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open("r", encoding="utf-8") as my_file:
            return my_file.read()
    except Exception as err:
        raise IOError(f"Error reading file {file_path}: {err}")

def read_lines(dirpath: Path, filename: str) -> List[str]:
    """
    Reads the content of a file as a list of lines.

    Validates that the file path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        Path(filename).suffix,
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open("r", encoding="utf-8") as my_file:
            return my_file.readlines()
    except Exception as err:
        raise IOError(f"Error reading file {file_path}: {err}")

def read_html(dirpath: Path, filename: str) -> str:
    """
    Reads the content of an HTML file as text.

    Validates that the file path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".html",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open("r", encoding="utf-8") as html_file:
            return html_file.read()
    except Exception as err:
        raise IOError(f"Error reading HTML file {file_path}: {err}")

def read_csv(dirpath: Path, filename: str) -> List[Dict[str, Any]]:
    """
    Reads a CSV file and returns a list of dictionaries.

    Validates that the file path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".csv",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [dict(row) for row in reader]
    except Exception as err:
        raise IOError(f"Error reading CSV file {file_path}: {err}")

def read_csv_to_dataframe(dirpath: Path, filename: str) -> pd.DataFrame:
    """
    Reads a CSV file and returns a pandas DataFrame.

    Validates that the file path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".csv",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        return pd.read_csv(file_path)
    except Exception as err:
        raise IOError(f"Error reading CSV file {file_path}: {err}")

def read_excel(dirpath: Path, filename: str, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    """
    Reads an Excel (.xlsx) file and returns a pandas DataFrame.

    Validates that the file path is absolute, exists, and is a file.
    Raises ValueError if any check fails, and IOError if reading the file fails.

    Args:
        dirpath: Directory containing the file.
        filename: Name of the .xlsx file.
        sheet_name: Name (str) or zero-based index (int) of the worksheet to read.
            Defaults to 0, i.e. the first worksheet in the workbook.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".xlsx",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
    except Exception as err:
        raise IOError(f"Error reading Excel file {file_path}: {err}")

def clean_dataframe_text_column(df: pd.DataFrame, column_name: str, use_name_cleanup: bool = True) -> pd.DataFrame:
    """
    Cleans a text column in a DataFrame by removing emojis, invalid Unicode,
    and other unwanted characters (e.g. from rider name fields).

    Operates on a copy of the DataFrame; the original is left unmodified.

    Args:
        df: The DataFrame to clean.
        column_name: The name of the column to clean. Must exist in df.
        use_name_cleanup: If True (default), applies cleanup_name_string, which also
            strips known team/club tag substrings (e.g. 'ZSUN', 'CC') in addition to
            sanitising invalid Unicode and emoji. If False, applies only sanitise_string.

    Returns:
        A new DataFrame with the specified column cleaned.

    Raises:
        ValueError: If column_name is not present in df.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame. Available columns: {list(df.columns)}")

    cleaning_function = cleanup_name_string if use_name_cleanup else sanitise_string

    cleaned_df = df.copy()
    cleaned_df[column_name] = cleaned_df[column_name].apply(
        lambda value: cleaning_function(value) if pd.notna(value) else value
    )
    return cleaned_df

# ===========================
# File Writing Utilities
# ===========================

def write_text_with_txt_file_extension(dirpath: Path, filename: str, text: str) -> str:
    """
    Writes text to a file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".txt",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open('w', encoding='utf-8') as text_file:
            text_file.write(text)
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing file {file_path}: {err}")

def write_lines_with_txt_file_extension(dirpath: Path, filename: str, lines: List[str]) -> str:
    """
    Writes a list of text lines to a file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".txt",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open('w', encoding='utf-8') as text_file:
            text_file.writelines(lines)
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing file {file_path}: {err}")

def write_text_with_json_file_extension(dirpath: Path, filename: str, text: str) -> str:
    """
    Writes JSON text to a file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open('w', encoding='utf-8') as json_file:
            json_file.write(text)
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing file {file_path}: {err}")

def write_text_with_csv_file_extension(dirpath: Path, filename: str, text: str) -> str:
    """
    Writes CSV text to a file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".csv",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open('w', encoding='utf-8') as json_file:
            json_file.write(text)
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing file {file_path}: {err}")

def write_text_with_html_file_extension(dirpath: Path, filename: str, text: str) -> str:
    """
    Writes HTML text to a file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".html",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        with file_path.open('w', encoding='utf-8') as html_file:
            html_file.write(text)
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing file {file_path}: {err}")

def write_dataframe_as_xlsx_file(dirpath: Path, filename: str, dataframe: pd.DataFrame) -> str:
    """
    Writes a pandas DataFrame to an Excel (.xlsx) file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".xlsx",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        dataframe.to_excel(file_path, index=False, engine="openpyxl")  # type: ignore
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing Excel file {file_path}: {err}")

def write_dataframe_as_csv_file(dirpath: Path, filename: str, dataframe: pd.DataFrame) -> str:
    """
    Writes a pandas DataFrame to a CSV file.

    Validates that the file path is absolute and the directory exists.
    Raises ValueError if any check fails, and IOError if writing the file fails.
    Returns the string path to the written file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".csv",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    file_path = Path(dirpath) / Path(filename)
    try:
        dataframe.to_csv(file_path, index=False, encoding="utf-8")
        return str(file_path)
    except Exception as err:
        raise IOError(f"Error writing CSV file {file_path}: {err}")