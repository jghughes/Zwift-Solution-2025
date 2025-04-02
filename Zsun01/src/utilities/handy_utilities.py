from typing import Dict, cast
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDataTransferObject
from zwiftrider_criticalpower_dto import ZwiftRiderCriticalPowerDataTransferObject
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem

def get_all_zwiftriders() -> Dict[str, ZwiftRiderItem]:

    file_name = "zwiftrider_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    inputjson = read_text(directory_path, file_name)

    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto) # for the benfit of type inference

    dict_of_zwiftrideritem = ZwiftRiderItem.from_dict_of_dataTransferObjects(dict_of_zwiftrider_dto)

    return dict_of_zwiftrideritem

def get_all_zwiftriders_cp_data() -> Dict[str, ZwiftRiderCriticalPowerItem]:

    file_name = "zwiftrider_critical_power_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    inputjson = read_text(directory_path, file_name)

    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderCriticalPowerDataTransferObject])

    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderCriticalPowerDataTransferObject], dict_of_zwiftrider_dto) # for the benfit of type inference

    dict_of_zwiftrideritem = ZwiftRiderCriticalPowerItem.from_dict_of_dataTransferObjects(dict_of_zwiftrider_dto)

    return dict_of_zwiftrideritem


