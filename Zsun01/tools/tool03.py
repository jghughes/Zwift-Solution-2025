from constants import RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging
from handy_utilities import read_dict_of_zsunriderItems, read_many_zwiftpower_bestpower_files_in_folder, write_dict_of_zsunbestpowerItems, get_betel_IDs
from jgh_sanitise_string import make_short_displayname

def main():
    """
    Read and validate raw ZwiftPower files for each Betel. Source files are the files from Dave K for all Zsun club members
    and stored in INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH.

    Write the consolidated data as a dict and serialise and save for storage in the Zsun01 project folder
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

    betel_rider_profiles_dict = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    # do work

    betel_IDs = get_betel_IDs()

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    betel_cp_dict = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    logger.debug(f"loaded cp_data for {len(betel_cp_dict)} riders")

    # function to make nick-names 

    # Clean up names in each JghFlattened90DayBestPowerCurveItem

    for rider_id, rider_cp_data in betel_cp_dict.items():
        rider_cp_data.zwiftid = int(rider_id) # write filename into zwiftId field
        rider_cp_data.name = make_short_displayname(betel_rider_profiles_dict[rider_id].name) # add short name
        # betel_cp_dict[rider_id] = rider_cp_data
        logger.debug(f"{rider_id} {rider_cp_data.name}")



    # Write the cleaned-up data to a file

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betelV4.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_zsunbestpowerItems(betel_cp_dict, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

if __name__ == "__main__":
    main()

