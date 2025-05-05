from handy_utilities import read_many_zwiftracingapp_profile_files_in_folder, get_betel_zwift_ids, read_dict_of_zsunrider_items
from zsun_rider_item import ZsunRiderItem

import logging
from jgh_logging import jgh_configure_logging

def main():
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

    dict_of_zwiftrideritem = read_dict_of_zsunrider_items(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)


    zsun_cp_dict = read_many_zwiftracingapp_profile_files_in_folder([], INPUT_ZSUNDATA_FROM_DAVEK_DIRPATH)

    # Separate Betel IDs into found and not found lists
    betel_found :  = []
    betel_not_found = []

    for betel_id in betel_IDs:
        if betel_id in zsun_cp_dict:
            name = zsun_cp_dict[betel_id].fullname
            betel_found.append((betel_id, name))
        else:
            name = dict_of_zwiftrideritem.get(betel_id, ZsunRiderItem(name="Unknown")).name
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