from filenames import RIDERS_FILE_NAME
from dirpaths import DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging
from handy_utilities import read_dict_of_zsunriderItems, read_many_zwiftpower_bestpower_files_in_folder, write_dict_of_zsunbestpowerItems, get_betel_IDs
from jgh_sanitise_string import make_short_displayname

def main():
    """
    Function Main reads and validates raw ZwiftPower files for all ZSUN riders in the power-graph-watts folder. 
    
    There are something like 1,500 riders in the ZSUN project, and each rider has a best power graph file. The best power files are stored in a folder named "power-graph-watts" in the INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH. The purpose of Main() is to read and process all of these one by one, mapping each one into a ZsunRiderItem and then consolidating all of them into single file that is subsequently the sourcefile of best power data that is used for curve fitting that uses machine learning to distill each riders best power graph into a pair of curves that are then used throughout the project.

    To start with, all the rider names need to be cleaned up to remove commonplace special characters and redundant text, so that the rider names can be displyed prettily. This is done using the make_short_displayname() function.

    Main() consolidates the Write the consolidated data as a JSON dict and save for storage in the Zsun01 project data folder
    named "input_cp_data_for_betel_from_zwiftpower.json". This file is subsequently used in `tool04` to 
    do critical_power data modelling and curve fitting to generate the modelled data stored in "betel_cp_data.json"

    Dependencies:
        - Requires `handy_utilities` for reading and writing CP data.
        - Uses `JghFlattened90DayBestPowerCurveDTO` for data validation and processing.

    Returns:
        None
    """
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

