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

    betel_IDs = get_betel_zwift_ids()


    dict_of_jghbestpoweritems_for_betel = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, ZWIFTPOWER_GRAPHS_DIRPATH)

    ZSUN01_BETEL_PROFILES_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zsun01_betel_zsunrideritems = read_dict_of_zsunrider_items(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    for zwiftID, jghbestpoweritem in dict_of_jghbestpoweritems_for_betel.items():
        jghbestpoweritem.zwift_id = zwiftID
        if zwiftID in dict_of_zsun01_betel_zsunrideritems:
            pass
        else:
            logger.warning(f"ZwiftID {zwiftID} not found in betel data.")

    OUTPUT_FILE_NAME = "jghbestpoweritems_for_betel.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_90day_bestpower_items(dict_of_jghbestpoweritems_for_betel, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    for zwiftID, jghbestpoweritem in dict_of_jghbestpoweritems_for_betel.items():
        name = dict_of_zsun01_betel_zsunrideritems[zwiftID].name
        x_y_ordinates = jghbestpoweritem.export_all_x_y_ordinates()  # Export critical power data as a dictionary
        table_data = [[x, y] for x, y in x_y_ordinates.items()]  # Convert dictionary to a list of [x, y] pairs
        table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

        logger.info(f"JghBestPowerItem ordinates for ZwiftID: {zwiftID}  Name: {name}\n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

    # segue: get a hold off ordinates for MarkB

    x_y_ordinates = dict_of_jghbestpoweritems_for_betel["5530045"].export_all_x_y_ordinates()

    # convert to a pandas dataframe
    df = pd.DataFrame(list(x_y_ordinates.items()), columns=["Time (x) [seconds]", "Power (y) [watts]"])
    #save to exel
    output_file_name = "markb_90day_best_power_x_y_ordinates.xlsx"
    output_dir_path = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/markb/"
    write_pandas_dataframe_as_xlsx(df, output_file_name, output_dir_path)
    logger.info(f"Saved {len(x_y_ordinates)} x y ordinates for MarkB to: {output_file_path}")



if __name__ == "__main__":
    main()


