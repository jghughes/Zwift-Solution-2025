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

    # tests

def get_recognised_ZsunItems_only(riderIDs: List[str], dict_of_ZsunItems: Dict[str, ZsunItem]) -> List[ZsunItem]:
    """
    Returns a list of ZsunItem objects for riderIDs found in dict_of_ZsunItems.
    Logs a warning for each riderID not found.
    """
    riders: List[ZsunItem] = []
    for riderID in riderIDs:
        if riderID in dict_of_ZsunItems:
            riders.append(dict_of_ZsunItems[riderID])
        else:
            logger.warning(f"Rider ID '{riderID}' not found in dict_of_ZsunItems. Skipping.")
    return riders


def main():

    all_riders = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME,DATA_DIRPATH)

    logger.info(f"Imported {len(all_riders)} zsun riders")

def main01():

    riderIDs = RepositoryOfTeams.get_IDs_of_riders_on_a_team("test_sample")

    zsun_raw_cp_dict_for_betel = read_zwiftracingapp_files(riderIDs,ZWIFTRACINGAPP_DIRPATH)

    jgh_cp_dict = read_json_dict_of_ZsunWattsDTO(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_json_dict_of_ZsunWattsItem(combined_raw_cp_dict_for_betel, OUTPUT_CPDATA_FILENAME, INPUT_CP_DATA_DIRPATH)

def main02():

    dict_of_zwift_profiles = read_zwift_files(None, ZWIFT_DIRPATH)
    dict_of_zwiftracingapp_profiles = read_zwiftracingapp_files(None, ZWIFTRACINGAPP_DIRPATH)
    dict_of_zwiftpower_profiles = read_zwiftpower_files(None, ZWIFTPOWER_DIRPATH)
    dict_of_zwiftpower_90day_bestpower = read_zwiftpower_graph_watts_files(None, ZWIFTPOWER_GRAPHS_DIRPATH)

    logger.info(f"Imported {len(dict_of_zwift_profiles)} zwift profile items")
    logger.info (f"Imported {len(dict_of_zwiftracingapp_profiles)} zwiftracingapp profile items")
    logger.info(f"Imported {len(dict_of_zwiftpower_profiles)} zwiftpower profile items")
    logger.info(f"Imported {len(dict_of_zwiftpower_90day_bestpower)} zwiftpower 90-day best graph items")

if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")

    from team_rosters import RepositoryOfTeams

    from filenames import RIDERS_FILE_NAME
    from dirpaths import DATA_DIRPATH, ZWIFT_DIRPATH, ZWIFTRACINGAPP_DIRPATH, ZWIFTPOWER_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    OUTPUT_CPDATA_FILENAME = "extracted_input_cp_data_for_betel.json"

    main()
    # # main01()
    # main02()
