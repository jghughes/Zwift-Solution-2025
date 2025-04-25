import os
from typing import Dict, cast, Optional, List
from jgh_read_write import read_text, read_filepath_as_text, help_select_filepaths_in_folder
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDTO
from zwiftpower_90day_best_dto import ZwiftPowerImportDTO, ZwiftPower90DayBestGraphDTO
from zwiftrider_related_items import ZwiftRiderItem, ZwiftPower90DayBestGraphItem
from zwiftracing_dto import ZwiftRacingAppDTO


import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

def get_betel_zwift_ids() -> List[str]:

    file_name = "betel_rider_profiles.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    riders = read_dict_of_zwiftriders(file_name, dir_path)

    # extract list of zwiftIds from the riders
    answer = [str(rider.zwiftid) for rider in riders.values()]

    return answer

def get_betel(id : int) -> ZwiftRiderItem:
    """
    Retrieve a specific Zwift rider by their ID from the JSON file and convert it to a ZwiftRiderItem instance.
    Args:
        id (int): The ID of the rider to retrieve.
    Returns:
        ZwiftRiderItem: The ZwiftRiderItem instance for the specified rider.
    """
    file_name = "betel_rider_profiles.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    riders = read_dict_of_zwiftriders(file_name, dir_path)
    # extract list of zwiftIds from the riders
    answer = riders[str(id)]
    return answer

def get_zwift_rider(id : int) -> ZwiftRiderItem:
    """
    Retrieve a specific Zwift rider by their ID from the JSON file and convert it to a ZwiftRiderItem instance.
    Args:
        id (int): The ID of the rider to retrieve.
    Returns:
        ZwiftRiderItem: The ZwiftRiderItem instance for the specified rider.
    """
    file_name = "betel_rider_profiles.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    riders = read_dict_of_zwiftriders(file_name, dir_path)
    # extract list of zwiftIds from the riders
    answer = riders[str(id)]
    return answer

def read_dict_of_zwiftriders(file_name: str, dir_path: str) -> Dict[str, ZwiftRiderItem]:
    """
    Retrieve all Zwift riders from a JSON file and convert them to ZwiftRiderItem instances.
    The data transfer object is ZwiftRiderDTO.

    Args:
        file_name (str): The name of the file to read.
        dir_path (str): The directory path where the file is located.

    Returns:
        Dict[str, ZwiftRiderItem]: A dictionary of ZwiftRiderItem instances.
    """

    # Raise an error if dir_path parameter is not minimally satisfactory

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    # Raise an error if the directory does not exist
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    # do work

    inputjson = read_text(dir_path, file_name)

    answer = JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDTO])
    answer = cast(Dict[str, ZwiftRiderDTO], answer)

    return {
        key: ZwiftRiderItem.from_dataTransferObject(dto)
        for key, dto in answer.items()
    }

def read_dict_of_cpdata(file_name: str, dir_path: str) -> Dict[str, ZwiftPower90DayBestGraphItem]:
    """
    Retrieve a compndium of Zwift riders critical power data from a JSON file 
    in thr format of a duct and convert them to a dict of ZwiftPower90DayBestGraphItem instances.
    The key of both dicts is zwiftID. The data transfer object is ZwiftPower90DayBestGraphDTO.

    Args:
        file_name (str): The name of the file to read.
        dir_path (str): The directory path where the file is located.

    Returns:
        Dict[str, ZwiftPower90DayBestGraphItem]: A dictionary of ZwiftPower90DayBestGraphItem instances.
    """
    # Raise an error if dir_path parameter is not minimally satisfactory

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    # Raise an error if the directory does not exist
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    # do work

    inputjson = read_text(dir_path, file_name)

    answer = JghSerialization.validate(inputjson, Dict[str, ZwiftPower90DayBestGraphDTO])
    answer = cast(Dict[str, ZwiftPower90DayBestGraphDTO], answer)

    return {
        key: ZwiftPower90DayBestGraphItem.from_dataTransferObject(dto)
        for key, dto in answer.items()
    }

def write_dict_of_cpdata(data: Dict[str, ZwiftPower90DayBestGraphItem], file_name: str, dir_path: str) -> None:
    """
    Serialize a dictionary of ZwiftPower90DayBestGraphItem instances and write it to a JSON file.

    Args:
        data (Dict[str, ZwiftPower90DayBestGraphItem]): The data to serialize.
        file_name (str): The name of the file to write.
        dir_path (str): The directory path where the file will be written.
    """
    # Raise an error if dir_path parameter is not minimally satisfactory

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    # Raise an error if the directory does not exist
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    # do work

    serialized_data = JghSerialization.serialise(data)

    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(serialized_data)

    logger.debug(f"File saved : {file_name}")

def read_many_zwiftracing_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> Dict[str, ZwiftPower90DayBestGraphItem]:
    """
    Retrieve multiple ZwiftRacing JSON data files from a directory and convert them into a dictionary
    of `ZwiftPower90DayBestGraphItem` instances. The key of the dictionary is the `zwiftID` extracted
    from the filename (without the extension).

    If `riderIDs` is provided, only files matching the specified rider IDs are processed. If `riderIDs`
    is `None`, all JSON files in the directory are processed.

    Args:
        riderIDs (Optional[list[str]]): A list of rider IDs to filter the files. If `None`, all files
                                        in the directory are processed.
        dir_path (str): The directory path where the JSON files are located.

    Returns:
        Dict[str, ZwiftPower90DayBestGraphItem]: A dictionary where the keys are `zwiftID` strings
                                                and the values are `ZwiftPower90DayBestGraphItem` instances.

    Raises:
        ValueError: If `dir_path` is not a valid non-empty string.
        FileNotFoundError: If the specified directory does not exist.

    Example:
        >>> riderIDs = ["1193", "5134"]
        >>> dir_path = "/path/to/zwiftracing/files"
        >>> answer = read_many_zwiftracing_files_in_folder(riderIDs, dir_path)
        >>> print(answer)
        {
            "1193": ZwiftPower90DayBestGraphItem(...),
            "5134": ZwiftPower90DayBestGraphItem(...)
        }
    """
    
    answer: Dict[str, ZwiftPower90DayBestGraphItem] = {}

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)

    file_count = 0
    error_count = 0

    for file_path in file_paths:

        inputjson = read_filepath_as_text(file_path)

        file_count += 1

        try:
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppDTO)
            dto = cast(ZwiftRacingAppDTO, dto)
        except Exception:
            error_count += 1
            logger.error(f"{error_count} serialisation error. Skipping file:- |n{file_path}")
            continue

        file_name = os.path.basename(file_path)

        zwiftID, _ = os.path.splitext(file_name)  # Safely remove the extension

        logger.debug(f"{file_count} processing : {file_name}")

        answer[zwiftID] = ZwiftPower90DayBestGraphItem.from_zwift_racing_app_DTO(dto)

    return answer





















    # Raise an error if dir_path parameter is not minimally satisfactory

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    # Raise an error if the directory does not exist
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    answer: Dict[str, ZwiftPower90DayBestGraphItem] = {}

    file_count = 0
    error_count = 0

    for entry in os.listdir(dir_path):

        # Check if the entry is a valid JSON file. if not skip it.
        if not entry.endswith(".json"):
            continue

        file_name = entry

        # Skip the file if riderIDs is provided but is empty
        if riderIDs is not None and not riderIDs:
            continue

        # Skip the file if riderIDs is provided and the file name (without .json) is not in riderIDs
        if riderIDs and file_name[:-5] not in riderIDs:
            continue
    
        # Go ahead and process the file


        file_path = os.path.join(dir_path, file_name)

        if os.path.isfile(file_path):

            inputjson = read_text(dir_path, file_name)

            file_count += 1

            logger.debug(f"{file_count} processing : {file_name}")

            try:

                dto = JghSerialization.validate(inputjson, ZwiftRacingAppDTO)

            except Exception:
                error_count += 1
                logger.error(f"     {error_count} serialisation error. Skipping file: {file_name}")
                continue

            dto = cast(ZwiftRacingAppDTO, dto)

            if dto.riderId:
                answer[dto.riderId] = ZwiftPower90DayBestGraphItem.from_zwift_racing_app_DTO(
                    dto
                )

    return dict(sorted(answer.items(), key=lambda item: int(item[0])))

def read_many_zwiftpower_profile_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> Dict[str, ZwiftRiderItem]:
    """
    Retrieve multiple ZwiftPower CP graph JSON files from a directory and convert them into a dictionary
    of `ZwiftPower90DayBestGraphItem` instances. The key of the dictionary is the `zwiftID` extracted
    from the filename (without the extension).

    If `riderIDs` is provided, only files matching the specified rider IDs are processed. If `riderIDs`
    is `None`, all JSON files in the directory are processed.

    Args:
        riderIDs (Optional[list[str]]): A list of rider IDs to filter the files. If `None`, all files
                                        in the directory are processed.
        dir_path (str): The directory path where the JSON files are located.

    Returns:
        Dict[str, ZwiftPower90DayBestGraphItem]: A dictionary where the keys are `zwiftID` strings
                                                and the values are `ZwiftPower90DayBestGraphItem` instances.

    Raises:
        ValueError: If `dir_path` is not a valid non-empty string.
        FileNotFoundError: If the specified directory does not exist.

    Example:
        >>> riderIDs = ["1193", "5134"]
        >>> dir_path = "/path/to/zwiftpower/files"
        >>> answer = read_many_zwiftpower_graph_files_in_folder(riderIDs, dir_path)
        >>> print(answer)
        {
            "1193": ZwiftPower90DayBestGraphItem(...),
            "5134": ZwiftPower90DayBestGraphItem(...)
        }
    """

    answer: Dict[str, ZwiftRiderItem] = {}

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)

    file_count = 0
    error_count = 0

    for file_path in file_paths:

        inputjson = read_filepath_as_text(file_path)

        file_count += 1

        try:
            dto = JghSerialization.validate(inputjson, ZwiftRiderDTO)
            dto = cast(ZwiftRiderDTO, dto)
        except Exception:
            error_count += 1
            logger.error(f"{error_count} serialisation error. Skipping file:- |n{file_path}")
            continue


        file_name = os.path.basename(file_path)

        zwiftID, _ = os.path.splitext(file_name)  # Safely remove the extension

        logger.debug(f"{file_count} processing : {file_name}")

        answer[zwiftID] = ZwiftRiderItem.from_dataTransferObject(dto)

    return answer

def read_many_zwiftpower_graph_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> Dict[str, ZwiftPower90DayBestGraphItem]:
    """
    Retrieve multiple ZwiftPower CP graph JSON files from a directory and convert them into a dictionary
    of `ZwiftPower90DayBestGraphItem` instances. The key of the dictionary is the `zwiftID` extracted
    from the filename (without the extension).

    If `riderIDs` is provided, only files matching the specified rider IDs are processed. If `riderIDs`
    is `None`, all JSON files in the directory are processed.

    Args:
        riderIDs (Optional[list[str]]): A list of rider IDs to filter the files. If `None`, all files
                                        in the directory are processed.
        dir_path (str): The directory path where the JSON files are located.

    Returns:
        Dict[str, ZwiftPower90DayBestGraphItem]: A dictionary where the keys are `zwiftID` strings
                                                and the values are `ZwiftPower90DayBestGraphItem` instances.

    Raises:
        ValueError: If `dir_path` is not a valid non-empty string.
        FileNotFoundError: If the specified directory does not exist.

    Example:
        >>> riderIDs = ["1193", "5134"]
        >>> dir_path = "/path/to/zwiftpower/files"
        >>> result = read_many_zwiftpower_graph_files_in_folder(riderIDs, dir_path)
        >>> print(result)
        {
            "1193": ZwiftPower90DayBestGraphItem(...),
            "5134": ZwiftPower90DayBestGraphItem(...)
        }
    """



    answer: Dict[str, ZwiftPower90DayBestGraphItem] = {}

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)

    file_count = 0
    error_count = 0

    for file_path in file_paths:

        inputjson = read_filepath_as_text(file_path)

        file_count += 1

        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerImportDTO)
            dto = cast(ZwiftPowerImportDTO, dto)
        except Exception:
            error_count += 1
            logger.error(f"{error_count} serialisation error. Skipping file:- |n{file_path}")
            continue

        file_name = os.path.basename(file_path)

        zwiftID, _ = os.path.splitext(file_name)  # Safely remove the extension

        logger.debug(f"{file_count} processing : {file_name}")

        answer[zwiftID] = ZwiftPower90DayBestGraphItem.from_ZwiftPower90DayBestDataDTO(dto)

    return answer

def main():

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"


    zsun_raw_cp_dict_for_betel = read_many_zwiftracing_files_in_folder(get_betel_zwift_ids(),INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    jgh_cp_dict = read_dict_of_cpdata(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_dict_of_cpdata(combined_raw_cp_dict_for_betel, "extracted_input_cp_data_for_betel.json", INPUT_CP_DATA_DIRPATH)

def main02():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO


    INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"
    _ = read_many_zwiftpower_graph_files_in_folder(get_betel_zwift_ids(), INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH)

if __name__ == "__main__":
    main02()