"""
This tool extracts and processes best power data for a specific set of riders, then writes the cleaned data to a new JSON file.

The tool performs the following steps:
- Configures logging for the application.
- Loads all rider profiles from a JSON file into a dictionary.
- Retrieves a list of rider IDs (Betel IDs) to process.
- Reads best power data files for these riders from a specified input directory.
- For each rider, updates the best power data with the rider's Zwift ID and generates a short display name for logging.
- Writes the processed best power data for all riders to a new JSON file in the specified output directory.

This script demonstrates reading and writing JSON data, integrating multiple utility functions, and basic data transformation and logging in Python.
"""


from filenames import RIDERS_FILE_NAME
from dirpaths import DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging
from handy_utilities import read_dict_of_zsunriderItems, read_many_zwiftpower_bestpower_files_in_folder, write_dict_of_zsunbestpowerItems, get_betel_IDs
from jgh_sanitise_string import make_short_displayname

def main():
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    all_rider_profiles_as_dict = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    # do work

    betel_IDs = get_betel_IDs()

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/power-graph-watts/"

    betel_cp_dict = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    logger.debug(f"loaded cp_data for {len(betel_cp_dict)} riders")

    # function to make nick-names 

    for rider_id, rider_cp_data in betel_cp_dict.items():
        rider_cp_data.zwift_id = rider_id # write filename into zwiftId field
        display_name = make_short_displayname(all_rider_profiles_as_dict[rider_id].name) # add short name
        logger.debug(f"{rider_id} {display_name}")

    # Write the cleaned-up data to a file

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betelV4.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"

    write_dict_of_zsunbestpowerItems(betel_cp_dict, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

if __name__ == "__main__":
    main()

