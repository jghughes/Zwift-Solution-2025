import os
from typing import Dict, cast, List, DefaultDict
from collections import defaultdict
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from repository_of_scraped_riders import read_zwift_files, read_zwiftracingapp_files, read_zwiftpower_files, read_zwiftpower_graph_watts_files
from regression_modelling_dto import RegressionModellingDTO
from regression_modelling_item import RegressionModellingItem
from zsun_watts_properties_dto import ZsunWattsDTO
from zsun_watts_properties_item import ZsunWattsItem
from zsun_rider_dto import ZsunDTO
from zsun_rider_item import ZsunItem
import logging
logger = logging.getLogger(__name__)

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

def log_multiline(lines: list[str]) -> None:
    logger.info("\n".join(lines))

    # tests

def main():

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"

    zsun_raw_cp_dict_for_betel = read_zwiftracingapp_files(get_test_IDs(),INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    jgh_cp_dict = read_json_dict_of_ZsunWattsDTO(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_json_dict_of_ZsunWattsItem(combined_raw_cp_dict_for_betel, "extracted_input_cp_data_for_betel.json", INPUT_CP_DATA_DIRPATH)

def main02(logger: logging.Logger):

    dict_of_zwift_profiles = read_zwift_files(None, ZWIFT_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwift_profiles)} zwift profile items")

    dict_of_zwiftracingapp_profiles = read_zwiftracingapp_files(None, ZWIFTRACINGAPP_DIRPATH)
    logger.info (f"Imported {len(dict_of_zwiftracingapp_profiles)} zwiftracingapp profile items")

    dict_of_zwiftpower_profiles = read_zwiftpower_files(None, ZWIFTPOWER_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwiftpower_profiles)} zwiftpower profile items")

    dict_of_zwiftpower_90day_bestpower = read_zwiftpower_graph_watts_files(None, ZWIFTPOWER_GRAPHS_DIRPATH)
    logger.info(f"Imported {len(dict_of_zwiftpower_90day_bestpower)} zwiftpower bestpower info items")

if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwift/"
    ZWIFTRACINGAPP_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftracing-app-post/"
    ZWIFTPOWER_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-04-00/zwiftpower/power-graph-watts/"


    main()
    # main02()
    # main03()
    # main04()
    # main05()
    # main06()
