import logging
import time
from pathlib import Path

import pandas as pd

from custom_file_read_write import (
    read_rider_compute_list_from_json,
    read_universe_of_riders_from_multiple_events_by_rider_name,
    read_universe_of_riders_from_multiple_events_by_zwift_id,
    write_team_member_list_to_json,
)
from jgh_exceptions import AlertMessageError
from jgh_listdictionary import JghListDictionary
from jgh_logging import log_event, setup_json_logging
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_read_write import write_dataframe_as_xlsx_file
from rider_compute_item import RiderComputeItem
from storage_config import (
    DIRPATH_LOGGING,
    DIRPATH_RIDER_COMPUTE_DTO,
    DIRPATH_TEAM_MEMBER_DTO,
    FILENAME_RIDER_COMPUTE_DTO_JSON_LIST,
    FILENAME_TEAM_MEMBER_DTO_JSON_LIST,
    FILENAME_TEAM_MEMBER_DTO_XLSX_LIST,
)
from team_member_item import TeamMemberItem

rider_compute_dirpath = Path(DIRPATH_RIDER_COMPUTE_DTO)
generated_drs_events_results_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\DIRT\13\generated")
generated_zrl_events_results_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\WTRL\season-round-20\generated")

rider_compute_filename = FILENAME_RIDER_COMPUTE_DTO_JSON_LIST

generated_teamMember_lists_dirpath = Path(DIRPATH_TEAM_MEMBER_DTO)
drs_teamMember_filename_as_json = FILENAME_TEAM_MEMBER_DTO_JSON_LIST
drs_teamMember_filename_as_xlsx = FILENAME_TEAM_MEMBER_DTO_XLSX_LIST


def build_distinct_team_member_items_by_team_name(team_member_items: list[TeamMemberItem]) -> list[TeamMemberItem]:
    """Return a new list keeping only the first item for each team name, in original order."""
    seen_team_names: set[str] = set()
    distinct_team_member_items: list[TeamMemberItem] = []
    for team_member_item in team_member_items:
        if team_member_item.team_name not in seen_team_names:
            seen_team_names.add(team_member_item.team_name)
            distinct_team_member_items.append(team_member_item)
    return distinct_team_member_items


def build_distinct_team_member_items_dict_by_zwift_id(
    team_member_items_dict_by_zwift_id: JghListDictionary[str, TeamMemberItem],
) -> JghListDictionary[str, TeamMemberItem]:
    """Return a new dictionary in which each Zwift id's team member items have unique team names. The input is not modified."""
    distinct_team_member_items_dict_by_zwift_id: JghListDictionary[str, TeamMemberItem] = JghListDictionary[
        str, TeamMemberItem
    ]()
    for zwift_id in team_member_items_dict_by_zwift_id.get_keys():
        distinct_team_member_items_dict_by_zwift_id[zwift_id] = build_distinct_team_member_items_by_team_name(
            team_member_items_dict_by_zwift_id[zwift_id]
        )
    return distinct_team_member_items_dict_by_zwift_id


def build_distinct_team_member_items_dict_by_rider_name(
    team_member_items_dict_by_rider_name: JghListDictionary[str, TeamMemberItem],
) -> JghListDictionary[str, TeamMemberItem]:
    """Return a new dictionary in which each rider name's team member items have unique team names. The input is not modified."""
    distinct_team_member_items_dict_by_rider_name: JghListDictionary[str, TeamMemberItem] = JghListDictionary[
        str, TeamMemberItem
    ]()
    for rider_name in team_member_items_dict_by_rider_name.get_keys():
        distinct_team_member_items_dict_by_rider_name[rider_name] = build_distinct_team_member_items_by_team_name(
            team_member_items_dict_by_rider_name[rider_name]
        )
    return distinct_team_member_items_dict_by_rider_name


def build_rider_compute_items_dict_by_zwift_id(
    rider_compute_items: list[RiderComputeItem],
) -> dict[str, RiderComputeItem]:
    """Return a lookup of rider compute items by Zwift id. If an id occurs twice, the later item wins."""
    return {rider_compute_item.zwift_id: rider_compute_item for rider_compute_item in rider_compute_items}


def match_team_member_items_to_rider_compute_items(
    rider_compute_items: list[RiderComputeItem],
    team_member_items_dict_by_zwift_id: JghListDictionary[str, TeamMemberItem],
) -> JghListDictionary[RiderComputeItem, TeamMemberItem]:
    """Return a new dictionary with every rider compute item as a key, holding the team member items of matching riders.

    Team member items whose Zwift id is not in the rider compute items are ignored. The inputs are not modified.
    """
    team_member_items_dict_by_rider_compute_item: JghListDictionary[RiderComputeItem, TeamMemberItem] = (
        JghListDictionary[RiderComputeItem, TeamMemberItem]()
    )
    for rider_compute_item in rider_compute_items:
        team_member_items_dict_by_rider_compute_item.insert_key(rider_compute_item)

    rider_compute_items_dict_by_zwift_id = build_rider_compute_items_dict_by_zwift_id(rider_compute_items)
    for zwift_id in team_member_items_dict_by_zwift_id.get_keys():
        found_rider_compute_item = rider_compute_items_dict_by_zwift_id.get(zwift_id)
        if found_rider_compute_item is None:
            continue
        for team_member_item in team_member_items_dict_by_zwift_id[zwift_id]:
            team_member_items_dict_by_rider_compute_item.append_value_to_list(
                found_rider_compute_item, team_member_item
            )
    return team_member_items_dict_by_rider_compute_item


def build_lookup_rows_per_rider_compute_item(
    team_member_items_dict_by_rider_compute_item: JghListDictionary[RiderComputeItem, TeamMemberItem],
) -> list[tuple[RiderComputeItem, str]]:
    """Return (rider compute item, 'team A | team B') rows for riders with team names, sorted by team names then name."""
    rows: list[tuple[RiderComputeItem, str]] = []
    for rider_compute_item in team_member_items_dict_by_rider_compute_item.get_keys():
        team_member_items = sorted(
            team_member_items_dict_by_rider_compute_item[rider_compute_item],
            key=lambda z: z.team_name.casefold(),
        )
        if len(team_member_items) == 0:
            continue
        rows.append(
            (rider_compute_item, " | ".join(team_member_item.team_name for team_member_item in team_member_items))
        )

    rows.sort(key=lambda z: (z[1].casefold(), str(z[0].name).casefold()))
    return rows


def build_lookup_rows_per_rider_name(
    team_member_items_dict_by_rider_name: JghListDictionary[str, TeamMemberItem],
) -> list[tuple[str, str]]:
    """Return (rider name, 'team A | team B') rows for riders with team names, sorted by team names then name."""
    rows: list[tuple[str, str]] = []
    for rider_name in team_member_items_dict_by_rider_name.get_keys():
        team_member_items = sorted(
            team_member_items_dict_by_rider_name[rider_name],
            key=lambda z: z.team_name.casefold(),
        )
        if len(team_member_items) == 0:
            continue
        rows.append((rider_name, " | ".join(team_member_item.team_name for team_member_item in team_member_items)))

    rows.sort(key=lambda z: (z[1].casefold(), z[0].casefold()))
    return rows


def format_lookup_row_per_rider_name(rider_name: str, concatenated_team_names: str) -> str:
    """Return one fixed-width line: rider name, then the concatenated team names."""
    return f"{'[zwift_id]'!s:<10} {rider_name!s:<25} {concatenated_team_names}"


def format_lookup_row_per_rider_compute_item(rider_compute_item: RiderComputeItem, concatenated_team_names: str) -> str:
    """Return one fixed-width line: Zwift id, name, then the concatenated team names."""
    return f"{rider_compute_item.zwift_id!s:<10} {rider_compute_item.name!s:<25} {concatenated_team_names}"


def find_configuration_error(dirpaths: list[Path], filenames: list[str]) -> Exception | None:
    """Return the first problem found with the directories and filenames, or None if all are valid."""
    try:
        throw_if_any_dirpath_invalid_or_not_exists(dirpaths)
        throw_if_any_filename_invalid(filenames)
    except Exception as err:
        return err
    return None


def save_as_excel_file(
    output_dirPath: Path,
    output_filename: str,
    team_member_items: list[TeamMemberItem],
) -> None:
    """
    Serialize teamMemberItems to DTO and save as an Excel file.
    Args:
        team_member_items: List of TeamMemberItems to be saved.
        output_dirPath: Directory where the Excel file will be saved.
        output_filename: Name of the Excel file to be saved.
    """
    dto_list = [TeamMemberItem.to_dataTransferObject(rider) for rider in team_member_items]
    dto_list_dataframe_column_order = list(
        dto_list[0].model_fields.keys()
    )  # print all columns in the order they are defined in the DTO
    dto_list_dataframe_rows = [dto.model_dump(exclude_none=False) for dto in dto_list]
    df = pd.DataFrame(dto_list_dataframe_rows, columns=dto_list_dataframe_column_order)
    write_dataframe_as_xlsx_file(output_dirPath, output_filename, df)


def main01() -> None:
    print("Tool starting")

    configuration_error = find_configuration_error(
        [rider_compute_dirpath, generated_drs_events_results_dirpath],
        [rider_compute_filename],
    )
    if configuration_error is not None:
        print(configuration_error)
        return

    # step 1: read membership master list
    print(
        f"\nreading rider_compute_item master list\n   Dirpath: {rider_compute_dirpath}\n   Filename: {rider_compute_filename}"
    )
    rider_compute_items: list[RiderComputeItem] = read_rider_compute_list_from_json(
        rider_compute_dirpath, rider_compute_filename
    )
    print(f"\nrider compute items read\n   {len(rider_compute_items)}")

    # step 2: read DRS riders from all events in season
    print(f"\nreading DRS riders from all events in season\n   Dirpath: {generated_drs_events_results_dirpath}")
    drs_team_member_items_dict_by_zwift_id: JghListDictionary[str, TeamMemberItem] = (
        read_universe_of_riders_from_multiple_events_by_zwift_id(generated_drs_events_results_dirpath)
    )
    print(f"\nriders\n   {drs_team_member_items_dict_by_zwift_id.count_of_keys}")

    distinct_drs_team_member_items_dict_by_zwift_id = build_distinct_team_member_items_dict_by_zwift_id(
        drs_team_member_items_dict_by_zwift_id
    )
    print(f"\nteam member items\n   {distinct_drs_team_member_items_dict_by_zwift_id.count_of_values}")

    # step 3: match DRS team member items to rider compute items
    print("\nadding DRS team member items")
    team_member_items_dict_by_rider_compute_item = match_team_member_items_to_rider_compute_items(
        rider_compute_items, distinct_drs_team_member_items_dict_by_zwift_id
    )
    print(
        f"\nresulting\n   Team member items added in total: {team_member_items_dict_by_rider_compute_item.count_of_values}"
    )

    # step 4: build and print rider names|team names lookup list
    print("\nrider names | team names lookup list")
    print(f"{'ZwiftId':<10} {'Name':<25} Team names")
    for rider_compute_item, concatenated_team_names in build_lookup_rows_per_rider_compute_item(
        team_member_items_dict_by_rider_compute_item
    ):
        print(format_lookup_row_per_rider_compute_item(rider_compute_item, concatenated_team_names))

    # step 5: save team member items list to Excel file
    team_member_items_as_list: list[TeamMemberItem] = team_member_items_dict_by_rider_compute_item.get_values_for_all()
    team_member_items_as_list.sort(key=lambda z: z.team_name.casefold())
    save_as_excel_file(generated_teamMember_lists_dirpath, drs_teamMember_filename_as_xlsx, team_member_items_as_list)
    print(
        f"\nSaved team member items list to Excel file\n   Dirpath: {generated_teamMember_lists_dirpath}\n   Filename: {drs_teamMember_filename_as_xlsx}"
    )

    # step 6: save team member items list as json file
    write_team_member_list_to_json(
        generated_teamMember_lists_dirpath, drs_teamMember_filename_as_json, team_member_items_as_list
    )
    print(
        f"\nSaved team member items list to JSON file\n   Dirpath: {generated_teamMember_lists_dirpath}\n   Filename: {drs_teamMember_filename_as_json}"
    )


def main02() -> None:
    print("Tool starting")

    configuration_error = find_configuration_error(
        [rider_compute_dirpath, generated_zrl_events_results_dirpath],
        [rider_compute_filename],
    )
    if configuration_error is not None:
        print(configuration_error)
        return

    # step 1: read rider_compute_item master list
    print(
        f"\nreading rider_compute_item master list\n   Dirpath: {rider_compute_dirpath}\n   Filename: {rider_compute_filename}"
    )
    rider_compute_items: list[RiderComputeItem] = read_rider_compute_list_from_json(
        rider_compute_dirpath, rider_compute_filename
    )
    print(f"\nrider compute items read\n   {len(rider_compute_items)}")

    # step 2: read ZRL riders from all events in season
    print(f"\nreading ZRL riders from all events in season\n   Dirpath: {generated_zrl_events_results_dirpath}")
    zrl_team_member_items_dict_by_rider_name: JghListDictionary[str, TeamMemberItem] = (
        read_universe_of_riders_from_multiple_events_by_rider_name(generated_zrl_events_results_dirpath)
    )
    print(f"\nriders\n   {zrl_team_member_items_dict_by_rider_name.count_of_keys}")

    distinct_zrl_team_member_items_dict_by_rider_name = build_distinct_team_member_items_dict_by_rider_name(
        zrl_team_member_items_dict_by_rider_name
    )
    print(f"\nteam member items\n   {distinct_zrl_team_member_items_dict_by_rider_name.count_of_values}")

    # step 3: print rider names|team names lookup list
    print("\nrider names | team names lookup list")
    print(f"{'ZwiftId':<10} {'Name':<25} Team names")
    for rider_name, concatenated_team_names in build_lookup_rows_per_rider_name(
        distinct_zrl_team_member_items_dict_by_rider_name
    ):
        print(format_lookup_row_per_rider_name(rider_name, concatenated_team_names))


# main runner
if __name__ == "__main__":
    from jgh_logging import log_event, setup_json_logging
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        print("Starting script...be patient, this may or may not take a while...\n")

        start_time = time.time()
        main01()
        # main02()
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
