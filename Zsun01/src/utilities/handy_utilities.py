import os
from typing import Dict, cast, Optional, List, DefaultDict
from collections import defaultdict
from jgh_read_write import read_text, read_filepath_as_text, help_select_filepaths_in_folder
from jgh_serialization import JghSerialization
from zwift_rider_particulars_dto import ZwiftRiderParticularsDTO
from zwift_rider_particulars_item import ZwiftRiderParticularsItem
from zwiftpower_watts_ordinates_dto import ZwiftPowerWattsOrdinatesDTO
from zwiftpower_rider_particulars_dto import ZwiftPowerRiderParticularsDTO
from zwiftpower_rider_particulars_item import ZwiftPowerRiderParticularsItem
from zwiftracingapp_rider_particulars_dto import *
from zwiftracingapp_rider_particulars_item import ZwiftRacingAppRiderParticularsItem
from regression_modelling_dto import RegressionModellingDTO
from regression_modelling_item import RegressionModellingItem
from zsun_watts_properties_dto import ZsunWattsPropertiesDTO
from zsun_watts_properties_item import ZsunWattsPropertiesItem
from zsun_rider_dto import ZsunRiderDTO
from zsun_rider_item import ZsunRiderItem

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

#functions used to read many files in a folder and return a dictionary of items. used to read raw zwift profiles, zwiftracingapp profiles, zwiftpower profiles, and zwiftpower best power files obtained by DaveK for Brute

def read_many_zwift_profile_files_in_folder(file_names: Optional[list[str]], dir_path: str) -> DefaultDict[str, ZwiftRiderParticularsItem]:

    answer: defaultdict[str, ZwiftRiderParticularsItem] = defaultdict(ZwiftRiderParticularsItem)

    file_paths = help_select_filepaths_in_folder(file_names,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")

        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftRiderParticularsDTO)
            dto = cast(ZwiftRiderParticularsDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        item = ZwiftRiderParticularsItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_many_zwiftracingapp_profile_files_in_folder(file_names: Optional[list[str]], dir_path: str) -> DefaultDict[str, ZwiftRacingAppRiderParticularsItem]:
    
    answer: defaultdict[str, ZwiftRacingAppRiderParticularsItem] = defaultdict(ZwiftRacingAppRiderParticularsItem)

    file_paths = help_select_filepaths_in_folder(file_names,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppRiderParticularsDTO)
            dto = cast(ZwiftRacingAppRiderParticularsDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        item = ZwiftRacingAppRiderParticularsItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_many_zwiftpower_profile_files_in_folder(file_names: Optional[list[str]], dir_path: str) -> DefaultDict[str, ZwiftPowerRiderParticularsItem]:
    answer: defaultdict[str, ZwiftPowerRiderParticularsItem] = defaultdict(ZwiftPowerRiderParticularsItem)

    file_paths = help_select_filepaths_in_folder(file_names,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")

    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerRiderParticularsDTO)
            dto = cast(ZwiftPowerRiderParticularsDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        item = ZwiftPowerRiderParticularsItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_many_zwiftpower_bestpower_files_in_folder(file_names: Optional[list[str]], dir_path: str) -> DefaultDict[str, ZsunWattsPropertiesItem]:

    answer: defaultdict[str, ZsunWattsPropertiesItem] = defaultdict(ZsunWattsPropertiesItem)

    file_paths = help_select_filepaths_in_folder(file_names,".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerWattsOrdinatesDTO)
            dto = cast(ZwiftPowerWattsOrdinatesDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)  # Safely remove the extension
        temp = ZsunWattsPropertiesItem.from_ZwiftPowerBestPowerDTO(dto) # the meat
        temp.zwift_id = zwift_id  # zwift_id is obtained from the file name, this is the only place it is set
        answer[zwift_id] = temp


    return answer

# functions to get arbitrary Zwift IDs and zsunrideritems for testing.

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

def read_dict_of_test_zsunriderDTO(id : str) -> ZsunRiderItem:
    file_name = "test_ZsunRiderItems.json"
    dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    riders = read_dict_of_zsunriderDTO(file_name, dir_path)
    answer = riders[id]
    return answer

#functions used to read a pre-processed file in a folder and return a dictionary of its contents. 

def read_dict_of_zsunriderDTO(file_name: str, dir_path: str) -> DefaultDict[str, ZsunRiderItem]:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")

    inputjson = read_text(dir_path, file_name)
    answer = JghSerialization.validate(inputjson, Dict[str, ZsunRiderDTO])
    answer = cast(Dict[str, ZsunRiderDTO], answer)
    return defaultdict(
        ZsunRiderItem, 
        {
            key: ZsunRiderItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def read_dict_of_zsunwattspropertiesDTO(file_name: str, dir_path: str) -> DefaultDict[str, ZsunWattsPropertiesItem]:
    if not dir_path:
        raise ValueError("dir_path must be a valid string.")
    if not dir_path.strip():
        raise ValueError("dir_path must be a valid non-empty string.")
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Unexpected error: The specified directory does not exist: {dir_path}")
    
    inputjson = read_text(dir_path, file_name)
    answer = JghSerialization.validate(inputjson, Dict[str, ZsunWattsPropertiesDTO])
    answer = cast(Dict[str, ZsunWattsPropertiesDTO], answer)
    return defaultdict(
        ZsunWattsPropertiesItem,
        {
            key: ZsunWattsPropertiesItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def write_dict_of_zsunwattspropertiesItem(data: Dict[str, ZsunWattsPropertiesItem], file_name: str, dir_path: str) -> None:
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

def read_dict_of_regressionmodellingDTO(file_name: str, dir_path: str) -> DefaultDict[str, RegressionModellingItem]:
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

def write_dict_of_regressionmodellingItem(data: Dict[str, RegressionModellingItem], file_name: str, dir_path: str) -> None:
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

def main():

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"


    zsun_raw_cp_dict_for_betel = read_many_zwiftracingapp_profile_files_in_folder(get_test_IDs(),INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    jgh_cp_dict = read_dict_of_zsunwattspropertiesDTO(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_dict_of_zsunwattspropertiesItem(combined_raw_cp_dict_for_betel, "extracted_input_cp_data_for_betel.json", INPUT_CP_DATA_DIRPATH)

def main02():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/power-graph-watts/"

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

    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwift/"

    my_dict = read_many_zwift_profile_files_in_folder(None, ZWIFT_PROFILES_DIRPATH)

    logger.info (f"Imported {len(my_dict)} zwift profile items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Profile for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.last_name} zFTP = {round(item.zftp)} Watts, Height = {round(item.height_mm/10.0)} cm")

    logger.info(f"Imported {len(my_dict)} items")

def main04():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"

    my_dict = read_many_zwiftracingapp_profile_files_in_folder(None, ZWIFTRACINGAPP_PROFILES_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.fullname} country = {item.country}")

    logger.info(f"Imported {len(my_dict)} items")

def main05():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/profile-page/"

    my_dict = read_many_zwiftpower_profile_files_in_folder(None, ZWIFTPOWER_PROFILES_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.zwift_name}")

    logger.info(f"Imported {len(my_dict)} items")

def main06():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/power-graph-watts/"

    my_dict = read_many_zwiftpower_bestpower_files_in_folder(None, ZWIFTPOWER_GRAPHS_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} cp60 = {item.bp_60}")

    logger.info(f"Imported {len(my_dict)} items")


if __name__ == "__main__":
    main06()