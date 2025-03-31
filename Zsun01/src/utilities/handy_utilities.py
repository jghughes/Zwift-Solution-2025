from typing import Dict, cast
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDataTransferObject
from zwiftrider_related_items import ZwiftRiderItem

def get_all_zwiftriders() -> Dict[str, ZwiftRiderItem]:

    file_name = "zwiftrider_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    inputjson = read_text(directory_path, file_name)

    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto) # for the benfit of type inference

    dict_of_zwiftrideritem = ZwiftRiderItem.from_dict_of_dataTransferObjects(dict_of_zwiftrider_dto)

    return dict_of_zwiftrideritem


