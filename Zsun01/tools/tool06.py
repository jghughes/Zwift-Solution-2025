from handy_utilities import read_many_zwiftracingapp_files_in_folder, get_betel_zwift_ids, read_dict_of_zwiftriders
from zwiftrider_related_items import ZwiftRiderItem

import logging
from jgh_logging import jgh_configure_logging

def main():
    """
    Identify and categorize Betel rider IDs based on their presence in Zwift Racing App data.

    This script performs the following steps:
    1. Reads Zwift rider data and Zwift Racing App data.
    2. Separates Betel rider IDs into two categories:
       - Found: IDs present in the Zwift Racing App data.
       - Not Found: IDs not present in the Zwift Racing App data.
    3. For each Betel ID:
       - If found, retrieves the rider's name from the Zwift Racing App data.
       - If not found, attempts to retrieve the rider's name from Zwift rider data.
       - Defaults the name to "Unknown" if it cannot be found.
    4. Sorts both the found and not found lists alphabetically by rider name.
    5. Prints the sorted lists of Betel IDs and their corresponding names.

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
        - Requires `handy_utilities` for reading Zwift rider and CP data.
        - Uses `ZwiftRiderItem` for handling rider data.

    Returns:
        None
    """
    # configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)  # interesting messages, but not a deluge of INFO

    # Module-level constants
    INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"

    betel_IDs =get_betel_zwift_ids()

    # do work

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zwiftriders(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)


    zsun_cp_dict = read_many_zwiftracingapp_files_in_folder([], INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    # Separate Betel IDs into found and not found lists
    betel_found = []
    betel_not_found = []

    for betel_id in betel_IDs:
        if betel_id in zsun_cp_dict:
            name = zsun_cp_dict[betel_id].name
            betel_found.append((betel_id, name))
        else:
            name = dict_of_zwiftrideritem.get(betel_id, ZwiftRiderItem(name="Unknown")).name
            betel_not_found.append((betel_id, name))

    # Sort both lists alphabetically by name
    betel_found.sort(key=lambda x: x[1].lower())
    betel_not_found.sort(key=lambda x: x[1].lower())

    # Print the lists
    print("Betel IDs found in zsun_cp_dict:")
    for betel_id, name in betel_found:
        print(f"ID: {betel_id}, Name: {name}")

    print("\nBetel IDs not found in zsun_cp_dict:")
    for betel_id, name in betel_not_found:
        print(f"ID: {betel_id}, Name: {name}")


if __name__ == "__main__":
    main()