"""
Filters and re-exports a subset of RiderStatsItems for specified teams.

Reads the full list of RiderStatsItems, keeps only the riders on the rosters of the
requested teams in RepositoryOfTeamRosters, and writes the result to the scratchpad
folder as an abridged JSON list.
"""

import logging
import time
from pathlib import Path

import pandas as pd

from custom_file_read_write import read_rider_stats_list_from_json, write_rider_stats_list_to_json
from jgh_exceptions import AlertMessageError
from jgh_logging import log_event, setup_json_logging
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_read_write import (
    write_dataframe_as_xlsx_file,
)
from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_stats_item import RiderStatsItem
from storage_config import (
    DIRPATH_LOGGING,
    DIRPATH_RIDER_STATS_DTO,
    DIRPATH_RUBBISH_SCRATCHPAD,
    FILENAME_ABRIDGED_RIDER_STATS_DTO_JSON_LIST,
    FILENAME_ABRIDGED_RIDER_STATS_DTO_XLSX_LIST,
    FILENAME_RIDER_STATS_DTO_JSON_LIST,
)


def validate_dirpaths_and_filenames() -> None:
    """
    Check that the input and output directories exist and that the output filename is valid.

    Raises:
        Exception: If any required directory or filename is invalid or does not exist.
    """
    throw_if_any_dirpath_invalid_or_not_exists(
        [
            Path(DIRPATH_RIDER_STATS_DTO),
            Path(DIRPATH_RUBBISH_SCRATCHPAD),
        ]
    )
    throw_if_any_filename_invalid([FILENAME_ABRIDGED_RIDER_STATS_DTO_JSON_LIST])


def validate_that_teams_are_in_repository(team_names: list[str]) -> None:
    """
    Check that every requested team exists in RepositoryOfTeamRosters.

    Raises:
        AlertMessageError: If any team is not in the repository.
    """
    dict_of_teams = RepositoryOfTeamRosters.get_dict_of_teams_and_their_riders()
    for team_name in team_names:
        if team_name not in dict_of_teams:
            raise AlertMessageError(message=f"Team '{team_name}' is not in the repository.")


def save_as_excel_file(
    output_dirPath: Path,
    output_filename: str,
    rider_stats_items: list[RiderStatsItem],
) -> None:
    """
    Serialize riderStatsItems to DTO and save as an Excel file.
    Args:
        rider_stats_items: List of RiderStatsItems to be saved.
        output_dirPath: Directory where the Excel file will be saved.
        output_filename: Name of the Excel file to be saved.
    """
    dto_list = [RiderStatsItem.to_dataTransferObject(rider) for rider in rider_stats_items]
    dto_list_dataframe_column_order: list[str] = [
        "row",
        "full_name",
        # "zwift_country_code3",
        # "zwift_zftp_wkg",
        # "velo_cat_label",
        # "route_name",
        "route_sec",
        # "route_hh_mm_ss",
        "route_watts",
        "route_wkg",
        # "route_kph",
    ]
    # dto_list_dataframe_column_order = list(dto_list[0].model_fields.keys()) #print all columns in the order they are defined in the DTO
    dto_list_dataframe_rows = [dto.model_dump(exclude_none=False) for dto in dto_list]
    df = pd.DataFrame(dto_list_dataframe_rows, columns=dto_list_dataframe_column_order)
    write_dataframe_as_xlsx_file(output_dirPath, output_filename, df)


def main(team_names: list[str]) -> None:
    """
    Run the whole workflow: validate, read, filter, then write.

    Reads all RiderStatsItems and writes out only those whose zwift_id is on the roster
    of one of the specified teams, preserving the original order.

    Args:
        team_names: Names of the teams in RepositoryOfTeamRosters.

    Raises:
        AlertMessageError: If any team is missing from RepositoryOfTeamRosters.
        Exception: If a required path or filename is invalid.
    """
    validate_dirpaths_and_filenames()
    validate_that_teams_are_in_repository(team_names)
    print("\nValidated that all required directories and filenames exist and are valid.\n")

    rider_stats_items: list[RiderStatsItem] = read_rider_stats_list_from_json(
        Path(DIRPATH_RIDER_STATS_DTO), FILENAME_RIDER_STATS_DTO_JSON_LIST
    )
    print(
        f"\nRead {len(rider_stats_items)} RiderStatsItems\n from "
        f"{Path(DIRPATH_RIDER_STATS_DTO) / FILENAME_RIDER_STATS_DTO_JSON_LIST}.\n"
    )

    dict_of_all_teams_in_repository = RepositoryOfTeamRosters.get_dict_of_teams_and_their_riders()
    zwift_ids_of_riders_in_requested_teams: set[str] = {
        zwift_id for team_name in team_names for zwift_id, _ in dict_of_all_teams_in_repository[team_name]
    }
    abridged_list_of_riders: list[RiderStatsItem] = [
        rider for rider in rider_stats_items if rider.zwift_id in zwift_ids_of_riders_in_requested_teams
    ]
    write_rider_stats_list_to_json(
        Path(DIRPATH_RUBBISH_SCRATCHPAD), FILENAME_ABRIDGED_RIDER_STATS_DTO_JSON_LIST, abridged_list_of_riders
    )
    print(
        f"\nWrote {len(abridged_list_of_riders)}/{len(rider_stats_items)} RiderStatsItems\n to "
        f"{Path(DIRPATH_RUBBISH_SCRATCHPAD) / FILENAME_ABRIDGED_RIDER_STATS_DTO_JSON_LIST}.\n"
    )
    save_as_excel_file(
        Path(DIRPATH_RUBBISH_SCRATCHPAD), FILENAME_ABRIDGED_RIDER_STATS_DTO_XLSX_LIST, abridged_list_of_riders
    )

    print(
        f"\nWrote {len(abridged_list_of_riders)}/{len(rider_stats_items)} RiderStatsItems\n to "
        f"{Path(DIRPATH_RUBBISH_SCRATCHPAD) / FILENAME_ABRIDGED_RIDER_STATS_DTO_XLSX_LIST}.\n"
    )


if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        # _team_names = ["rangers"]
        _team_names = ["rangers", "drifters", "outlaws", "copperheads", "sidewinders"]

        start_time = time.time()
        main(_team_names)
        end_time = time.time()

        success_msg = f"Success: main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(logger, message=alert_err.message, level=logging.INFO, exception=alert_err)
        print(f"\n{alert_err.message}\n")
    except Exception as ex:
        log_event(
            logger, message=f"Unhandled Exception: {ex}", level=logging.ERROR, exception=ex
        )  # Pass the original exception object
        print(f"\nUnhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n\n")
