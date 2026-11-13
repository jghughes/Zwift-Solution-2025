import logging
import time
from pathlib import Path

from custom_file_read_write import read_rider_compute_list_from_json, read_universe_of_riders_from_multiple_events
from jgh_exceptions import AlertMessageError
from jgh_listdictionary import JghListDictionary
from jgh_logging import log_event, setup_json_logging
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from rider_compute_item import RiderComputeItem
from rider_team_name_item import RiderTeamNameItem
from storage_config import DIRPATH_LOGGING

membership_list_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\!StuffFromDaveK_byJgh\riderComputeDTO_by_jgh")
generated_results_for_drs_events_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\DIRT\13\generated")
generated_results_for_zrl_events_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\WTRL\season-round-20\generated")

membership_list_fileName = r"rider_compute_dto_as_list.json"


def main01() -> None:

    print("Tool starting")

    try:
        throw_if_any_dirpath_invalid_or_not_exists(
            [membership_list_dirpath, generated_results_for_drs_events_dirpath, generated_results_for_zrl_events_dirpath]
        )
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([membership_list_fileName])
    except Exception as err:
        print(err)
        return

    # ===========================
    print(f"\nreading membershiplist\n   Dirpath: {membership_list_dirpath}\n   Filename: {membership_list_fileName}")
    membership_list : list[RiderComputeItem] = read_rider_compute_list_from_json(membership_list_dirpath, membership_list_fileName)
    _answer_list_dict : JghListDictionary[RiderComputeItem, RiderTeamNameItem] = JghListDictionary[RiderComputeItem,RiderTeamNameItem]()
    for member in membership_list:
        _answer_list_dict.insert_key(member)
    print(f"\nriders read\n   Number: {_answer_list_dict.count_of_keys}")
    # ===========================

    # ===========================
    print(f"\nreading DRS riders from all events in season\n   Dirpath: {generated_results_for_drs_events_dirpath}")
    drs_riders_dict : JghListDictionary[str, RiderTeamNameItem] = read_universe_of_riders_from_multiple_events(generated_results_for_drs_events_dirpath)
    print(f"\nriders\n   Number: {drs_riders_dict.count_of_keys}")

    for zwift_id in drs_riders_dict.get_keys():
        seen_team_names : set[str] = set()
        items_with_unique_team_names : list[RiderTeamNameItem] = []
        for item in drs_riders_dict[zwift_id]:
            if item.team_name not in seen_team_names:
                seen_team_names.add(item.team_name)
                items_with_unique_team_names.append(item)
        drs_riders_dict[zwift_id] = items_with_unique_team_names
    print(f"\nteam names\n   Number: {drs_riders_dict.count_of_values}")
    # ===========================

    # ===========================
    print("\nadding master list name and DRS name/s to lookup dict of names per rider")
    count_of_names : int = 0

    members_by_zwift_id : dict[str, RiderComputeItem] = {member.zwift_id: member for member in membership_list}

    for zwift_id in drs_riders_dict.get_keys():
        member = members_by_zwift_id.get(zwift_id)
        if member is None:
            continue
        for rider_team_name_item in drs_riders_dict[zwift_id]:
            _answer_list_dict.append_value_to_list(member, rider_team_name_item)
            count_of_names += 1
    print(f"\nresulting\n   Number of names added in total: {count_of_names}")
    # ===========================

    # ===========================
    print("\nrider names|team names lookup list")
    print(f"{'ZwiftId':<10} {'Name':<25} Team names")
    rows : list[tuple[RiderComputeItem, str]] = []
    for member in _answer_list_dict.get_keys():
        team_name_items = sorted(_answer_list_dict[member], key=lambda item: item.team_name.casefold())
        if len(team_name_items) == 0:
            continue
        rows.append((member, " | ".join([item.team_name for item in team_name_items])))

    rows.sort(key=lambda row: (row[1].casefold(), str(row[0].name).casefold()))

    for member, concatenated_team_names in rows:
        print(f"{member.zwift_id!s:<10} {member.name!s:<25} {concatenated_team_names}")
    # ===========================





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
