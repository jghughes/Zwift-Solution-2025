import os
import re
from typing import Callable, Optional, Tuple, List
from pathlib import Path
from urllib.parse import urlparse
from jgh_exceptions import AlertMessageError
# =========================
# Constants
# =========================

AZURE_CONTAINER_NAME_PATTERN = r"[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?"
AZURE_BLOB_ENDPOINT_PATTERN = r"[a-z0-9\-]+\.blob_name\.core\.windows\.net"
BLOB_NAME_INVALID_CHARS = ['\\', '?', '#', '%']
BLOB_NAME_MIN_LENGTH = 1
BLOB_NAME_MAX_LENGTH = 1024

# =========================
# Format-only Validation Functions
# =========================


def is_valid_dirpath(dirpath: str) -> Tuple[bool, str]:
    try:
        path_obj = Path(dirpath)
        if not path_obj.is_absolute():
            return False, "Dirpath is not absolute."
        for i, part in enumerate(path_obj.parts):
            # Skip drive part for Windows (e.g., 'C:\\' or 'C:')
            if i == 0 and re.match(r'^[A-Za-z]:\\?$', part):
                continue
            if part in ('', '.', '..'):
                continue
            if re.search(r'[<>:"|?*\x00-\x1F]', part):
                return False, f"Dirpath part '{part}' contains invalid characters."
            if '/' in part or '\\' in part:
                return False, f"Dirpath part '{part}' contains slash or backslash."
        return True, "Dirpath format is valid."
    except Exception as e:
        return False, f"Exception during dirpath validation: {e}"






# def is_valid_dirpath(dirpath: str) -> Tuple[bool, str]:
#     """
#     Returns (True, message) if dirpath is a valid absolute directory path format (does not check existence).
#     Returns (False, message) if invalid.
#     """
#     try:
#         path_obj = Path(dirpath)
#         if not path_obj.is_absolute():
#             return False, "Dirpath is not absolute."
#         for i, part in enumerate(path_obj.parts):
#             # Skip drive part for Windows (e.g., 'C:\\')
#             if i == 0 and re.match(r'^[A-Za-z]:\\?$', part):
#                 continue
#             if part in ('', '.', '..'):
#                 continue
#             if re.search(r'[<>:"|?*\x00-\x1F]', part):
#                 return False, f"Dirpath part '{part}' contains invalid characters."
#             if '/' in part or '\\' in part:
#                 return False, f"Dirpath part '{part}' contains slash or backslash."
#         return True, "Dirpath format is valid."
#     except Exception as e:
#         return False, f"Exception during dirpath validation: {e}"

def is_valid_foldername(foldername: str) -> Tuple[bool, str]:
    """
    Returns (True, message) if foldername is a valid folder name (does not check existence).
    Returns (False, message) if invalid.
    """
    try:
        if not foldername or foldername in ('.', '..'):
            return False, "Foldername is empty or reserved ('.' or '..')."
        if re.search(r'[<>:"/\\|?*\x00-\x1F]', foldername):
            return False, "Foldername contains invalid characters."
        if '/' in foldername or '\x00' in foldername:
            return False, "Foldername contains slash or null byte."
        reserved: set[str] = {'CON', 'PRN', 'AUX', 'NUL'} | {f'COM{i}' for i in range(1, 10)} | {f'LPT{i}' for i in range(1, 10)}
        if foldername.upper() in reserved:
            return False, "Foldername is a reserved NTFS name."
        if foldername[-1] in {' ', '.'}:
            return False, "Foldername cannot end with a space or period."
        if len(foldername) > 255:
            return False, "Foldername exceeds 255 characters."
        return True, "Foldername format is valid."
    except Exception as e:
        return False, f"Exception during foldername validation: {e}"

def is_valid_ntfs_filename_format(filename: str) -> Tuple[bool, str]:
    """Validate NTFS filename format. Returns (is_valid, message)."""
    if not filename:
        return False, "NTFS: Filename cannot be empty."
    if re.search(r'[<>:"/\\|?*\x00-\x1F]', filename):
        return False, "NTFS: Filename contains invalid characters."
    reserved: set[str] = {'CON', 'PRN', 'AUX', 'NUL'} | {f'COM{i}' for i in range(1, 10)} | {f'LPT{i}' for i in range(1, 10)}
    name, _ = os.path.splitext(filename)
    if name.upper() in reserved:
        return False, f"NTFS: Filename '{name}' is a reserved name."
    if filename[-1] in {' ', '.'}:
        return False, "NTFS: Filename cannot end with a space or period."
    if len(filename) > 255:
        return False, "NTFS: Filename exceeds 255 characters."
    return True, "NTFS: Filename is valid."

def is_valid_unix_filename_format(filename: str) -> Tuple[bool, str]:
    """Validate Unix filename format. Returns (is_valid, message)."""
    if not filename:
        return False, "Unix: Filename cannot be empty."
    if '/' in filename:
        return False, "Unix: Filename cannot contain '/'."
    if '\x00' in filename:
        return False, "Unix: Filename cannot contain null byte."
    try:
        if len(filename.encode('utf-8')) > 255:
            return False, "Unix: Filename exceeds 255 bytes."
    except Exception as e:
        return False, f"Unix: Error encoding filename to UTF-8: {e}"
    return True, "Unix: Filename is valid."

def has_file_extension(filename: str) -> Tuple[bool, str]:
    """Check if filename has an extension. Returns (has_extension, message)."""
    if not filename:
        return False, "Filename is not a non-empty string."
    try:
        ext = os.path.splitext(filename)[1]
        if ext == '':
            return False, "Filename does not have an extension."
        return True, f"Filename has extension: {ext}"
    except Exception as e:
        return False, f"Error checking file extension: {e}"

def is_valid_filename(filename: str) -> Tuple[bool, str]:
    """
    Returns (True, message) if filename is valid, (False, error message) if not.
    Only checks format, not existence.
    """
    try:
        if not filename:
            return False, "Filename is empty."
        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*\x00-\x1F]', filename):
            return False, "Filename contains invalid characters."
        # Reserved NTFS names
        reserved: set[str] = {'CON', 'PRN', 'AUX', 'NUL'} | {f'COM{i}' for i in range(1, 10)} | {f'LPT{i}' for i in range(1, 10)}
        name, _ = os.path.splitext(filename)
        if name.upper() in reserved:
            return False, f"Filename '{name}' is a reserved NTFS name."
        # Cannot end with space or period
        if filename[-1] in {' ', '.'}:
            return False, "Filename cannot end with a space or period."
        # Length check
        if len(filename) > 255:
            return False, "Filename exceeds 255 characters."
        # Simple pattern check
        if not re.match(r'^[\w\-. ]+$', filename):
            return False, "Filename contains invalid format."
        return True, "Filename format is valid."
    except Exception as e:
        return False, f"Exception during filename validation: {e}"

def is_valid_url(url: str) -> Tuple[bool, str]:
    """
    Returns (True, message) if url is valid, (False, error message) if not.
    Only checks format, not existence or reachability.
    """
    try:
        if not url:
            return False, "URL is empty or not a string."
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if re.match(pattern, url):
            return True, "URL format is valid."
        else:
            return False, f"URL format is invalid: {url}"
    except Exception as e:
        return False, f"Exception during URL validation: {e}"

# =========================
# Format/Name Validation for Azure Storage
# =========================

def warn_if_blob_name_is_invalid(blob_name: str) -> str|None:
    """
    Validates the blob_name name for Azure Blob Storage.
    Ensures it is a valid NTFS and Unix filename, includes an extension,
    is within allowed length, and does not contain reserved URL characters.
    Returns an warning message string if invalid, or None if all is good.
    """
    if not blob_name.strip():
        return "Error: Invalid blob_name parameter."
    if not (BLOB_NAME_MIN_LENGTH <= len(blob_name) <= BLOB_NAME_MAX_LENGTH):
        return f"Error: blob_name must be between {BLOB_NAME_MIN_LENGTH} and {BLOB_NAME_MAX_LENGTH} characters."
    if any(c in blob_name for c in BLOB_NAME_INVALID_CHARS):
        return "Error: blob_name contains invalid characters."
    filename = os.path.basename(blob_name)
    if not  is_valid_ntfs_filename_format(filename):
        return "Error: blob_name is not a valid NTFS filename."
    if not is_valid_unix_filename_format(filename):
        return "Error: blob_name is not a valid Unix filename."
    if not has_file_extension(filename):
        return "Error: blob_name must include a file extension."
    return None

def warn_if_container_name_is_invalid(container_name: str) -> str|None:
    """
    Validates the Azure Blob Storage container_name name.
    Returns an warning message string if invalid, or None if all is good.
    """
    if not container_name.strip():
        return "Error: Invalid container_name parameter. Parameter is empty."
    if not re.fullmatch(AZURE_CONTAINER_NAME_PATTERN, container_name):
        return "Error: container_name is not valid per Azure naming rules."
    return None

def warn_if_account_name_is_invalid(account_name: str) -> str|None:
    """
    Validates the Azure Blob Storage storage_account_name.
    Returns an warning message string if invalid, or None if all is good.
    """
    if not account_name.strip():
        return "Error: Invalid account_name parameter. Parameter is empty."
    if not re.fullmatch(AZURE_CONTAINER_NAME_PATTERN, account_name):
        return "Error: account_name is not valid per Azure naming rules."
    return None

def validate_azure_storage_blob_name(blob_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validates the blob_name for Azure Blob Storage.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    Pattern and error reporting matches  is_valid_ntfs_filename_format().
    """
    if not blob_name.strip():
        return False, "Error: blob_name parameter is empty or whitespace."
    BLOB_NAME_INVALID_CHARS = ['\\', '?', '#', '%']
    BLOB_NAME_MIN_LENGTH = 1
    BLOB_NAME_MAX_LENGTH = 1024
    if not (BLOB_NAME_MIN_LENGTH <= len(blob_name) <= BLOB_NAME_MAX_LENGTH):
        return False, f"Error: blob_name must be between {BLOB_NAME_MIN_LENGTH} and {BLOB_NAME_MAX_LENGTH} characters."
    for c in BLOB_NAME_INVALID_CHARS:
        if c in blob_name:
            return False, f"Error: blob_name contains invalid character '{c}'."
    filename = os.path.basename(blob_name)
    valid_ntfs, ntfs_error =  is_valid_ntfs_filename_format(filename)
    if not valid_ntfs:
        return False, f"Error: {ntfs_error} The blob_name is [{filename}]"
    valid_unix, unix_error = is_valid_unix_filename_format(filename)
    if not valid_unix:
        return False, f"Error: {unix_error} The blob_name is [{filename}]"
    if not  has_file_extension(filename):
        return False, f"Error: blob_name must include a file extension. The blob_name is [{filename}]"
    return True, None

def validate_azure_storage_container_name(container_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validates the Azure Blob Storage container_name.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    Pattern and error reporting matches  is_valid_ntfs_filename_format().
    """
    if not container_name.strip():
        return False, "Error: container_name parameter is empty or whitespace."
    AZURE_CONTAINER_NAME_PATTERN = r"[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?"
    if not re.fullmatch(AZURE_CONTAINER_NAME_PATTERN, container_name):
        return False, "Error: container_name is not valid per Azure naming rules."
    return True, None

def validate_azure_storage_account_name(account_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validates the Azure Blob Storage storage_account_name.
    Returns (True, None) if valid, or (False, error_message) if invalid.
    Pattern and error reporting matches  is_valid_ntfs_filename_format().
    """
    AZURE_ACCOUNT_NAME_PATTERN = r"^[a-z0-9]{3,24}$"
    if not isinstance(account_name, str):
        return False, "Error: account_name must be a string."
    account_name = account_name.strip()
    if not account_name:
        return False, "Error: account_name parameter is empty or whitespace."
    if not re.fullmatch(AZURE_ACCOUNT_NAME_PATTERN, account_name):
        return False, (
            "Error: account_name is not valid per Azure storage account naming rules "
            "(3-24 lowercase letters or digits, no dashes or special characters)."
        )
    return True, None

# =========================
# Existence-checking Validation Functions
# =========================

def validate_file_exists(file_path: Path) -> Tuple[bool, str]:
    """Check if file exists and is a file. Returns (exists, message)."""
    if not file_path.is_absolute():
        return False, f"File path must be absolute. Got: {file_path}"
    try:
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"
        if not file_path.is_file():
            return False, f"Path exists but is not a file: {file_path}"
    except Exception as e:
        return False, f"Error checking file existence: {e}"
    return True, "File exists and is a valid file."



def validate_dirpath_format_and_existence(
    dirpath: Path,
    must_exist: bool = True,
    on_error: Optional[Callable[[str], None]] = None
) -> Tuple[bool, str]:
    """
    Validate directory path format and existence. Returns (is_valid, message).
    If validation fails and on_error is provided, calls on_error(message).
    """
    # Type check and conversion
    if isinstance(dirpath, str):
        dirpath_str = dirpath
        dirpath = Path(dirpath)
    else:
        dirpath_str = str(dirpath)

    valid_format, format_msg = is_valid_dirpath(dirpath_str)
    if not valid_format:
        error_msg = f"Dirpath format invalid: {format_msg}"
        if on_error:
            on_error(error_msg)
        return False, error_msg

    if not dirpath.is_absolute():
        error_msg = f"Dirpath must be an absolute path. Got: {dirpath}"
        if on_error:
            on_error(error_msg)
        return False, error_msg

    try:
        if must_exist:
            if not dirpath.exists():
                error_msg = f"Directory not found. Dirpath: {dirpath}"
                if on_error:
                    on_error(error_msg)
                return False, error_msg
            if not dirpath.is_dir():
                error_msg = f"Path exists but is not a directory. Dirpath: {dirpath}"
                if on_error:
                    on_error(error_msg)
                return False, error_msg
    except Exception as e:
        error_msg = f"Error checking directory existence: {e}"
        if on_error:
            on_error(error_msg)
        return False, error_msg
    return True, "Directory exists and is a valid directory."








# def validate_dirpath_format_and_existence(
#     dirpath: Path,
#     must_exist: bool = True
# ) -> Tuple[bool, str]:
#     """Validate directory path format and existence. Returns (is_valid, message)."""
#     if not dirpath.is_absolute():
#         return False, f"Dirpath must be an absolute path. Got: {dirpath}"
#     try:
#         if must_exist:
#             if not dirpath.exists():
#                 return False, f"Directory not found. Dirpath: {dirpath}"
#             if not dirpath.is_dir():
#                 return False, f"Path exists but is not a directory. Dirpath: {dirpath}"
#     except Exception as e:
#         return False, f"Error checking directory existence: {e}"
#     return True, "Directory exists and is a valid directory."



def validate_file_path_and_existence(
    dirpath: Path,
    filename_including_extension: str,
    mandatory_extension: str,
    require_file_exists_for_read: bool = False,
    validate_dir_and_extension_only: bool = False
) -> Tuple[bool, str]:
    """Validate file path, filename, extension, and existence. Returns (is_valid, message)."""
    # Type check and conversion for dirpath
    if isinstance(dirpath, str):
        dirpath = Path(dirpath)
    valid_dir, dir_msg = validate_dirpath_format_and_existence(dirpath, must_exist=True)
    if not valid_dir:
        return False, f"Directory validation failed: {dir_msg}"
    if mandatory_extension and (not mandatory_extension.startswith(".") or len(mandatory_extension) < 2):
        return False, f"Error: mandatory_extension must be a non-empty string starting with a dot. Got: [{mandatory_extension}]"
    if validate_dir_and_extension_only:
        return True, "Directory and extension format validated only."
    for validator in [is_valid_ntfs_filename_format, is_valid_unix_filename_format]:
        valid, error = validator(filename_including_extension)
        if not valid:
            return False, f"Error: {error} The filename is [{filename_including_extension}]"
    if mandatory_extension and not filename_including_extension.endswith(mandatory_extension):
        return False, (
            f"Error: Invalid filename format, or incorrect filename extension. "
            f"The filename is [{filename_including_extension}]"
        )
    file_path = dirpath / filename_including_extension
    if require_file_exists_for_read:
        valid_file, file_msg = validate_file_exists(file_path)
        if not valid_file:
            return False, f"Error: Read file does not exist. [{file_path}] Details: {file_msg}"
    return True, "File path, filename, extension, and existence (if required) are valid."




# def validate_file_path_and_existence(
#     dirpath: Path,
#     filename_including_extension: str,
#     mandatory_extension: str,
#     require_file_exists_for_read: bool = False,
#     validate_dir_and_extension_only: bool = False
# ) -> Tuple[bool, str]:
#     """Validate file path, filename, extension, and existence. Returns (is_valid, message)."""
#     valid_dir, dir_msg = validate_dirpath_format_and_existence(dirpath, must_exist=True)
#     if not valid_dir:
#         return False, f"Directory validation failed: {dir_msg}"
#     if mandatory_extension and (not mandatory_extension.startswith(".") or len(mandatory_extension) < 2):
#         return False, f"Error: mandatory_extension must be a non-empty string starting with a dot. Got: [{mandatory_extension}]"
#     if validate_dir_and_extension_only:
#         return True, "Directory and extension format validated only."
#     for validator in [is_valid_ntfs_filename_format, is_valid_unix_filename_format]:
#         valid, error = validator(filename_including_extension)
#         if not valid:
#             return False, f"Error: {error} The filename is [{filename_including_extension}]"
#     if mandatory_extension and not filename_including_extension.endswith(mandatory_extension):
#         return False, (
#             f"Error: Invalid filename format, or incorrect filename extension. "
#             f"The filename is [{filename_including_extension}]"
#         )
#     file_path = dirpath / filename_including_extension
#     if require_file_exists_for_read:
#         valid_file, file_msg = validate_file_exists(file_path)
#         if not valid_file:
#             return False, f"Error: Read file does not exist. [{file_path}] Details: {file_msg}"
#     return True, "File path, filename, extension, and existence (if required) are valid."

# =========================
# Exception-throwing Wrappers
# =========================

def throw_if_ntfs_filename_format_invalid(filename: str) -> None:
    """Raise ValueError if NTFS filename format is invalid."""
    valid, errorMsg = is_valid_ntfs_filename_format(filename)
    if not valid:
        raise ValueError(f"Validation failed. Filename [{filename}] is problematic: {errorMsg}")

def throw_if_file_path_invalid_or_not_exists(file_path: Path) -> None:
    """Raise ValueError if file path is invalid or does not exist."""
    valid, message = validate_file_exists(file_path)
    if not valid:
        raise ValueError(f"File path validation failed: {message}")

def throw_if_file_path_ingredients_invalid_or_not_exists(
    dirpath: Path,
    filename_including_extension: str,
    mandatory_extension: str,
    require_file_exists_for_read: bool = False,
    validate_dir_and_extension_only: bool = False
) -> None:
    """Raise ValueError if file path ingredients are invalid or file does not exist."""
    valid, message = validate_file_path_and_existence(
        dirpath,
        filename_including_extension,
        mandatory_extension,
        require_file_exists_for_read,
        validate_dir_and_extension_only
    )
    if not valid:
        raise ValueError(f"File path validation failed: {message}")

def throw_if_dirpath_invalid_or_not_exists(
    dirpath: Path,
    must_exist: bool = True
) -> None:
    """Raise ValueError if directory path is invalid or does not exist."""
    valid, message = validate_dirpath_format_and_existence(dirpath, must_exist=must_exist)
    if not valid:
        raise ValueError(f"Directory path validation failed: {message}")

def throw_if_any_dirpath_invalid_or_not_exists(
    dirpaths: List[Path],
    must_exist: bool = True
) -> None:
    """
    Validates a list of directory paths.
    Raises ValueError with all errors concatenated if any path is invalid or does not exist.
    """
    errors = collect_dirpath_errors(dirpaths, must_exist=must_exist)
    if errors:
        raise ValueError(errors)

def throw_if_any_filename_invalid(
    filenames: List[str]
) -> None:
    """
    Validates a list of filenames.
    Raises ValueError with all errors concatenated if any filename is invalid.
    """
    errors = collect_filename_errors(filenames)
    if errors:
        raise ValueError(errors)

def throw_if_blob_name_is_invalid(blob_name: str) -> None:
    """
    Validates the blob_name name and raises an exception if invalid.
    :param blob_name: The name of the blob_name to validate.
    :raises AlertMessageError: If the blob_name name is invalid.
    """
    warning = warn_if_blob_name_is_invalid(blob_name)
    if warning:
        raise AlertMessageError(message=warning, error_type=LogEventType.ALERT_MESSAGE)

def throw_if_container_name_is_invalid(container_name: str) -> None:
    """
    Validates the container_name name and raises an exception if invalid.
    :param container_name: The name of the container_name to validate.
    :raises AlertMessageError: If the container_name name is invalid.
    """
    warning = warn_if_container_name_is_invalid(container_name)
    if warning:
        raise AlertMessageError(message=warning, error_type=LogEventType.ALERT_MESSAGE)

def throw_if_account_name_is_invalid(account_name: str) -> None:
    """
    Validates the storage_account_name name and raises an exception if invalid.
    :param account_name: The name of the storage_account_name to validate.
    :raises AlertMessageError: If the storage_account_name name is invalid.
    """
    warning = warn_if_account_name_is_invalid(account_name)
    if warning:
        raise AlertMessageError(message=warning, error_type=LogEventType.ALERT_MESSAGE)

def throw_if_any_parameter_is_invalid(
    account_name: str,
    container_name: str,
    blob_name: Optional[str] = None
) -> None:
    """
    Validates required Azure Storage parameters.
    Raises AlertMessageError if any parameter is invalid.
    - account_name and container_name are required.
    - blob_name is optional and only validated if provided.
    """
    _, account_warning = validate_azure_storage_account_name(account_name)
    if account_warning:
        raise AlertMessageError(account_warning)
    _, container_warning = validate_azure_storage_container_name(container_name)
    if container_warning:
        raise AlertMessageError(container_warning)
    if blob_name is not None:
        _, blob_warning = validate_azure_storage_blob_name(blob_name)
        if blob_warning:
            raise AlertMessageError(blob_warning)

# =========================
# Batch Error Collection Utilities
# =========================

def collect_dirpath_errors(
    dirpaths: List[Path],
    must_exist: bool = True
) -> str:
    """
    Validates a list of directory paths using throw_if_dirpath_invalid_or_not_exists.
    Collects all errors and returns them as a single concatenated string.
    If no errors, returns an empty string.
    """
    errors: List[str] = []
    for dirpath in dirpaths:
        try:
            throw_if_dirpath_invalid_or_not_exists(dirpath, must_exist=must_exist)
        except ValueError as ex:
            errors.append(f"{dirpath}: {ex}")
    return "\n".join(errors)

def collect_filename_errors(
    filenames: List[str]
) -> str:
    """
    Validates a list of filenames using is_valid_ntfs_filename_format and is_valid_unix_filename_format.
    Collects all errors and returns them as a single concatenated string.
    If no errors, returns an empty string.
    """
    errors: List[str] = []
    for filename in filenames:
        valid_ntfs, ntfs_msg = is_valid_ntfs_filename_format(filename)
        valid_unix, unix_msg = is_valid_unix_filename_format(filename)
        if not valid_ntfs:
            errors.append(f"{filename}: {ntfs_msg}")
        if not valid_unix:
            errors.append(f"{filename}: {unix_msg}")
    return "\n".join(errors)

# =========================
# File/Folder Path Utilities
# =========================

def parse_filename(url: str) -> str:
    """
    Given a URL, returns the file name only.
    Example:
      url = "https://data.zsunr.com/riders/json/zwift/1193.json"
      returns "1193.json"
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip('/')
    file = Path(path).name
    return file

def find_file_path_if_valid_and_exists(
    dirpath: Path,
    filename_including_extension: str,
    mandatory_extension: str,
    must_exist: bool
) -> Tuple[Optional[str], str]:
    """Get file path if valid and exists. Returns (filepath or None, message)."""
    valid_dir, dir_msg = validate_dirpath_format_and_existence(dirpath, must_exist=True)
    if not valid_dir:
        return None, f"Directory validation failed: {dir_msg}"
    valid_file, file_msg = validate_file_path_and_existence(
        dirpath,
        filename_including_extension,
        mandatory_extension,
        must_exist
    )
    if not valid_file:
        return None, f"File path validation failed: {file_msg}"
    return str(dirpath / filename_including_extension), "File path is valid."

def find_all_file_paths_in_folder(
    dirpath: Path,
    filenames_without_extension: Optional[List[str]],
    mandatory_extension: Optional[str] = None
) -> Tuple[Optional[List[str]], str]:
    """Get existing file paths in folder. Returns (list of filepaths or None, message)."""
    valid_dir, dir_msg = validate_dirpath_format_and_existence(dirpath, must_exist=True)
    if not valid_dir:
        return None, f"Directory validation failed: {dir_msg}"
    if mandatory_extension:
        if not mandatory_extension.startswith(".") or len(mandatory_extension) < 2:
            return None, (
                f"Error: mandatory_extension must be a non-empty string starting with a dot. "
                f"Got: [{mandatory_extension}]"
            )
    valid_filenames: List[str] = []
    if filenames_without_extension is not None:
        for fname in filenames_without_extension:
            valid_ntfs, _ = is_valid_ntfs_filename_format(fname)
            valid_unix, _ = is_valid_unix_filename_format(fname)
            if valid_ntfs and valid_unix:
                valid_filenames.append(fname)
    try:
        all_file_paths = [
            str(f) for f in dirpath.iterdir()
            if f.is_file() and (not mandatory_extension or f.name.endswith(mandatory_extension))
        ]
    except Exception as e:
        return None, f"Error reading directory contents: {e}"
    if not valid_filenames:
        return all_file_paths, "Returned all files matching extension (no filename filtering applied)."
    filtered_paths = [
        file_path for file_path in all_file_paths
        if Path(file_path).stem in valid_filenames
    ]
    return filtered_paths, "Returned files matching valid filenames and extension."