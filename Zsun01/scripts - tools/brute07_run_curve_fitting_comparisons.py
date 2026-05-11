"""
This helper tool is not used directly in the Brute production pipeline.
It assists with iterative fine-tuning of curve parameters by providing
sanity checks on modelled best-fit inverse-exponential curves. The tool
applies fitted parameters to a small subset of familiar riders (e.g.,
myself, DaveK, and other Betels) and prints their synthetic power-duration
graphs in tabular form for visual inspection. This helps determine if the
modeled curves are realistic compared to actual power data. The output is
also saved to a JSON file for later reference.

Recent updates:
- Output directory and file name are now explicitly set in the script.
- Logging configuration is loaded from an external JSON settings file.
- Minor improvements to table formatting and data export.

The script performs the following steps:
- Configures logging for the application using a JSON settings file.
- Retrieves a list of rider IDs (test_IDs) to process.
- Loads Zwift profile data and ZwiftPower best power data for these
  riders from specified input directories.
- Writes the best power data for all riders to a JSON file in the
  specified output directory.
- For each rider, logs a formatted table of their power-duration data
  (time vs. watts) using the tabulate library for clear presentation.

This tool demonstrates data loading, aggregation, export, and formatted
logging for cycling performance analysis using Python.
"""
from pathlib import Path

from tabulate import tabulate

from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from storage_config import (
    FILENAME_RIDER_BRUTE_DTO_JSON_DICT,
    DIRPATH_ZWIFT_FILES,
    DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    DIRPATH_RUBBISH_SCRATCHPAD,
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
)
from zwiftid_file_reader_sync import read_zwiftdto_files_to_item_dict_sync, read_zwiftpower90daywattsdto_files_to_item_dict_sync
from working_file_read_write import write_zwiftpower_90day_watts_dict_to_json
from repository_of_team_rosters import RepositoryOfTeamRosters

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def run_curve_fitting_comparisons():


    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), Path(DIRPATH_RUBBISH_SCRATCHPAD)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_BRUTE_DTO_JSON_DICT])
    except Exception as err:
        print(err)
        return


    test_IDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)

    dict_of_zwift_profiles_for_test_IDs = read_zwiftdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFT_FILES), test_IDs) # merely need this to get the first_name and last_name names of the riders

    dict_of_zsunwatts_graphs_for_testIDs = read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), test_IDs) 

    write_zwiftpower_90day_watts_dict_to_json(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_file_name, dict_of_zsunwatts_graphs_for_testIDs)

    # log all the x and y data for all riders in pretty tables

    for zwift_id, ZwiftPowerFlattened90dayWattsItem in dict_of_zsunwatts_graphs_for_testIDs.items():
        name = dict_of_zwift_profiles_for_test_IDs[zwift_id].first_name + " " + dict_of_zwift_profiles_for_test_IDs[zwift_id].last_name
        x_y_ordinates = ZwiftPowerFlattened90dayWattsItem.export_all_x_y_ordinates()  # Export critical power data as a dictionary
        table_data = [[x, y] for x, y in x_y_ordinates.items()]  # Convert dictionary to a list of [x, y] pairs
        table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

        print(f"ZwiftPowerFlattened90dayWattsItem ordinates for ZwiftID: {zwift_id}  Name: {name}\n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        team_name = "scratchpad"
        output_file_name = "zsunwatts_graphs_for_testIDs.json"
        run_curve_fitting_comparisons()

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




