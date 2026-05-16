import os
import json

from pathlib import Path
from typing import Callable, Dict, Optional, Type, TypeVar
from jgh_exceptions import AlertMessageError
from jgh_path_helpers import find_all_file_paths_in_folder, throw_if_dirpath_invalid_or_not_exists
from jgh_read_write import read_text_from_path
from zwift_id_base import HasZwiftID
from zwift_item import ZwiftItem
# from zwiftpower_profile_item import ZwiftPowerProfileItem
# from zwiftpower_profile_dto import ZwiftPowerProfileDTO
from zwiftpower_graph_watts_dto import ZwiftPowerGraphWattsDTO
from zwift_dto import ZwiftDTO
from zwiftracingapp_item import ZwiftRacingAppItem
from zwiftracingapp_dto import ZwiftRacingAppDTO
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem
from pydantic import BaseModel

import logging
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING
setup_json_logging(DIRPATH_LOGGING)
logger = logging.getLogger()


T = TypeVar("T", bound=HasZwiftID)
DTO = TypeVar("DTO", bound=BaseModel)

def read_file_named_by_zwiftId_to_tuple_sync(
    file_path: str,
    data_transfer_class: Type[DTO],
    function_to_translate_from_dto_to_corresponding_item: Callable[[DTO], T]
) -> tuple[Optional[str], Optional[T], Optional[str]]:
    """
    Reads a JSON file whose filename (without extension) is a Zwift ID, validates and deserializes it into a DTO,
    then converts it to a domain item. The Zwift ID is extracted from the filename and assigned to the resulting item.

    Args:
        file_path (str): Path to the JSON file. The filename (without extension) must be the Zwift ID.
        data_transfer_class (Type[DTO]): DTO class type for validation/deserialization.
        function_to_translate_from_dto_to_corresponding_item (Callable[[DTO], T]): Function to convert DTO to domain item.

    Returns:
        tuple:
            zwift_id (Optional[str]): Zwift ID extracted from filename, or None if error.
            item (Optional[T]): The constructed domain item with zwift_id set, or None if error.
            error_message (Optional[str]): Error message if reading or validation fails, otherwise None.

    Notes:
        - If reading or validation fails, zwift_id and item are None and error_message contains details.
        - The function does not log errors; error handling is delegated to the caller.
    """
    file_name = os.path.basename(file_path)
    try:
        inputjson = read_text_from_path(Path(file_path))
    except Exception as err:
        return None, None, f"Failed to read file: {file_name}. Error: {err}"

    try:
        something = json.loads(inputjson)
        dto = data_transfer_class.model_validate(something, strict=True)
        # dto = JghSerialization.validate(inputjson, data_transfer_class)
        # dto = cast(DTO, dto)
    except Exception as err:
        return None, None, f"Validation failed for file: {file_name}. Error: {err}"

    # Extract the Zwift ID from the filename by removing its extension.
    # For example, "1234567.json" yields zwift_id = "1234567".
    filename_fragment, _ = os.path.splitext(file_name)
    item = function_to_translate_from_dto_to_corresponding_item(dto)
    item.zwift_id = filename_fragment
    return filename_fragment, item, None

def read_many_files_named_by_zwiftId_to_dict_sync(
    dirpath: Path,
    specified_zwiftIDs: Optional[list[str]],
    data_transfer_class: Type[DTO],
    corresponding_item_class: Type[T],
    function_to_translate_from_dto_to_corresponding_item: Callable[[DTO], T]
) -> dict[str, T]:
    """
    Reads JSON files from a directory where each filename (without extension) represents a Zwift ID.
    Validates and deserializes each file into a DTO, then converts it to a domain item.
    Each error encountered during reading or validation is logged individually using structured logging.

    Args:
        dirpath (Path): Directory containing the JSON files.
        specified_zwiftIDs (Optional[list[str]]): List of Zwift IDs to filter files, or None to include all.
        data_transfer_class (Type[DTO]): DTO class type for validation/deserialization.
        corresponding_item_class (Type[T]): Domain item class type.
        function_to_translate_from_dto_to_corresponding_item (Callable[[DTO], T]): Function to convert DTO to domain item.

    Returns:
        dict[str, T]: Dictionary mapping Zwift ID (str) to domain item (T) for successfully processed files.

    Raises:
        AlertMessageError: If the directory is invalid or no files are found.

    Notes:
        - Only files with valid Zwift IDs and passing validation are included in the result.
        - Each file error is logged individually via log_event.
        - A summary log entry is emitted after processing all files.
    """
    throw_if_dirpath_invalid_or_not_exists(dirpath)

    answer: dict[str, T] = {}

    file_paths, message = find_all_file_paths_in_folder(dirpath, specified_zwiftIDs, ".json")

    if file_paths is None:
        log_event(
            logger,
            message=f"File discovery failed: {message}",
            level=logging.ERROR
        )
        raise AlertMessageError(message=f"File discovery failed: {message}")
    elif not file_paths:
        log_event(
            logger,
            message=f"No JSON files found in directory: {dirpath}. Details: {message}",
            level=logging.ERROR
        )
        return {}

    for file_path in file_paths:
        zwift_id, item, error = read_file_named_by_zwiftId_to_tuple_sync(file_path, data_transfer_class, function_to_translate_from_dto_to_corresponding_item)
        if error is not None:
            log_event(
                logger,
                message=error,
                level=logging.ERROR
            )
        elif zwift_id and item:
            answer[zwift_id] = item

    log_event(
        logger,
        message=f"Imported {len(answer)} profiles from {len(file_paths)} files. Skipped {len(file_paths) - len(answer)} bad files.",
        level=logging.INFO
    )
    return answer

def read_zwiftdto_files_to_item_dict_sync(dirpath: Path, specified_zwiftIDs: Optional[list[str]]) -> Dict[str, ZwiftItem]:
    return read_many_files_named_by_zwiftId_to_dict_sync(dirpath, 
                                                         specified_zwiftIDs, 
                                                         ZwiftDTO, 
                                                         ZwiftItem, 
                                                         ZwiftItem.from_dataTransferObject)

def read_zwiftracingappdto_files_to_item_dict_sync(dirpath: Path, specified_zwiftIDs: Optional[list[str]]) -> Dict[str, ZwiftRacingAppItem]:
    return read_many_files_named_by_zwiftId_to_dict_sync(dirpath, 
                                                         specified_zwiftIDs, 
                                                         ZwiftRacingAppDTO, 
                                                         ZwiftRacingAppItem, 
                                                         ZwiftRacingAppItem.from_dataTransferObject)

def read_zwiftpower90daywattsdto_files_to_item_dict_sync(dirpath: Path, specified_zwiftIDs: Optional[list[str]]) -> Dict[str, ZwiftPowerFlattened90dayWattsItem]:
    return read_many_files_named_by_zwiftId_to_dict_sync(dirpath, 
                                                         specified_zwiftIDs, 
                                                         ZwiftPowerGraphWattsDTO, 
                                                         ZwiftPowerFlattened90dayWattsItem, 
                                                         ZwiftPowerFlattened90dayWattsItem.from_ZwiftPowerWattsDTO)

