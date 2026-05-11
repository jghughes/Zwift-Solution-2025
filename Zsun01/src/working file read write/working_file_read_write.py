from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import json

from jgh_path_helpers import throw_if_file_path_ingredients_invalid_or_not_exists
from jgh_read_write import read_text, write_text_with_json_file_extension
from regression_modelling_dto import RegressionModellingDTO, RegressionModellingDTODictModel
from regression_modelling_item import RegressionModellingItem
from rider_brute_item import RiderBruteItem
from rider_brute_dto import RiderBruteDtoDictModel
from rider_stats_item import RiderStatsItem
from rider_stats_dto import RiderStatsDtoListModel


from zwiftpower_flattened_90_day_watts_dto import ZwiftPower90DayWattsDTODictModel, ZwiftPowerFlattened90DayWattsDTO
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem 

def read_rider_brute_dict_from_json(dirpath: Path, filename: str) -> Dict[str, RiderBruteItem]:
    """
    Reads a JSON file and deserializes its contents into a dictionary of RiderBruteItem domain objects.

    Args:
        dirpath: Directory path containing the target file.
        filename: Name of the JSON file (without extension).

    Returns:
        A defaultdict of RiderBruteItem instances keyed by rider ID string,
        defaulting to an empty RiderBruteItem for missing keys.

    Raises:
        ValueError: If the directory or file path is invalid or the file does not exist.
    """

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

def read_rider_stats_list_from_json(dirpath: Path, filename: str) -> List[RiderStatsItem]:
    """
    Reads a JSON file and deserializes its contents into a list of RiderStatsItem domain objects.

    Args:
        dirpath: Directory path containing the target file.
        filename: Name of the JSON file (without extension).

    Returns:
        A list of RiderStatsItem instances populated from the JSON data.

    Raises:
        ValueError: If the directory or file path is invalid or the file does not exist.
    """
    throw_if_file_path_ingredients_invalid_or_not_exists(
        dirpath,
        filename,
        ".json",
        require_file_exists_for_read=True,
        validate_dir_and_extension_only=False
    )
    text = read_text(dirpath, filename)
    something = json.loads(text)
    answer = RiderStatsDtoListModel.model_validate(something, strict=True).root
    return [RiderStatsItem.from_dataTransferObject(dto) for dto in answer]

def read_zwiftpower_90day_watts_dict_from_json(dirpath: Path, filename: str) -> Dict[str, ZwiftPowerFlattened90dayWattsItem]:
    """
    Reads a JSON file and deserializes its contents into a dictionary of ZwiftPowerFlattened90dayWattsItem domain objects.

    Args:
        dirpath: Directory path containing the target file.
        filename: Name of the JSON file (without extension).

    Returns:
        A defaultdict of ZwiftPowerFlattened90dayWattsItem instances keyed by rider ID string,
        defaulting to an empty ZwiftPowerFlattened90dayWattsItem for missing keys.

    Raises:
        ValueError: If the directory or file path is invalid or the file does not exist.
    """

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

def read_regression_modelling_dict_from_json(dirpath: Path, filename: str) -> Dict[str, RegressionModellingItem]:
    """
    Reads a JSON file and deserializes its contents into a dictionary of RegressionModellingItem domain objects.

    Args:
        dirpath: Directory path containing the target file.
        filename: Name of the JSON file (without extension).

    Returns:
        A defaultdict of RegressionModellingItem instances keyed by rider ID string,
        defaulting to an empty RegressionModellingItem for missing keys.

    Raises:
        ValueError: If the directory or file path is invalid or the file does not exist.
    """

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

def write_zwiftpower_90day_watts_dict_to_json(dirpath: Path, filename: str, data: Dict[str, ZwiftPowerFlattened90dayWattsItem]) -> None:
    """
    Serializes and writes a dictionary of ZwiftPowerFlattened90dayWattsItem domain objects to a JSON file.

    Args:
        dirpath: Directory path where the output file will be written.
        filename: Name of the JSON file (without extension).
        data: Dictionary of ZwiftPowerFlattened90dayWattsItem instances keyed by rider ID string.

    Returns:
        None.

    Raises:
        ValueError: If the directory or file path is invalid.
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
    write_text_with_json_file_extension(dirpath, filename, text)

def write_regression_modelling_dict_to_json(dirpath: Path, filename: str, data: Dict[str, RegressionModellingItem]) -> None:
    """
    Serializes and writes a dictionary of RegressionModellingItem domain objects to a JSON file.

    Args:
        dirpath: Directory path where the output file will be written.
        filename: Name of the JSON file (without extension).
        data: Dictionary of RegressionModellingItem instances keyed by rider ID string.

    Returns:
        None.

    Raises:
        ValueError: If the directory or file path is invalid.
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
    write_text_with_json_file_extension(dirpath, filename, text)



