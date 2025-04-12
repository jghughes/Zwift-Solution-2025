from typing import Dict, cast, Optional
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDTO
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDTO
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem
import os
from zwiftracing_app_post_dto import ZwiftRacingAppPostDTO

# Module-level constants
ZWIFTRIDER_FILE_NAME = "zwiftrider_dictionary.json"
ZWIFTRIDER_DIR_PATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

CPDATA_FILE_NAME = "betel_for_jgh_josh_markb.json"
CPDATA_DIR_PATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

ZWIFTRACERAPP_FILES_DIR_PATH = "C:/Users/johng/holding_pen/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"

ZWIFTRACERAPP_DATA_FILE_NAME = "raw_zwiftracing_app_data_dictionary.json"
ZWIFTRACERAPP_DATA_DIR_PATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

OUTPUT_FILE_NAME = "raw_betel_cp_data.json"
OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffFromDaveK/zsun_everything_April_2025/"


def read_dict_of_zwiftriders(
    file_name: Optional[str] = ZWIFTRIDER_FILE_NAME,
    dir_path: Optional[str] = ZWIFTRIDER_DIR_PATH
) -> Dict[str, ZwiftRiderItem]:
    """
    Retrieve all Zwift riders from a JSON file and convert them to ZwiftRiderItem instances.

    Args:
        file_name (Optional[str]): The name of the file to read.
        dir_path (Optional[str]): The directory path where the file is located.

    Returns:
        Dict[str, ZwiftRiderItem]: A dictionary of ZwiftRiderItem instances.
    """
    inputjson = read_text(dir_path, file_name)

    dict_of_zwiftrider_dto = JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDTO])
    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDTO], dict_of_zwiftrider_dto)

    return {
        key: ZwiftRiderItem.from_dataTransferObject(dto)
        for key, dto in dict_of_zwiftrider_dto.items()
    }


def read_dict_of_cpdata(
    file_name: Optional[str] = CPDATA_FILE_NAME,
    dir_path: Optional[str] = CPDATA_DIR_PATH
) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve all Zwift riders' critical power data from a JSON file and convert them to ZwiftRiderCriticalPowerItem instances.

    Args:
        file_name (Optional[str]): The name of the file to read.
        dir_path (Optional[str]): The directory path where the file is located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """
    inputjson = read_text(dir_path, file_name)

    dict_of_zwiftrider_cp_dto = JghSerialization.validate(inputjson, Dict[str, ZwiftRiderCriticalPowerDTO])
    dict_of_zwiftrider_cp_dto = cast(Dict[str, ZwiftRiderCriticalPowerDTO], dict_of_zwiftrider_cp_dto)

    return {
        key: ZwiftRiderCriticalPowerItem.from_dataTransferObject(dto)
        for key, dto in dict_of_zwiftrider_cp_dto.items()
    }


def read_collection_of_zwiftracerapp_files(
    dir_path: Optional[str] = ZWIFTRACERAPP_FILES_DIR_PATH
) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve all Zwift Racing App data from JSON files in a directory and convert them
    to ZwiftRiderCriticalPowerItem instances.

    Args:
        dir_path (Optional[str]): The directory path where the files are located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """
    result: Dict[str, ZwiftRiderCriticalPowerItem] = {}

    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        if os.path.isfile(file_path):
            inputjson = read_text(dir_path, file_name)
            zwiftracing_rider_dto = JghSerialization.validate(inputjson, ZwiftRacingAppPostDTO)
            zwiftracing_rider_dto = cast(ZwiftRacingAppPostDTO, zwiftracing_rider_dto)

            if zwiftracing_rider_dto.riderId:
                result[zwiftracing_rider_dto.riderId] = ZwiftRiderCriticalPowerItem.from_zwift_racing_app_DTO(
                    zwiftracing_rider_dto
                )

    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def read_dict_of_zwiftracerapp_data(
    file_name: Optional[str] = ZWIFTRACERAPP_DATA_FILE_NAME,
    dir_path: Optional[str] = ZWIFTRACERAPP_DATA_DIR_PATH
) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve all Zwift Racing App data from a single JSON dictionary file and convert
    them to ZwiftRiderCriticalPowerItem instances.

    Args:
        file_name (Optional[str]): The name of the file to read.
        dir_path (Optional[str]): The directory path where the file is located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """
    inputjson = read_text(dir_path, file_name)

    dict_of_zwiftracing_dto = JghSerialization.validate(inputjson, Dict[str, ZwiftRacingAppPostDTO])
    dict_of_zwiftracing_dto = cast(Dict[str, ZwiftRacingAppPostDTO], dict_of_zwiftracing_dto)

    return dict(sorted({
        key: ZwiftRiderCriticalPowerItem.from_zwift_racing_app_DTO(dto)
        for key, dto in dict_of_zwiftracing_dto.items()
    }.items(), key=lambda item: int(item[0])))


def write_dict_of_cpdata(
    data: Dict[str, ZwiftRiderCriticalPowerItem],
    file_name: Optional[str] = OUTPUT_FILE_NAME,
    dir_path: Optional[str] = OUTPUT_DIR_PATH
) -> None:
    """
    Serialize a dictionary of ZwiftRiderCriticalPowerItem instances and write it to a JSON file.

    Args:
        data (Dict[str, ZwiftRiderCriticalPowerItem]): The data to serialize.
        file_name (Optional[str]): The name of the file to write.
        dir_path (Optional[str]): The directory path where the file will be written.
    """
    serialized_data = JghSerialization.serialise(data)

    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(serialized_data)


#illustration of the function
if __name__ == "__main__":

    betelIDs =["1193", "5134", "9011", "11526", "183277", "383480", "384442", "480698", "58160", "1024413", "991817", "1713736", "2398312", "2508033", "2682791", "3147366", "5421258", "5490373", "5530045", "5569057", "6142432"]

    # Example usage
    zwiftracing_app_data_dict = read_dict_of_zwiftracerapp_data()

    # Instantiate a new dict that only includes the betelIDs
    zwiftracing_app_data_for_betels = {
        key: value
        for key, value in zwiftracing_app_data_dict.items()
        if key in betelIDs
    }

    me_josh_markb = read_dict_of_cpdata()

    # For each item in me_josh_markb, overwrite the matching cp_data attributes
    for key, cp_item in me_josh_markb.items():
        if key in zwiftracing_app_data_consolidated:
            # Overwrite the power data attributes
            consolidated_item = zwiftracing_app_data_consolidated[key]
            consolidated_item.cp_5_sec = cp_item.cp_5_sec
            consolidated_item.cp_15_sec = cp_item.cp_15_sec
            consolidated_item.cp_30_sec = cp_item.cp_30_sec
            consolidated_item.cp_1_min = cp_item.cp_1_min
            consolidated_item.cp_2_min = cp_item.cp_2_min
            consolidated_item.cp_3_min = cp_item.cp_3_min
            consolidated_item.cp_5_min = cp_item.cp_5_min
            consolidated_item.cp_10_min = cp_item.cp_10_min
            consolidated_item.cp_12_min = cp_item.cp_12_min
            consolidated_item.cp_15_min = cp_item.cp_15_min
            consolidated_item.cp_20_min = cp_item.cp_20_min
            consolidated_item.cp_30_min = cp_item.cp_30_min
            consolidated_item.cp_40_min = cp_item.cp_40_min

    # Serialize and write the data to a file
    write_dict_of_cpdata(zwiftracing_app_data_consolidated)