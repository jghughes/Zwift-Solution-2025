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

from repository_of_scraped_riders import read_zwift_files, read_zwiftpower_graph_watts_files
from handy_utilities import get_test_IDs, write_json_dict_of_ZsunWattsItem
from dirpaths import ZWIFT_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH
from tabulate import tabulate

import logging
logger = logging.getLogger(__name__)

def main():
    test_IDs = get_test_IDs()

    dict_of_zwift_profiles_for_test_IDs = read_zwift_files(test_IDs, ZWIFT_DIRPATH) # merely need this to get the first and last names of the riders

    dict_of_zsunwatts_graphs_for_testIDs = read_zwiftpower_graph_watts_files(test_IDs, ZWIFTPOWER_GRAPHS_DIRPATH) 

    write_json_dict_of_ZsunWattsItem(dict_of_zsunwatts_graphs_for_testIDs, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    # log all the x and y data for all riders in pretty tables

    for zwiftID, ZsunWattsItem in dict_of_zsunwatts_graphs_for_testIDs.items():
        name = dict_of_zwift_profiles_for_test_IDs[zwiftID].first_name + " " + dict_of_zwift_profiles_for_test_IDs[zwiftID].last_name
        x_y_ordinates = ZsunWattsItem.export_all_x_y_ordinates()  # Export critical power data as a dictionary
        table_data = [[x, y] for x, y in x_y_ordinates.items()]  # Convert dictionary to a list of [x, y] pairs
        table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

        logger.info(f"ZsunWattsItem ordinates for ZwiftID: {zwiftID}  Name: {name}\n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))


if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")

    OUTPUT_FILE_NAME = "zsunwatts_graphs_for_testIDs.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"

    main()


