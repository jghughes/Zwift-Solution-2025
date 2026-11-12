from pathlib import Path
from typing import Any
import json
from collections import defaultdict

import pandas as pd
from jgh_listdictionary import JghListDictionary
from jgh_path_helpers import throw_if_file_path_ingredients_invalid_or_not_exists
from jgh_read_write import list_filePaths_recursive, read_text, write_text_with_json_file_extension, write_dataframe_as_csv_file, write_dataframe_as_xlsx_file
from regression_modelling_dto import RegressionModellingDTO, RegressionModellingDTODictModel
from regression_modelling_item import RegressionModellingItem
from rider_compute_item import RiderComputeItem
from rider_compute_dto import RiderComputeDtoDictModel
from rider_stats_item import RiderStatsItem
from rider_stats_dto import RiderStatsDtoListModel


from zwiftpower_flattened_90_day_watts_dto import ZwiftPower90DayWattsDTODictModel, ZwiftPowerFlattened90DayWattsDTO
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem 

# from rider_team_name_dto import RiderTeamNameDTO
from rider_team_name_dto import RiderTeamNameDtoListModel
from rider_team_name_item import RiderTeamNameItem

def read_rider_compute_dict_from_json(dirpath: Path, filename: str) -> dict[str, RiderComputeItem]:
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

def read_single_event_result_file_to_obtain_name_of_teams_for_each_rider_from_json(dirpath: Path, filename: str) -> list[RiderStatsItem]:
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


def read_zwiftpower_90day_watts_dict_from_json(dirpath: Path, filename: str) -> dict[str, ZwiftPowerFlattened90dayWattsItem]:
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

def read_regression_modelling_dict_from_json(dirpath: Path, filename: str) -> dict[str, RegressionModellingItem]:
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

def write_zwiftpower_90day_watts_dict_to_json(dirpath: Path, filename: str, data: dict[str, ZwiftPowerFlattened90dayWattsItem]) -> None:
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
    dataAsDictDTO: dict[str, ZwiftPowerFlattened90DayWattsDTO] = {
        rider_id: ZwiftPowerFlattened90dayWattsItem.to_dataTransferObject(item)
        for rider_id, item in data.items()
    }
    myObj = ZwiftPower90DayWattsDTODictModel(dataAsDictDTO)
    text = myObj.model_dump_json(exclude_none=False)
    write_text_with_json_file_extension(dirpath, filename, text)

def write_regression_modelling_dict_to_json(dirpath: Path, filename: str, data: dict[str, RegressionModellingItem]) -> None:
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
    dataAsDictDTO: dict[str, RegressionModellingDTO] = {
        rider_id: RegressionModellingItem.to_dataTransferObject(item)
        for rider_id, item in data.items()
    }
    myObj = RegressionModellingDTODictModel(dataAsDictDTO)
    text = myObj.model_dump_json(exclude_none=False)
    write_text_with_json_file_extension(dirpath, filename, text)

def read_event_file_for_teams_for_riders(dirpath: Path, filename: str) -> list[RiderTeamNameItem]:
    """
    Reads a JSON file and deserializes its contents into a list of RiderTeamNameItem domain objects.

    Args:
        dirpath: Directory path containing the target file.
        filename: Name of the JSON file (without extension).

    Returns:
        A list of RiderTeamNameItem instances populated from the JSON data.

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
    answer_as_dto = RiderTeamNameDtoListModel.model_validate(something, strict=True).root
    answer_as_item = [RiderTeamNameItem.from_dataTransferObject(dto) for dto in answer_as_dto]
    return answer_as_item

def read_teams_per_rider_from_event_result_files(dirpath: Path) -> JghListDictionary[str, str]:
    """
    Reads every JSON event-result file in a directory and builds a lookup of
    the distinct team names associated with each rider across all events.

    Args:
        dirpath: Directory containing the event-result JSON files.

    Returns:
        A JghListDictionary mapping each rider's zwift_id to a list of the
        distinct team names that rider appears under.

    Raises:
        ValueError: If the directory or any file path is invalid or a file does not exist.
    """
    file_paths: list[Path] = list_filePaths_recursive(dirpath, "*.json")

    answer_as_list_dict: JghListDictionary[str, str] = JghListDictionary()

    for file_path in file_paths:
        file_name = file_path.name
        rider_items = read_event_file_for_teams_for_riders(dirpath, file_name)
        for item in rider_items:
            answer_as_list_dict.append_value_to_list(item.zwift_id, item.team_name)

    answer_as_list_dict.deduplicate_values_in_all_lists()

    return answer_as_list_dict

def read_json_list_and_export_tabular(
    input_dirpath: Path,
    input_filename: str,
    list_model_class: type[Any],
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