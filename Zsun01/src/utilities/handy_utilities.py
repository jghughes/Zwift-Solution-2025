import os
from typing import Dict, cast, Optional, List
from jgh_read_write import read_text, read_filepath_as_text, help_select_filepaths_in_folder
from jgh_serialization import JghSerialization
from zsun_rider_dto import ZsunRiderDTO
from zwiftpower_curves_of_bestpower_dto import ZwiftPowerCurvesOfBestPowerDTO
from zwiftpower_curve_of_90day_bestpower_dto import ZwiftPowerCurveOf90DayBestPowerDTO
from zsun_rider_item import ZsunRiderItem
from zwiftpower_curve_of_90day_bestpower_item import FlattenedVersionOfCurveOf90DayBestPowerItem
from zwiftracingapp_profile_dto import *
from zwiftpower_profile_dto import ZwiftPowerProfileDTO
from zwift_profile_dto import ZwiftProfileDTO
from collections import defaultdict
from zwiftpower_profile_item import ZwiftPowerProfileItem
from zwiftracingapp_profile_item import ZwiftRacingAppProfileItem, PowerItem, RaceDetailsItem
from zwift_profile_item import ZwiftProfileItem

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

def get_betel_zwift_ids() -> List[str]:

    file_name = "betel_rider_profiles.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    riders = read_dict_of_zsunrider_items(file_name, dir_path)

    # extract list of zwiftIds from the riders
    answer = [str(rider.zwift_id) for rider in riders.values()]

    return answer

def get_betel(id : int) -> ZsunRiderItem:
    file_name = "betel_rider_profiles.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    riders = read_dict_of_zsunrider_items(file_name, dir_path)
    # extract list of zwiftIds from the riders
    answer = riders[str(id)]
    return answer

def get_zsun_rider(id : int) -> ZsunRiderItem:
    file_name = "betel_rider_profiles.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    riders = read_dict_of_zsunrider_items(file_name, dir_path)
    # extract list of zwiftIds from the riders
    answer = riders[str(id)]
    return answer

def read_dict_of_zsunrider_items(file_name: str, dir_path: str) -> Dict[str, ZsunRiderItem]:
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

    answer = JghSerialization.validate(inputjson, Dict[str, ZsunRiderDTO])
    answer = cast(Dict[str, ZsunRiderDTO], answer)

    return {
        key: ZsunRiderItem.from_dataTransferObject(dto)
        for key, dto in answer.items()
    }

def read_dict_of_90day_bestpower_items(file_name: str, dir_path: str) -> Dict[str, FlattenedVersionOfCurveOf90DayBestPowerItem]:
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

    answer = JghSerialization.validate(inputjson, Dict[str, ZwiftPowerCurveOf90DayBestPowerDTO])
    answer = cast(Dict[str, ZwiftPowerCurveOf90DayBestPowerDTO], answer)

    return {
        key: FlattenedVersionOfCurveOf90DayBestPowerItem.from_dataTransferObject(dto)
        for key, dto in answer.items()
    }

def write_dict_of_90day_bestpower_items(data: Dict[str, FlattenedVersionOfCurveOf90DayBestPowerItem], file_name: str, dir_path: str) -> None:
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

def read_many_zwift_profile_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> defaultdict[str, ZwiftProfileItem]:
    
    answer: defaultdict[str, ZwiftProfileItem] = defaultdict(ZwiftProfileItem)

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")

        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftProfileDTO)
            dto = cast(ZwiftProfileDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        item = ZwiftProfileItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_many_zwiftracingapp_profile_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> defaultdict[str, ZwiftRacingAppProfileItem]:
    
    answer: defaultdict[str, ZwiftRacingAppProfileItem] = defaultdict(ZwiftRacingAppProfileItem)

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppProfileDTO)
            dto = cast(ZwiftRacingAppProfileDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        item = ZwiftRacingAppProfileItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_many_zwiftpower_profile_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> defaultdict[str, ZwiftPowerProfileItem]:
    answer: defaultdict[str, ZwiftPowerProfileItem] = defaultdict(ZwiftPowerProfileItem)

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")

    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerProfileDTO)
            dto = cast(ZwiftPowerProfileDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        item = ZwiftPowerProfileItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_many_zwiftpower_bestpower_files_in_folder(riderIDs: Optional[list[str]], dir_path: str) -> defaultdict[str, FlattenedVersionOfCurveOf90DayBestPowerItem]:

    answer: defaultdict[str, FlattenedVersionOfCurveOf90DayBestPowerItem] = defaultdict(FlattenedVersionOfCurveOf90DayBestPowerItem)

    file_paths = help_select_filepaths_in_folder(riderIDs,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerCurvesOfBestPowerDTO)
            dto = cast(ZwiftPowerCurvesOfBestPowerDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        answer[zwift_id] = FlattenedVersionOfCurveOf90DayBestPowerItem.from_ZwiftPower90DayBestDataDTO(dto)

    return answer

def main():

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"


    zsun_raw_cp_dict_for_betel = read_many_zwiftracingapp_profile_files_in_folder(get_betel_zwift_ids(),INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    jgh_cp_dict = read_dict_of_90day_bestpower_items(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_dict_of_90day_bestpower_items(combined_raw_cp_dict_for_betel, "extracted_input_cp_data_for_betel.json", INPUT_CP_DATA_DIRPATH)

def main02():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    dict_of_zwift_profiles = read_many_zwift_profile_files_in_folder(None, ZWIFT_PROFILES_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwift_profiles)} zwift profile items")

    dict_of_zwiftracingapp_profiles = read_many_zwiftracingapp_profile_files_in_folder(None, ZWIFTRACINGAPP_PROFILES_DIRPATH)
    logger.info (f"Imported {len(dict_of_zwiftracingapp_profiles)} zwiftracingapp profile items")

    dict_of_zwiftpower_profiles = read_many_zwiftpower_profile_files_in_folder(None, ZWIFTPOWER_PROFILES_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwiftpower_profiles)} zwiftpower profile items")

    dict_of_zwiftpower_90day_bestpower = read_many_zwiftpower_bestpower_files_in_folder(None, ZWIFTPOWER_GRAPHS_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwiftpower_90day_bestpower)} zwiftpower bestpower info items")

def main03():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"


    dict_of_zwiftracingapp_profiles = read_many_zwiftracingapp_profile_files_in_folder(None, ZWIFTRACINGAPP_PROFILES_DIRPATH)

    logger.info (f"Imported {len(dict_of_zwiftracingapp_profiles)} zwiftracingapp profile items")
    for zwift_id, item in dict_of_zwiftracingapp_profiles.items():
        if not item.poweritem:  # Check if poweritem is None or evaluates to False
            logger.warning(f"{zwift_id} {item.fullname} has no poweritem. Initializing with default values.")
            item.poweritem = PowerItem()  # Initialize with a default PowerItem instance       
        logger.info(f"{zwift_id} {item.fullname} zFTP = {round(item.zp_FTP)} Watts, CP = {round(item.poweritem.CP)} Watts, AWC = {round(item.poweritem.AWC/1000.0)} kJ")


if __name__ == "__main__":
    main03()