import logging
from jgh_logging import jgh_configure_logging
from handy_utilities import read_dict_of_zwiftriders, read_many_zwiftpower_critical_power_graph_files_in_folder, write_dict_of_cpdata, get_betel_zwift_ids

def main():
    """
    Read and validate raw ZwiftPower files for each Betel. Source files are the files from Dave K for all Zsun club members
    and stored in INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH.

    Write the consolidated data as a dict and serialise and save for storage in the Zsun01 project folder
    named "input_cp_data_for_betel_from_zwiftpower.json". This file is subsequently used in `tool04` to 
    do critical_power data modelling and curve fitting to generate the modelled data stored in "betel_cp_data.json"

    Dependencies:
        - Requires `handy_utilities` for reading and writing CP data.
        - Uses `ZwiftPower90DayBestGraphDTO` for data validation and processing.

    Returns:
        None
    """
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    betel_rider_profiles_dict = read_dict_of_zwiftriders(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    # do work

    betel_IDs = get_betel_zwift_ids()

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    betel_cp_dict = read_many_zwiftpower_critical_power_graph_files_in_folder(betel_IDs, INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    logger.debug(f"loaded cp_data for {len(betel_cp_dict)} riders")

    # function to make nick-names 

    def make_short_name(old_name: str) -> str:
        """
        Cleans up a given name according to the following rules:
        1. Trim spaces from the old name and replace any contained commas or dots with spaces.
        2. If the old name has only one word, capitalize the first letter of the word.
        3. If the old name has more than one word, concatenate the first word (with the first letter capitalized)
           with the capitalized first letter of the second word.

        Args:
            old_name (str): The original name to be cleaned.

        Returns:
            str: The cleaned-up new name.
        """
        # Step 1: Trim spaces and replace commas or dots with spaces
        old_name = old_name.strip().replace(",", " ").replace(".", " ")

        # Step 2: Split the name into words
        name_parts = old_name.split()

        # Step 3: Determine the new name
        if len(name_parts) == 1:
            # If the old name has only one word, capitalize the first letter
            new_name = name_parts[0][0].upper() + name_parts[0][1:]
        elif len(name_parts) > 1:
            # If the old name has more than one word, concatenate the first word
            # (with only the first letter capitalized) with the capitalized first letter of the second word
            new_name = name_parts[0][0].upper() + name_parts[0][1:] + " " + name_parts[1][0].upper()
        else:
            # Handle edge cases where the name might be empty
            new_name = "Unknown"

        return new_name

    # Clean up names in each ZwiftPower90DayBestGraphItem

    for rider_id, rider_cp_data in betel_cp_dict.items():
        rider_cp_data.zwiftid = int(rider_id) # write filename into zwiftId field
        rider_cp_data.name = make_short_name(betel_rider_profiles_dict[rider_id].name) # add short name
        # betel_cp_dict[rider_id] = rider_cp_data
        logger.debug(f"{rider_id} {rider_cp_data.name}")



    # Write the cleaned-up data to a file

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betelV4.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_cpdata(betel_cp_dict, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

if __name__ == "__main__":
    main()

