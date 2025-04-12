from typing import Dict, cast
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDTO
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDTO
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem

def get_all_zwiftriders() -> Dict[str, ZwiftRiderItem]:
    """
    Retrieve all Zwift riders from a JSON file and convert them to ZwiftRiderItem instances.

    Returns:
        Dict[str, ZwiftRiderItem]: A dictionary of ZwiftRiderItem instances eyed by 
        the same key as in the JSON dictionary, which currently is abbreviated rider name.
    """
    file_name = "zwiftrider_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    inputjson = read_text(directory_path, file_name)

    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDTO])

    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDTO], dict_of_zwiftrider_dto) # for the benfit of type inference

    dict_of_zwiftrideritem = {
        key: ZwiftRiderItem.from_dataTransferObject(dto)
        for key, dto in dict_of_zwiftrider_dto.items()
    }

    return dict_of_zwiftrideritem

def get_all_zwiftriders_cp_data() -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Retrieve all Zwift riders' critical power data from a JSON file and convert them to ZwiftRiderCriticalPowerItem instances.

    Returns:
    Dict[str, ZwiftRiderCriticalPowerItem]: A dictionary of ZwiftRiderCriticalPowerItem instances keyed by 
    the same key as in the JSON dictionary, which currently is abbreviated rider name.
    """
    file_name = "zwiftrider_critical_power_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    inputjson = read_text(directory_path, file_name)

    dict_of_zwiftrider_cp_dto = JghSerialization.validate(inputjson, Dict[str, ZwiftRiderCriticalPowerDTO])

    dict_of_zwiftrider_cp_dto = cast(Dict[str, ZwiftRiderCriticalPowerDTO], dict_of_zwiftrider_cp_dto)  # for the benefit of type inference

    # Map each DTO to a ZwiftRiderCriticalPowerItem using from_dataTransferObject
    dict_of_zwiftrider_cp_item = {
        key: ZwiftRiderCriticalPowerItem.from_dataTransferObject(dto)
        for key, dto in dict_of_zwiftrider_cp_dto.items()
    }

    return dict_of_zwiftrider_cp_item