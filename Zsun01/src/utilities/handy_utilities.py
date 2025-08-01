import os
from typing import Dict, cast, Optional, List, DefaultDict
from collections import defaultdict
from jgh_read_write import read_text, read_filepath_as_text, help_select_filepaths_in_folder
from jgh_serialization import JghSerialization
from zwift_rider_particulars_dto import ZwiftDTO
from zwift_rider_particulars_item import ZwiftItem
from zwiftpower_watts_ordinates_dto import ZwiftPowerWattsDTO
from zwiftpower_rider_particulars_dto import ZwiftPowerDTO
from zwiftpower_rider_particulars_item import ZwiftPowerItem
from zwiftracingapp_rider_particulars_dto import *
from zwiftracingapp_rider_particulars_item import ZwiftRacingAppItem
from regression_modelling_dto import RegressionModellingDTO
from regression_modelling_item import RegressionModellingItem
from zsun_watts_properties_dto import ZsunWattsDTO
from zsun_watts_properties_item import ZsunWattsItem
from zsun_rider_dto import ZsunDTO
from zsun_rider_item import ZsunItem

import logging
from jgh_logging import jgh_configure_logging

#functions used to read many files in a folder and return a dictionary of items. used to read the thousands of raw zwift profiles, zwiftracingapp profiles, zwiftpower profiles, and zwiftpower best power files obtained by DaveK for Brute. used in class RepositoryForScrapedDataFromDaveK

def read_zwift_files(
    file_names: Optional[list[str]],
    dir_path: str,
    logger: logging.Logger,
    log_level: int = logging.INFO
) -> DefaultDict[str, ZwiftItem]:
    logger.setLevel(log_level)
    answer: defaultdict[str, ZwiftItem] = defaultdict(ZwiftItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing...")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")

        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftDTO)
            dto = cast(ZwiftDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        item = ZwiftItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer


def read_zwiftracingapp_files(
    file_names: Optional[list[str]],
    dir_path: str,
    logger: logging.Logger,
    log_level: int = logging.INFO
) -> DefaultDict[str, ZwiftRacingAppItem]:
    logger.setLevel(log_level)
    answer: defaultdict[str, ZwiftRacingAppItem] = defaultdict(ZwiftRacingAppItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing..")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppDTO)
            dto = cast(ZwiftRacingAppDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        item = ZwiftRacingAppItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer


def read_zwiftpower_files(
    file_names: Optional[list[str]],
    dir_path: str,
    logger: logging.Logger,
    log_level: int = logging.INFO
) -> DefaultDict[str, ZwiftPowerItem]:
    logger.setLevel(log_level)
    answer: defaultdict[str, ZwiftPowerItem] = defaultdict(ZwiftPowerItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing..")

    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerDTO)
            dto = cast(ZwiftPowerDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        item = ZwiftPowerItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer


def read_zwiftpower_graph_watts_files(
    file_names: Optional[list[str]],
    dir_path: str,
    logger: logging.Logger,
    log_level: int = logging.INFO
) -> DefaultDict[str, ZsunWattsItem]:
    logger.setLevel(log_level)
    answer: defaultdict[str, ZsunWattsItem] = defaultdict(ZsunWattsItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing..")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerWattsDTO)
            dto = cast(ZwiftPowerWattsDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        temp = ZsunWattsItem.from_ZwiftPowerBestPowerDTO(dto)
        temp.zwift_id = zwift_id
        answer[zwift_id] = temp

    return answer

# functions to get arbitrary Zwift IDs and ZsunItems for testing.

def get_test_IDs() -> List[str]:
    return [
  "1024413",
  "11526",
  "11741",
  "1193",
  "1657744",
  "1707548",
  "183277",
  "1884456",
  "2398312",
  "2508033",
  "2682791",
  "3147366",
  "383480",
  "384442",
  "480698",
  "5134",
  "5421258",
  "5490373",
  "5530045",
  "5569057",
  "9011",
  "991817",
  "4945836",
]

    # file_name = "betel_IDs.json"
    # dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    # inputjson = read_text(dir_path, file_name)
    # anything = decode_json(inputjson)
    # answer = cast(List[str], anything)
    # return answer

def get_test_ZsunDTO(id : str) -> ZsunItem:
    file_name = "test_ZsunItems.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    riders = read_json_dict_of_ZsunDTO(file_name, dir_path)
    answer = riders[id]
    return answer

# functions used to read a pre-processed JSON dictionary file in some or other folder and return its contents. 

def read_json_dict_of_ZsunDTO(file_name: str, dir_path: str) -> DefaultDict[str, ZsunItem]:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    inputjson = read_text(dir_path, file_name)
    answer = JghSerialization.validate(inputjson, Dict[str, ZsunDTO])
    answer = cast(Dict[str, ZsunDTO], answer)
    return defaultdict(
        ZsunItem, 
        {
            key: ZsunItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def read_json_dict_of_ZsunWattsDTO(file_name: str, dir_path: str) -> DefaultDict[str, ZsunWattsItem]:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")
    
    inputjson = read_text(dir_path, file_name)
    answer = JghSerialization.validate(inputjson, Dict[str, ZsunWattsDTO])
    answer = cast(Dict[str, ZsunWattsDTO], answer)
    return defaultdict(
        ZsunWattsItem,
        {
            key: ZsunWattsItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def read_json_dict_of_regressionmodellingDTO(file_name: str, dir_path: str) -> DefaultDict[str, RegressionModellingItem]:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")
    
    inputjson = read_text(dir_path, file_name)
    answer = JghSerialization.validate(inputjson, Dict[str, RegressionModellingDTO])
    answer = cast(Dict[str, RegressionModellingDTO], answer)
    return defaultdict(RegressionModellingItem,
        {
            key: RegressionModellingItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

# functions used to write a dictionary of items to a JSON file in some or other folder.

def write_json_dict_of_ZsunWattsItem(data: Dict[str, ZsunWattsItem], file_name: str, dir_path: str) -> None:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    serialized_data = JghSerialization.serialise(data)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(serialized_data)

    logger.debug(f"File saved : {file_name}")


def write_json_dict_of_regressionmodellingItem(data: Dict[str, RegressionModellingItem], file_name: str, dir_path: str) -> None:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    serialized_data = JghSerialization.serialise(data)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(serialized_data)

    logger.debug(f"File saved : {file_name}")

# local logging utility function to log multiline messages

def log_multiline(logger: logging.Logger, lines: list[str]) -> None:
    logger.info("\n".join(lines))

    # tests

def main(logger: logging.Logger):

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"

    zsun_raw_cp_dict_for_betel = read_zwiftracingapp_files(get_test_IDs(),INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    jgh_cp_dict = read_json_dict_of_ZsunWattsDTO(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_json_dict_of_ZsunWattsItem(combined_raw_cp_dict_for_betel, "extracted_input_cp_data_for_betel.json", INPUT_CP_DATA_DIRPATH)

def main02(logger: logging.Logger):

    ZWIFT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwift/"
    ZWIFTRACINGAPP_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"
    ZWIFTPOWER_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/power-graph-watts/"

    dict_of_zwift_profiles = read_zwift_files(None, ZWIFT_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwift_profiles)} zwift profile items")

    dict_of_zwiftracingapp_profiles = read_zwiftracingapp_files(None, ZWIFTRACINGAPP_DIRPATH)
    logger.info (f"Imported {len(dict_of_zwiftracingapp_profiles)} zwiftracingapp profile items")

    dict_of_zwiftpower_profiles = read_zwiftpower_files(None, ZWIFTPOWER_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwiftpower_profiles)} zwiftpower profile items")

    dict_of_zwiftpower_90day_bestpower = read_zwiftpower_graph_watts_files(None, ZWIFTPOWER_GRAPHS_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwiftpower_90day_bestpower)} zwiftpower bestpower info items")

def main03(logger: logging.Logger):

    ZWIFT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwift/"

    my_dict = read_zwift_files(None, ZWIFT_DIRPATH)

    logger.info (f"Imported {len(my_dict)} zwift profile items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Profile for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.last_name} zFTP = {round(item.zftp)} Watts, Height = {round(item.height_mm/10.0)} cm")

    logger.info(f"Imported {len(my_dict)} items")

def main04(logger: logging.Logger):

    ZWIFTRACINGAPP_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"

    my_dict = read_zwiftracingapp_files(None, ZWIFTRACINGAPP_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.fullname} country = {item.country}")

    logger.info(f"Imported {len(my_dict)} items")

def main05(logger: logging.Logger):

    ZWIFTPOWER_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/profile-page/"

    my_dict = read_zwiftpower_files(None, ZWIFTPOWER_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.zwift_name}")

    logger.info(f"Imported {len(my_dict)} items")

def main06(logger: logging.Logger):

    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/power-graph-watts/"

    my_dict = read_zwiftpower_graph_watts_files(None, ZWIFTPOWER_GRAPHS_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} cp60 = {item.bp_60}")

    logger.info(f"Imported {len(my_dict)} items")


if __name__ == "__main__":
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # main(logger)
    # main02(logger)
    # main03(logger)
    # main04(logger)
    # main05(logger)
    main06(logger)
