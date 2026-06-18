from pathlib import Path
from typing import Dict, List, Any, Type
import json
from collections import defaultdict

import pandas as pd

from jgh_path_helpers import throw_if_file_path_ingredients_invalid_or_not_exists
from jgh_read_write import read_text, write_text_with_json_file_extension, write_dataframe_as_csv_file, write_dataframe_as_xlsx_file
from regression_modelling_dto import RegressionModellingDTO, RegressionModellingDTODictModel
from regression_modelling_item import RegressionModellingItem
from rider_compute_item import RiderComputeItem
from rider_compute_dto import RiderComputeDtoDictModel
from rider_stats_item import RiderStatsItem
from rider_stats_dto import RiderStatsDtoListModel


from zwiftpower_flattened_90_day_watts_dto import ZwiftPower90DayWattsDTODictModel, ZwiftPowerFlattened90DayWattsDTO
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem 

def read_rider_compute_dict_from_json(dirpath: Path, filename: str) -> Dict[str, RiderComputeItem]:
    """
    Reads a JSON file and deserializes its contents into a dictionary of RiderComputeItem domain objects.

    Args:
        dirpath: Directory path containing the target file.
        filename: Name of the JSON file (without extension).

    Returns:
        A defaultdict of RiderComputeItem instances keyed by rider ID string,
        defaulting to an empty RiderComputeItem for missing keys.

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
    answer = RiderComputeDtoDictModel.model_validate(something, strict=True).root
    return defaultdict(
        RiderComputeItem,
        {
            key: RiderComputeItem.from_dataTransferObject(dto)
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

def read_rider_stats_list_from_json_as_dict(filepath: Path) -> Dict[str, RiderStatsItem]:

    # parse filepath to get directory and filename
    dirPath = filepath.parent
    filename = filepath.name
    rider_stats_items = read_rider_stats_list_from_json(dirPath, filename)

    answer: Dict[str,RiderStatsItem] = {}

    # store RiderStatsItems in a dictionary keyed by zwift_id
    for item in rider_stats_items:
        answer[item.zwift_id] = item

    return answer

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

def read_json_list_and_export_tabular(
    input_dirpath: Path,
    input_filename: str,
    list_model_class: Type[Any],
    output_dirpath: Path,
) -> pd.DataFrame:
    """
    Reads a JSON list file, validates it with a Pydantic list-root model,
    and writes the validated DTOs to both a CSV and an XLSX file.
    Output files are written to output_dirpath using the same stem as
    input_filename, with .csv and .xlsx extensions respectively.

    Args:
        input_dirpath:   Directory containing the source JSON file.
        input_filename:  Filename of the JSON list file (with extension).
        list_model_class:  A Pydantic list-root model class whose .root is List[DTO].
        output_dirpath:  Directory where the CSV and XLSX files will be written.

    Returns:
        A pandas DataFrame representing the validated DTO list, with columns
        ordered according to the DTO's model_fields declaration.

    Raises:
        ValueError:      If any path or filename argument is invalid, or the
                         JSON list is empty after validation.
        ValidationError: If the JSON does not conform to the list model schema.
        IOError:         If reading or writing any file fails.
    """
    stem = Path(input_filename).stem

    raw_text = read_text(input_dirpath, input_filename)
    raw_data = json.loads(raw_text)

    validated_list = list_model_class.model_validate(raw_data, strict=True).root

    if not validated_list:
        raise ValueError(f"No DTOs found after validating '{input_filename}'.")

    column_order = list(validated_list[0].model_fields.keys())
    rows = [dto.model_dump(exclude_none=False) for dto in validated_list]
    dataframe = pd.DataFrame(rows, columns=column_order)

    write_dataframe_as_csv_file(output_dirpath, f"{stem}.csv", dataframe)
    write_dataframe_as_xlsx_file(output_dirpath, f"{stem}.xlsx", dataframe)

    return dataframe