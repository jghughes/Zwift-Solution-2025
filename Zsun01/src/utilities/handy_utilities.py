from typing import Dict, cast, Optional
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDTO
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDTO
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem
import os
from zwiftracing_app_post_dto import ZwiftRacingAppPostDTO

# Module-level constants
RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
CPDATA_FILE_NAME = "betel_cp_data.json"
ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
INPU_CPDATA_FILENAME_ORIGINATING_FROM_ZWIFTRACINGAPP = "input_cp_data_for_Zsun.json"
INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"

OUTPUT_FILE_NAME = "betel_cp_data.json"
OUTPUT_DIR_PATH = ZSUN01_PROJECT_DATA_DIRPATH


def read_dict_of_zwiftriders(
    file_name: Optional[str] = RIDERDATA_FILE_NAME,
    dir_path: Optional[str] = ZSUN01_PROJECT_DATA_DIRPATH
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
    dir_path: Optional[str] = ZSUN01_PROJECT_DATA_DIRPATH
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


def read_all_zwiftracerapp_files_in_folder(
    dir_path: Optional[str] = INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH
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

#illustration of the function
def main():
    betel_IDs =["1193", "5134", "9011", "11526", "183277", "383480", "384442", "480698", "58160", "1024413", "991817", "1713736", "2398312", "2508033"  "2682791", "3147366", "5421258", "5490373", "5530045", "5569057", "6142432"] 

    # Example usage


    zsun_cp_dict = read_all_zwiftracerapp_files_in_folder(INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)
    jgh_cp_dict = read_dict_of_cpdata(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    zsun_raw_cp_dict_for_betel = {key: value for key, value in zsun_cp_dict.items() if key in betel_IDs}

    combined_raw_cp_dict_for_betel = {**jgh_cp_dict, **zsun_raw_cp_dict_for_betel}

    write_dict_of_cpdata(combined_raw_cp_dict_for_betel, "extracted_input_cp_data_for_betel.json", INPUT_CP_DATA_DIRPATH)


if __name__ == "__main__":
    main()