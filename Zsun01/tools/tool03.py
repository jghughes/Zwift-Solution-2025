from handy_utilities import read_dict_of_cpdata, write_dict_of_cpdata, read_many_zwiftracing_files_in_folder

import logging
from jgh_logging import jgh_configure_logging

def main():
    """
    Process raw Zwift Racing App data files for Zsun club members to extract and
    consolidate critical power (CP) data for Betel riders.

    This script performs the following steps:
    1. Reads raw CP data from independent files for each Zsun member.
    2. Filters the data to include only Betel riders based on their Zwift IDs.
    3. Reads additional CP data for a subset of Betel riders from a separate file.
    4. Overwrites or adds the additional CP data to the filtered Betel rider data.
    5. Cleans up the names of Betel riders to ensure consistent formatting.
    6. Writes the consolidated and cleaned CP data for Betel riders to a JSON file.

    The consolidated data is subsequently used in `tool04` to generate populated
    CP data for all Betel riders.

    Module-Level Constants:
        - INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES: The filename
          of the additional CP data file for Betel riders.
        - INPUT_CP_DATA_DIRPATH: The directory path where the additional CP data
          file is located.
        - INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH: The directory path containing raw
          CP data files for Zsun members.
        - OUTPUT_FILE_NAME: The filename for the consolidated CP data output.
        - OUTPUT_DIR_PATH: The directory path where the consolidated CP data
          output will be written.

    Dependencies:
        - Requires `handy_utilities` for reading and writing CP data.
        - Uses `ZwiftRiderCriticalPowerDTO` for data validation and processing.

    Returns:
        None
    """
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # Module-level constants

    INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES = "input_cp_data_for_jgh_josh.json"
    INPUT_CP_DATA_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betel.json"
    OUTPUT_DIR_PATH = INPUT_CP_DATA_DIRPATH

    betel_IDs =["1193", "5134", "9011", "11526", "183277", "383480", "384442", "480698", "1024413", "1884456" "991817", "1713736", "2398312", "2508033"  "2682791", "3147366", "5421258", "5490373", "5530045", "5569057", "6142432"] 

    # do work

    betel_cp_dict = read_many_zwiftracing_files_in_folder(betel_IDs, INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    jgh_cp_dict = read_dict_of_cpdata(INPUT_CPDATA_FILENAME_ORIGINALLY_FROM_ZWIFT_FEED_PROFILES, INPUT_CP_DATA_DIRPATH)

    # Overwrite/add the items in raw_cp_dict_for_betel with all the items in jgh_cp_dict

    betel_cp_dict.update(jgh_cp_dict)

    # function to make prttty names 

    def clean_name(old_name: str) -> str:
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
            new_name = name_parts[0][0].upper() + name_parts[0][1:] + name_parts[1][0].upper()
        else:
            # Handle edge cases where the name might be empty
            new_name = "Unknown"

        return new_name

    # Clean up names in each ZwiftRiderCriticalPowerItem

    for rider_id, rider_cp_data in betel_cp_dict.items():
        # Clean up the name
        rider_cp_data.name = clean_name(rider_cp_data.name)
        # Update the rider's name in the dictionary
        betel_cp_dict[rider_id] = rider_cp_data

    # Write the cleaned-up data to a file

    write_dict_of_cpdata(betel_cp_dict, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

if __name__ == "__main__":
    main()

