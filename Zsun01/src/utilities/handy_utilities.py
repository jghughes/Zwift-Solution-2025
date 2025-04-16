from typing import Dict, cast, Optional
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDTO
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDTO
from zwiftpower_cp_graph_dto import ZwiftPowerCpGraphDTO
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem
import os
from zwiftracing_dto import ZwiftRacingAppPostDTO

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
    serialized_data = JghSerialization.serialise(data)

    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(serialized_data)

def read_many_zwiftracing_files_in_folder(riderIDs: list[str], dir_path: str) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve many individual ZwiftRacing JSON data files in a directory and convert them
    to a dict of ZwiftRiderCriticalPowerItem instances. The key of the dicts is zwiftID.  
    The data transfer object is ZwiftRacingAppPostDTO.

    Args:
        dir_path (str): The directory path where the files are located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """
    result: Dict[str, ZwiftRiderCriticalPowerItem] = {}

    for file_name in os.listdir(dir_path):
        if not dir_path or not file_name:
            raise ValueError("Both 'dir_path' and 'file_name' must be valid non-empty strings.")

        # if riderIDs is none, go ahead and download all files. Otherwise, skip files that are not in riderIDs

        if riderIDs and (not file_name.endswith(".json") or file_name[:-5] not in riderIDs):
            continue

        # go ahead and process the file


        file_path = os.path.join(dir_path, file_name)

        if os.path.isfile(file_path):
            inputjson = read_text(dir_path, file_name)
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppPostDTO)
            dto = cast(ZwiftRacingAppPostDTO, dto)

            if dto.riderId:
                result[dto.riderId] = ZwiftRiderCriticalPowerItem.from_zwift_racing_app_DTO(
                    dto
                )

    return dict(sorted(result.items(), key=lambda item: int(item[0])))

def read_many_zwiftpower_profile_files_in_folder(riderIDs: list[str], dir_path: str) -> Dict[str, ZwiftRiderItem]:
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
    result: Dict[str, ZwiftRiderItem] = {}

    for file_name in os.listdir(dir_path):
        if not dir_path or not file_name:
            raise ValueError("Both 'dir_path' and 'file_name' must be valid non-empty strings.")

        # if riderIDs is none, go ahead and download all files. Otherwise, skip files that are not in riderIDs

        if riderIDs and (not file_name.endswith(".json") or file_name[:-5] not in riderIDs):
            continue

        # go ahead and process the file

        file_path = os.path.join(dir_path, file_name)

        if os.path.isfile(file_path):
            inputjson = read_text(dir_path, file_name)
            dto = JghSerialization.validate(inputjson, ZwiftRiderDTO)
            dto = cast(ZwiftRiderDTO, dto)

            if dto.zwiftid:
                result[str(dto.zwiftid)] = ZwiftRiderItem.from_dataTransferObject(dto)

    return dict(sorted(result.items(), key=lambda item: int(item[0])))

def read_many_zwiftpower_cp_graph_files_in_folder(riderIDs: list[str], dir_path: str) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve many individual ZwiftPower cp_power_graph JSON files in a directory and convert them
    to a dict of ZwiftRiderCriticalPowerItem instances. If riderIDs is None, all files are processed.
    Otherwise, only files with filenames the same as in riderIDs are processed. The key 
    of the dict is zwiftID. The data transfer object is ZwiftPowerCpGraphDTO.

    Args:
        dir_path (str): The directory path where the files are located.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances.
    """
    result: Dict[str, ZwiftRiderCriticalPowerItem] = {}

    for file_name in os.listdir(dir_path):
        if not dir_path or not file_name:
            raise ValueError("Both 'dir_path' and 'file_name' must be valid non-empty strings.")

        # if riderIDs is none, go ahead and download all files. Otherwise, skip files that are not in riderIDs

        if riderIDs and (not file_name.endswith(".json") or file_name[:-5] not in riderIDs):
            continue

        # go ahead and process the file

        file_path = os.path.join(dir_path, file_name)

        if os.path.isfile(file_path):
            inputjson = read_text(dir_path, file_name)
            dto = JghSerialization.validate(inputjson, ZwiftPowerCpGraphDTO)
            dto = cast(ZwiftPowerCpGraphDTO, dto)

            if file_name[:-5]:
                result[file_name[:-5]] = ZwiftRiderCriticalPowerItem.from_zwiftpower_cp_graph_DTO(dto)

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


if __name__ == "__main__":
    main()