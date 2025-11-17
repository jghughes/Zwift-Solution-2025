from collections import defaultdict
from pathlib import Path
from typing import Dict
import json

from jgh_path_helpers import throw_if_file_path_ingredients_invalid_or_not_exists
from jgh_read_write import read_text, write_json_file
from regression_modelling_dto import RegressionModellingDTO, RegressionModellingDTODictModel
from regression_modelling_item import RegressionModellingItem
from rider_brute_item import RiderBruteItem
from rider_brute_dto import RiderBruteDtoDictModel

from zwiftpower_flattened_90_day_watts_dto import ZwiftPower90DayWattsDTODictModel, ZwiftPowerFlattened90DayWattsDTO
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem 

def read_file_as_json_dict_of_RiderDTO(dirpath: Path, filename: str) -> Dict[str, RiderBruteItem]:
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    text = read_text(dirpath, filename)
    something = json.loads(text)
    answer = RiderBruteDtoDictModel.model_validate(something, strict=True).root
    return defaultdict(
        RiderBruteItem,
        {
            key: RiderBruteItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def read_file_as_json_dict_of_ZwiftPower90DayWattsDTO(dirpath: Path, filename: str) -> Dict[str, ZwiftPowerFlattened90dayWattsItem]:
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    text = read_text(dirpath, filename)
    something = json.loads(text)
    answer = ZwiftPower90DayWattsDTODictModel.model_validate(something, strict=True).root
    return defaultdict(
        ZwiftPowerFlattened90dayWattsItem,
        {
            key: ZwiftPowerFlattened90dayWattsItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def read_file_as_json_dict_of_RegressionModellingDTO(dirpath: Path, filename: str) -> Dict[str, RegressionModellingItem]:
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    text = read_text(dirpath, filename)
    something = json.loads(text)
    answer = RegressionModellingDTODictModel.model_validate(something, strict=True).root
    return defaultdict(
        RegressionModellingItem,
        {
            key: RegressionModellingItem.from_dataTransferObject(dto)
            for key, dto in answer.items()
        }
    )

def write_with_json_file_ext_dict_of_ZwiftPower90dayWattsDTO(
    dirpath: Path,
    filename: str,
    data: Dict[str, ZwiftPowerFlattened90dayWattsItem]
) -> None:
    """
    Serializes and writes a dictionary of ZwiftPower90dayWattsDto objects to a JSON file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    dataAsDictDTO: Dict[str, ZwiftPowerFlattened90DayWattsDTO] = {
        rider_id: ZwiftPowerFlattened90dayWattsItem.to_dataTransferObject(item)
        for rider_id, item in data.items()
    }
    myObj = ZwiftPower90DayWattsDTODictModel(dataAsDictDTO)
    text = myObj.model_dump_json(exclude_none=False)
    write_json_file(dirpath, filename, text)

def write_with_json_file_ext_dict_of_RegressionModellingDto(
    dirpath: Path,
    filename: str,
    data: Dict[str, RegressionModellingItem]
) -> None:
    """
    Serializes and writes a dictionary of RegressionModellingDto objects to a JSON file.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=False,
        validate_dir_and_extension_only=False
    )
    dataAsDictDTO: Dict[str, RegressionModellingDTO] = {
        rider_id: RegressionModellingItem.to_dataTransferObject(item)
        for rider_id, item in data.items()
    }
    myObj = RegressionModellingDTODictModel(dataAsDictDTO)
    text = myObj.model_dump_json(exclude_none=False)
    write_json_file(dirpath, filename, text)



