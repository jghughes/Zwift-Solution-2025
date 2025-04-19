import os
from typing import Dict, cast, Optional
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDTO
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDTO
from zwiftpower_cp_graph_dto import ZwiftPowerCpGraphDTO
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem
from zwiftracing_dto import ZwiftRacingAppPostDTO

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO


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

    dto_dict = JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDTO])
    dto_dict = cast(Dict[str, ZwiftRiderDTO], dto_dict)

    return {
        key: ZwiftRiderItem.from_dataTransferObject(dto)
        for key, dto in dto_dict.items()
    }

def read_dict_of_cpdata(file_name: str, dir_path: str) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve a compndium of Zwift riders critical power data from a JSON file 
    in thr format of a duct and convert them to a dict of ZwiftRiderCriticalPowerItem instances.
    The key of both dicts is zwiftID. The data transfer object is ZwiftRiderCriticalPowerDTO.

    Args:
        file_name (str): The name of the file to read.
        dir_path (str): The directory path where the file is located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
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

    dto_dict = JghSerialization.validate(inputjson, Dict[str, ZwiftRiderCriticalPowerDTO])
    dto_dict = cast(Dict[str, ZwiftRiderCriticalPowerDTO], dto_dict)

    return {
        key: ZwiftRiderCriticalPowerItem.from_dataTransferObject(dto)
        for key, dto in dto_dict.items()
    }

def write_dict_of_cpdata(data: Dict[str, ZwiftRiderCriticalPowerItem], file_name: str, dir_path: str) -> None:
    """
    Serialize a dictionary of ZwiftRiderCriticalPowerItem instances and write it to a JSON file.

    Args:
        data (Dict[str, ZwiftRiderCriticalPowerItem]): The data to serialize.
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

def read_many_zwiftracing_files_in_folder(riderIDs: Optional[list[str]], dir_path: Optional[str]) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve many individual ZwiftRacing JSON data files in a directory and convert them
    to a dict of ZwiftRiderCriticalPowerItem instances. The key of the dicts is zwiftID.  
    The data transfer object is ZwiftRacingAppPostDTO.

    Args:
        dir_path (str): The directory path where the files are located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """

    # Raise an error if dir_path parameter is not minimally satisfactory

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    # Raise an error if the directory does not exist
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    result: Dict[str, ZwiftRiderCriticalPowerItem] = {}

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

                dto = JghSerialization.validate(inputjson, ZwiftRacingAppPostDTO)

            except Exception:
                error_count += 1
                logger.error(f"     {error_count} serialisation error. Skipping file: {file_name}")
                continue

            dto = cast(ZwiftRacingAppPostDTO, dto)

            if dto.riderId:
                result[dto.riderId] = ZwiftRiderCriticalPowerItem.from_zwift_racing_app_DTO(
                    dto
                )

    return dict(sorted(result.items(), key=lambda item: int(item[0])))

def read_many_zwiftpower_profile_files_in_folder(riderIDs: Optional[list[str]], dir_path: Optional[str]) -> Dict[str, ZwiftRiderItem]:
    """
    Retrieve many individual ZwiftPower profile JSON files in a directory and convert them
    to a dict of ZwiftRiderItem instances. If riderIDs is None, all files are processed.
    Otherwise, only files with filenames the same as in riderIDs are processed. The key 
    of the dict is zwiftID. The data transfer object is ZwiftRacingAppPostDTO.

    Args:
        dir_path (str): The directory path where the files are located.

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

    result: Dict[str, ZwiftRiderItem] = {}

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

            # logger.debug(f"{file_count} processing : {file_name}")

            try:

                dto = JghSerialization.validate(inputjson, ZwiftRiderDTO)

            except Exception:
                error_count += 1
                logger.error(f"     {error_count} serialisation error. Skipping file: {file_name}")
                continue

            dto = cast(ZwiftRiderDTO, dto)

            if dto.zwiftid:
                result[str(dto.zwiftid)] = ZwiftRiderItem.from_dataTransferObject(dto)

    return dict(sorted(result.items(), key=lambda item: int(item[0])))

def read_many_zwiftpower_cp_graph_files_in_folder(riderIDs: Optional[list[str]], dir_path: Optional[str]) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve many individual ZwiftPower cp_power_graph JSON files in a directory and convert them
    to a dict of ZwiftRiderCriticalPowerItem instances. If "riderIDs" parameter is None, all files 
    in the specified directory are processed.
    Otherwise, only files with filenames the same as in riderIDs are processed. The key 
    of the resulting dict of items the aforementioned filename/zwiftID. 
    The data transfer object used to read the JSON from ZwiftPower is ZwiftPowerCpGraphDTO.

    Args:
        riderIDs (Optional[list[str]]): List of rider IDs to filter, or None to process all files.
        dir_path (str): The directory path where the files are located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """
    # Raise an error if dir_path parameter is not minimally satisfactory

    if not dir_path:
        raise ValueError("dir_path must be a valid string.")

    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")

    # Raise an error if the directory does not exist
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    result: Dict[str, ZwiftRiderCriticalPowerItem] = {}

    # exit if riderIDs list is provided but is inadvertently empty
    if riderIDs is not None and not riderIDs:
        return result

    file_count = 0
    error_count = 0
    logger.debug(f"\nProcessing zwift riders: \n{riderIDs}\n\n")

    for entry in os.listdir(dir_path):

        # Check if the entry is a valid JSON file. if not its a subdir or an irrelevant file. hop over it.
        if not entry.endswith(".json"):
            continue

        file_name = entry

        # If a list of riderIDs is provided, check if the file name (without .json) is on the list. if not, hop over it.
        if riderIDs and file_name[:-5] not in riderIDs:
            continue
    
        # Go ahead and process the file
        logger.debug(f"\nAh ha. Success. We have found a file. On we go. File_name is:-\n{file_name} ")

        file_path = os.path.join(dir_path, file_name)
        logger.debug(f"\nAh ha. Success. We have found a file_path. On we go. File_path is:-\n{file_path} ")

        if os.path.isfile(file_path):

            logger.debug(f"\nReading the file.....")

            inputjson = read_text(dir_path, file_name)

            logger.debug(f"\n|nRaw input JSON for Richard Mann: \n\n{inputjson}\n\n")

            file_count += 1
            # logger.debug(f"{file_count} processing : {file_name}")

            try:

                dto = JghSerialization.validate(inputjson, ZwiftPowerCpGraphDTO)

                logger.debug(f"\n\nValidated ZwiftPowerCpGraphDTO for Richard Mann: \n\n{dto}\n\n")


            except Exception:
                error_count += 1
                logger.error(f"     {error_count} serialisation error. Skipping file: {file_name}")
                continue

            dto = cast(ZwiftPowerCpGraphDTO, dto)

            if file_name[:-5]:
                result[file_name[:-5]] = ZwiftRiderCriticalPowerItem.from_zwiftpower_cp_graph_DTO(dto)
                logger.debug(f"\n\nMapped ZwiftRiderCriticalPowerItem for Richard Mann: \n\n{dto}\n\n")


    return dict(sorted(result.items(), key=lambda item: int(item[0])))

def main():

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"

    riderIDs =["1193", "5134", "9011", "11526", "183277", "383480", "384442", "480698", "1884456", "1024413", "991817", "1713736", "2398312", "2508033"  "2682791", "3147366", "5421258", "5490373", "5530045", "5569057", "6142432"] 

    zsun_raw_cp_dict_for_betel = read_many_zwiftracing_files_in_folder(riderIDs,INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

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

    INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"
    _ = read_many_zwiftpower_cp_graph_files_in_folder(["1193"], INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH)

if __name__ == "__main__":
    main02()