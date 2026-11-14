import logging
import time
from pathlib import Path

from custom_file_read_write import read_rider_compute_list_from_json, read_universe_of_riders_from_multiple_events
from jgh_exceptions import AlertMessageError
from jgh_listdictionary import JghListDictionary
from jgh_logging import log_event, setup_json_logging
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from rider_compute_item import RiderComputeItem
from simple_rider_item import SimpleRiderItem
from storage_config import DIRPATH_LOGGING

membership_files_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\!StuffFromDaveK_byJgh\riderComputeDTO_by_jgh")
generated_drs_events_results_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\DIRT\13\generated")
generated_zrl_events_results_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\WTRL\season-round-20\generated")

membership_filename = r"rider_compute_dto_as_list.json"


def distinct_by_team_name(items: list[SimpleRiderItem]) -> list[SimpleRiderItem]:
    """Return a new list keeping only the first item for each team name, in original order."""
    seen_team_names: set[str] = set()
    distinct_items: list[SimpleRiderItem] = []
    for item in items:
        if item.team_name not in seen_team_names:
            seen_team_names.add(item.team_name)
            distinct_items.append(item)
    return distinct_items


def distinct_team_names_per_zwift_id(
    riders_by_zwift_id: JghListDictionary[str, SimpleRiderItem],
) -> JghListDictionary[str, SimpleRiderItem]:
    """Return a new dictionary in which each rider's items have unique team names. The input is not modified."""
    result: JghListDictionary[str, SimpleRiderItem] = JghListDictionary[str, SimpleRiderItem]()
    for zwift_id in riders_by_zwift_id.get_keys():
        result[zwift_id] = distinct_by_team_name(riders_by_zwift_id[zwift_id])
    return result


def index_members_by_zwift_id(members: list[RiderComputeItem]) -> dict[str, RiderComputeItem]:
    """Return a lookup of members by Zwift id. If an id occurs twice, the later member wins."""
    return {member.zwift_id: member for member in members}


def match_team_names_to_members(
    members: list[RiderComputeItem],
    riders_by_zwift_id: JghListDictionary[str, SimpleRiderItem],
) -> JghListDictionary[RiderComputeItem, SimpleRiderItem]:
    """Return a new dictionary with every member as a key, holding the team-name items of matching riders.

    Riders whose Zwift id is not in the membership list are ignored. The inputs are not modified.
    """
    result: JghListDictionary[RiderComputeItem, SimpleRiderItem] = JghListDictionary[
        RiderComputeItem, SimpleRiderItem
    ]()
    for member in members:
        result.insert_key(member)

    members_by_zwift_id = index_members_by_zwift_id(members)
    for zwift_id in riders_by_zwift_id.get_keys():
        found_member = members_by_zwift_id.get(zwift_id)
        if found_member is None:
            continue
        for rider_team_name_item in riders_by_zwift_id[zwift_id]:
            result.append_value_to_list(found_member, rider_team_name_item)
    return result


def build_lookup_rows(
    team_names_by_member: JghListDictionary[RiderComputeItem, SimpleRiderItem],
) -> list[tuple[RiderComputeItem, str]]:
    """Return (member, 'team A | team B') rows for members with team names, sorted by team names then name."""
    rows: list[tuple[RiderComputeItem, str]] = []
    for member in team_names_by_member.get_keys():
        items = sorted(team_names_by_member[member], key=lambda item: item.team_name.casefold())
        if len(items) == 0:
            continue
        rows.append((member, " | ".join(item.team_name for item in items)))

    rows.sort(key=lambda row: (row[1].casefold(), str(row[0].name).casefold()))
    return rows


def format_lookup_row(member: RiderComputeItem, concatenated_team_names: str) -> str:
    return f"{member.zwift_id!s:<10} {member.name!s:<25} {concatenated_team_names}"


def find_configuration_error(dirpaths: list[Path], filenames: list[str]) -> Exception | None:
    """Return the first problem found with the directories and filenames, or None if all are valid."""
    try:
        throw_if_any_dirpath_invalid_or_not_exists(dirpaths)
        throw_if_any_filename_invalid(filenames)
    except Exception as err:
        return err
    return None


def main01() -> None:
    print("Tool starting")

    configuration_error = find_configuration_error(
        [membership_files_dirpath, generated_drs_events_results_dirpath, generated_zrl_events_results_dirpath],
        [membership_filename],
    )
    if configuration_error is not None:
        print(configuration_error)
        return

    # step 1: read membership master list. read DRS riders from all events in season
    print(
        f"\nreading membership master list\n   Dirpath: {membership_files_dirpath}\n   Filename: {membership_filename}"
    )
    members: list[RiderComputeItem] = read_rider_compute_list_from_json(membership_files_dirpath, membership_filename)
    print(f"\nriders read\n   {len(members)}")

    print(f"\nreading DRS riders from all events in season\n   Dirpath: {generated_drs_events_results_dirpath}")
    drs_riders_dict: JghListDictionary[str, SimpleRiderItem] = read_universe_of_riders_from_multiple_events(
        generated_drs_events_results_dirpath
    )
    print(f"\nriders\n   {drs_riders_dict.count_of_keys}")

    drs_riders_with_unique_team_names = distinct_team_names_per_zwift_id(drs_riders_dict)
    print(f"\nteam names\n   {drs_riders_with_unique_team_names.count_of_values}")

    # step 2: match DRS team name/s to members
    print("\nadding DRS team name/s")
    team_names_by_member = match_team_names_to_members(members, drs_riders_with_unique_team_names)
    print(f"\nresulting\n   Team names added in total: {team_names_by_member.count_of_values}")

    # step 3: build and print member names|team names lookup list
    print("\nmember names | team names lookup list")
    print(f"{'ZwiftId':<10} {'Name':<25} Team names")
    for member, concatenated_team_names in build_lookup_rows(team_names_by_member):
        print(format_lookup_row(member, concatenated_team_names))


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
