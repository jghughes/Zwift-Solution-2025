"""
This tool is for debugging and testing purposes during development. It is designed 
to extract and process best power data from ZwiftPower 90-day power graphs, transforming 
them into a format suitable for Brute. We inspect the output of this tool by
eyeballing the resultant JSON file and manually satisfying ourselves that
everything works as intended and as the Brute production pipeline expects.

This tool extracts and processes input_data ZwiftPower 90-day power-graphs,
translates them into the equivalent output ZsunBestPowerItems, and then writes
the cleaned data to a new JSON dictionary file keyed by ZwiftID.
ZsunBestPowerItems contain the best power data for each rider, which is used in
the Zsun application. Each power-graph is a dict of 99 data-points from 1
second to 7200 seconds. Each ZsunWattsPropertiesItem does not feature a list in the
same way. It features 99 matching named properties. The meat of the tool is in
the way we convert the input_data for each rider (Dict[int, float]): A
dictionary where keys are durations (in seconds) and values are the
corresponding critical power values to the output data (Dict[zwift_id,
ZsunWattsPropertiesItem]) where the power item has a whole bunch of individual
properties where the name of the property is a str and the value of the
property is corresponding critical power value. By giving the properties names
that match the int keys in the input_data, we have effectively flattened the
data and can do all sorts of astonishing clever things with the 99 datapoints.

The tool performs the following steps:
- Configures logging for the application.
- Loads all current fully populated rider profiles from a JSON file in the data
  folder into a dictionary.
- Retrieves a list of a small subset of rider IDs to process. Currently these
  are the BetelIDs, but they could be any subset.
- Using the pydantic ZwiftPowerWattsOrdinatesDTO, it validates each individual
  best-power-graph data file for these riders from the folder received from
  DaveK and maps them into a ZwiftPowerWattsOrdinatesDTO and thence into a
  ZsunWattsPropertiesItem. The datafiles are all named by ZwiftID. The items are all
  stored in a dictionary with the rider's Zwift ID as the key.
- For each item in the dictionary, inserts the filename into the zwift_ID
  property, and generates a pretty display name - for logging only.
- Writes the processed best power data for all riders to a new JSON file in the
  specified output directory.

This script demonstrates reading and writing JSON data using pydantic DTOs, mappings
to dataclasses and back again, and using sundry file utility functions. 
"""

from filenames import RIDERS_FILE_NAME
from dirpaths import DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging
from handy_utilities import read_dict_of_zsunriderDTO, read_many_zwiftpower_bestpower_files_in_folder, write_dict_of_zsunwattspropertiesItem, get_test_IDs
from jgh_sanitise_string import make_short_displayname

def main():
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    all_rider_profiles_as_dict = read_dict_of_zsunriderDTO(RIDERS_FILE_NAME, DATA_DIRPATH)

    # do work

    betel_IDs = get_test_IDs()

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

    write_dict_of_zsunwattspropertiesItem(betel_cp_dict, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

if __name__ == "__main__":
    main()

