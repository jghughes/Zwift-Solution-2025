import asyncio
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_string import format_seconds_to_hh_mm_ss
from storage_config import (
    DIRPATH_ZWIFT_FILES,  
    DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, 
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    )
from storage_config import (
    FILENAME_RIDER_COMPUTE_DTO_JSON_DICT, 
    FILENAME_RIDER_COMPUTE_DTO_XLSX_LIST, 
    )
from repository_of_riders import RepositoryOfRiders
import json
import time
from pathlib import Path
from typing import List
from jgh_read_write import read_text
from jgh_string import  format_seconds_to_hh_mm_ss
from storage_config import DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES
import logging
from jgh_exceptions import AlertMessageError

async def reconcile_lists_and_save():
    print("starting script\n")
    logger = logging.getLogger()

    try:
        throw_if_any_dirpath_invalid_or_not_exists([
            Path(DIRPATH_ZWIFT_FILES),
            Path(DIRPATH_ZWIFTRACINGAPP_FILES),
            Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES),
            Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT)]
        )
    except Exception as err:
        logger.error(f"Directory validation error: {err}", exc_info=True)
        print(err)
        return
    try:
        throw_if_any_filename_invalid([
            FILENAME_RIDER_COMPUTE_DTO_JSON_DICT, 
            FILENAME_RIDER_COMPUTE_DTO_XLSX_LIST]
        )
    except Exception as err:
        logger.error(f"Filename validation error: {err}", exc_info=True)
        print(err)
        return
    print("local dir_paths and filenames validated.")

    url_for_club_members_on_zwiftpower = f"https://data.zsunr.com/riders/json/zwiftpower/{_zp_club_members_filename}"
    print(f"\nfetch single file of club members listed in: {_zp_club_members_filename}")
    print(f"url: {url_for_club_members_on_zwiftpower}")
    text = read_text( Path(DIRPATH_ZWIFTPOWER), _zp_club_members_filename)
    zwiftIDs: List[str] = json.loads(text)
    print(f"number of member IDs in file: {len(zwiftIDs)}")
    print("\nTHE MEAT: populate repository of riders.")
    timer_start = time.perf_counter()
    rider_repository: RepositoryOfRiders = RepositoryOfRiders()
    rider_repository.populate_repository(None, DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, "") 
    timer_end = time.perf_counter()
    elapsed = timer_end - timer_start
    print(f"\nrider_repository populated in: {format_seconds_to_hh_mm_ss(elapsed)}")


    dict_of_ZwiftPower90dayWattsItem = rider_repository.get_dict_of_ZwiftPower90dayWattsItem_by_ids(None)
    dict_of_ZwiftRacingAppItem_by_ids = rider_repository.get_dict_of_ZwiftRacingAppItem_by_ids(None)
    dict_of_RiderBruteItem = rider_repository.get_dict_of_RiderComputeItem_by_ids(None)
    dict_of_RiderStatsItem = rider_repository.get_dict_of_RiderStatsItem_by_ids(None)
    print(f"number of member IDs in file: {len(zwiftIDs)}")
    print(f"number of racers with power graphs: {len(dict_of_ZwiftPower90dayWattsItem)}")
    print(f"number of racers with RacingApp profiles: {len(dict_of_ZwiftRacingAppItem_by_ids)}")
    print(f"number of bona fide racers in Brute list: {len(dict_of_RiderBruteItem)}")
    print(f"number of bona fide racers in Stats list: {len(dict_of_RiderStatsItem)}")

    print("\nTask #1: generate a list of dict_of_ZwiftRacingAppItem_by_ids that are not in dict_of_RiderStatsItem. Missing riders:")
    missing_riderstats_items: Dict[str, Any] = {}
    for zwift_id, racingapp_item in dict_of_ZwiftRacingAppItem_by_ids.items():
        if zwift_id not in dict_of_RiderStatsItem:
            missing_riderstats_items[zwift_id] = racingapp_item

    # sort by name
    missing_riderstats_items = dict(sorted(missing_riderstats_items.items(), key=lambda item: item[1].full_name.lower()))
    # # print id and name
    for zwift_id, racingapp_item in missing_riderstats_items.items():
        print(f" - ZwiftID: {zwift_id}, Name: {racingapp_item.full_name}")
    print(f"total missing RiderStatsItem records: {len(missing_riderstats_items)}")

    # print("\nTask #2: generate list of those missing riders who do have ZwiftPower90dayWattsItem.")
    missing_with_powergraph: Dict[str, Any] = {}
    for zwift_id, racingapp_item in missing_riderstats_items.items():
        if zwift_id in dict_of_ZwiftPower90dayWattsItem:
            missing_with_powergraph[zwift_id] = racingapp_item
    # sort by name
    missing_with_powergraph = dict(sorted(missing_with_powergraph.items(), key=lambda item: item[1].full_name.lower()))
    # # print id and name
    for zwift_id, racingapp_item in missing_with_powergraph.items():
        print(f" - ZwiftID: {zwift_id}, Name: {racingapp_item.full_name}")
    print(f"total missing RiderStatsItem records who do have ZwiftPower90dayWattsItem: {len(missing_with_powergraph)}")
    print("\nwork complete. consult the log files for details.\n")
    print("\nyou may close the app. thank you.\n")


#runner
if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:
        _zp_club_members_filename = "zp-club-members.json"

        asyncio.run(reconcile_lists_and_save())

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

    except AlertMessageError as alert_err:
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )
        print(f"{alert_err.message}\n")

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")


