import logging
import time
from pathlib import Path

from custom_file_read_write import read_rider_stats_list_from_json, read_teams_names_per_rider_from_event_result_files
from jgh_exceptions import AlertMessageError
from jgh_listdictionary import JghListDictionary
from jgh_logging import log_event, setup_json_logging
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from rider_stats_item import RiderStatsItem
from storage_config import DIRPATH_LOGGING

rider_stats_masterlist_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\!StuffFromDaveK_byJgh\riderStatsDTO_by_jgh")
generated_results_for_drs_events_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\DIRT\13\generated")
generated_results_for_zrl_events_dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\WTRL\season-round-20\generated")

rider_stats_masterlist_filename = r"rider_stats_dto_as_list.json"


def main01() -> None:

    print("Tool starting")

    try:
        throw_if_any_dirpath_invalid_or_not_exists(
            [rider_stats_masterlist_dirpath, generated_results_for_drs_events_dirpath, generated_results_for_zrl_events_dirpath]
        )
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([rider_stats_masterlist_filename])
    except Exception as err:
        print(err)
        return

    # ===========================
    print(f"\nreading rider stats master list\n   Dirpath: {rider_stats_masterlist_dirpath}\n   Filename: {rider_stats_masterlist_filename}")
    rider_stats_master_list : list[RiderStatsItem] = read_rider_stats_list_from_json(rider_stats_masterlist_dirpath, rider_stats_masterlist_filename)
    _answer_as_lookup_dict_of_teamnames_per_rider : JghListDictionary[str, str] = JghListDictionary[str,str]()
    for rider_stats_item in rider_stats_master_list:
        _answer_as_lookup_dict_of_teamnames_per_rider.insert_key(rider_stats_item.zwift_id)
    print(f"\nriders read\n   Number: {len(_answer_as_lookup_dict_of_teamnames_per_rider.get_keys())}")
    # ===========================

    # ===========================
    print(f"\nreading DRS riders from all events in season\n   Dirpath: {generated_results_for_drs_events_dirpath}")
    _dict_of_drs_team_names_per_rider : JghListDictionary[str, str] = read_teams_names_per_rider_from_event_result_files(generated_results_for_drs_events_dirpath)
    print(f"\nriders\n   Number: {_dict_of_drs_team_names_per_rider.number_of_keys}")
    _dict_of_drs_team_names_per_rider.deduplicate_values_in_all_lists()
    print(f"\nteam names\n   Number: {_dict_of_drs_team_names_per_rider.number_of_values}")
    # ===========================

    # ===========================
    # print("\nadding DRS team name/s to lookup dict of team names per rider")
    # _answer_as_lookup_dict_of_teamnames_per_rider = JghListDictionary[str, str]()
    # count_of_team_names : int = 0
    # for zwift_id in _dict_of_drs_team_names_per_rider.get_keys():
    #     if zwift_id in _answer_as_lookup_dict_of_teamnames_per_rider:
    #         team_names = _dict_of_drs_team_names_per_rider.get_values(zwift_id)
    #         for name in team_names:
    #             _answer_as_lookup_dict_of_teamnames_per_rider.append_value_to_list(zwift_id, name)
    #             count_of_team_names += 1
    # print(f"\nresulting \n   Number of team names added in total: {count_of_team_names}")
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
