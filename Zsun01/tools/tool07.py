"""
This little tool is not used directly in the Brute production pipeline.
It is a helper tool. It is written to help in the process of iterative
fine-tuning of curve parameters. It is used to do reality checks of
modelled best-fit inverse-exponential curves by applying the fitted
parameters to a small subset of riders with whom I am personally
familiar: such as myself, DaveK, and the other Betels. I use their
calculated inverse-exponential curves to print their synthetic power-
duration graphs to the console in tabular form so that I can inspect
them visually to decide if they are realistic compared to their actual
power curves or wildly out of whack. I save the output to a JSON file
for later reference. This tool provides an interim sanity check to
ensure that the power-duration relationships are being modeled well
before applying them to the entire Zsun database.

The script performs the following steps:
- Configures logging for the application.
- Retrieves a list of rider IDs (Betel IDs) to process.
- Loads Zwift profile data and ZwiftPower best power data for these
  riders from specified input directories.
- Writes the best power data for all riders to a JSON file in the
  specified output directory.
- For each rider, logs a formatted table of their power-duration data
  (time vs. watts) using the tabulate library for clear presentation.

This tool demonstrates data loading, aggregation, export, and formatted
logging for cycling performance analysis using Python.
"""
from scraped_zwift_data_repository import read_zwift_files, read_zwiftpower_graph_watts_files

from handy_utilities import *
import pandas as pd


# Module-level constants



def main():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZWIFT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwift/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/power-graph-watts/"



    betel_IDs = get_test_IDs()
    # betel_IDs = ['4945836'] # david_evanetich

    dict_of_profiles_for_everybody = read_zwift_files(betel_IDs, ZWIFT_DIRPATH, logger, logging.DEBUG) # merely need this to get the first and last names of the riders

    dict_of_jghbestpoweritems_for_betel = read_zwiftpower_graph_watts_files(betel_IDs, ZWIFTPOWER_GRAPHS_DIRPATH, logger, logging.DEBUG)) # read all the raw 90-day best power files for the riders in betel_IDs

    OUTPUT_FILE_NAME = "jghbestpoweritems_for_betel.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"

    write_json_dict_of_ZsunWattsItem(dict_of_jghbestpoweritems_for_betel, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    for zwiftID, ZsunWattsItem in dict_of_jghbestpoweritems_for_betel.items():
        name = dict_of_profiles_for_everybody[zwiftID].first_name + " " + dict_of_profiles_for_everybody[zwiftID].last_name
        x_y_ordinates = ZsunWattsItem.export_all_x_y_ordinates()  # Export critical power data as a dictionary
        table_data = [[x, y] for x, y in x_y_ordinates.items()]  # Convert dictionary to a list of [x, y] pairs
        table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

        logger.info(f"ZsunWattsItem ordinates for ZwiftID: {zwiftID}  Name: {name}\n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))



if __name__ == "__main__":
    main()


