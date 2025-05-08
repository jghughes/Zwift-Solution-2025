from handy_utilities import *
import pandas as pd
from jgh_read_write import write_pandas_dataframe_as_xlsx


# Module-level constants



def main():
    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"



    betel_IDs = get_betel_IDs()
    # betel_IDs = ['4945836'] # david_evanetich

    dict_of_profiles_for_everybody = read_many_zwift_profile_files_in_folder(betel_IDs, ZWIFT_PROFILES_DIRPATH)

    dict_of_jghbestpoweritems_for_betel = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, ZWIFTPOWER_GRAPHS_DIRPATH)

    OUTPUT_FILE_NAME = "jghbestpoweritems_for_betel.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_zsunbestpowerItems(dict_of_jghbestpoweritems_for_betel, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    for zwiftID, ZsunBestPowerItem in dict_of_jghbestpoweritems_for_betel.items():
        name = dict_of_profiles_for_everybody[zwiftID].first_name + " " + dict_of_profiles_for_everybody[zwiftID].last_name
        x_y_ordinates = ZsunBestPowerItem.export_all_x_y_ordinates()  # Export critical power data as a dictionary
        table_data = [[x, y] for x, y in x_y_ordinates.items()]  # Convert dictionary to a list of [x, y] pairs
        table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

        logger.info(f"ZsunBestPowerItem ordinates for ZwiftID: {zwiftID}  Name: {name}\n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))



if __name__ == "__main__":
    main()


