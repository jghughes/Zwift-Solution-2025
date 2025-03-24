from typing import Dict, cast
from jgh_read_write import read_text
from jgh_serialization import JghSerialization
from zwiftrider_dto import ZwiftRiderDataTransferObject
from zwiftrider_item import ZwiftRiderItem

def get_all_zwiftriders() -> Dict[str, ZwiftRiderItem]:

    file_name = "rider_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/rider_data/"

    # # Load rider data from JSON
    inputjson = read_text(directory_path, file_name)
    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    # # for the benfit of type inference: explicitly cast the return value of the serialisation to expected generic Type
    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto)

    # #transform to ZwiftRiderItem dict
    dict_of_zwiftrideritem = ZwiftRiderItem.from_dataTransferObject_dict(dict_of_zwiftrider_dto)

    return dict_of_zwiftrideritem
