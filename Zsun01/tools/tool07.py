from math import log
from handy_utilities import write_dict_of_90day_bestpower_items, read_many_zwiftpower_bestpower_files_in_folder, read_dict_of_zsunrider_items,get_betel_zwift_ids


# Module-level constants



def main():
    """
    Main function to process ZwiftPower the voluminous critical_power data for a shortlist of riders,
    in this caes Betel riders.

    This function performs the following tasks:
    1. Configures logging for the application.
    2. Reads critical power data from ZwiftPower JSON files in a specified directory.
    3. Reads Zwift rider data from a predefined JSON file.
    4. Updates the critical power data with rider names and ensures `zwiftid` is an integer.
    5. Logs warnings for any rider IDs in the critical power data that are not found in the rider data.
    6. Writes the processed critical power data to a JSON file in the specified output directory.

    Module-level constants:
        - `INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH`: Directory path for ZwiftPower critical power data files.
        - `OUTPUT_FILE_NAME`: Name of the output JSON file.
        - `OUTPUT_DIR_PATH`: Directory path for the output JSON file.
        - `betel_IDs`: List of rider IDs to process.

    Dependencies:
        - `read_many_zwiftpower_bestpower_files_in_folder`: Reads ZwiftPower critical power data files.
        - `read_dict_of_zsunrider_items`: Reads Zwift rider data.
        - `write_dict_of_90day_bestpower_items`: Writes processed critical power data to a JSON file.
        - `jgh_configure_logging`: Configures logging for the application.

    Raises:
        - Logs warnings for missing rider IDs in the Zwift rider data.

    Returns:
        None
    """

    # configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    
    betel_IDs = get_betel_zwift_ids()

    INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    raw_cp_dict_for_betel = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH)

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zsunrider_items(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    for rider_id, rider_cp_data in raw_cp_dict_for_betel.items():
        rider_cp_data.zwiftid = int(rider_id) # Ensure zwiftid is an integer and fill in the blank
        if rider_id in dict_of_zwiftrideritem:
            rider_cp_data.name = dict_of_zwiftrideritem[rider_id].name
        else:
            logger.warning(f"Rider ID {rider_id} not found in zwiftriders data.")

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betelV2.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_90day_bestpower_items(raw_cp_dict_for_betel, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    for rider_id, rider_cp_data in raw_cp_dict_for_betel.items():
        cp_data = rider_cp_data.export_zwiftpower_graph_data()  # Export critical power data as a dictionary
        table_data = [[x, y] for x, y in cp_data.items()]  # Convert dictionary to a list of [x, y] pairs
        table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

        logger.info(f"Critical Power Data for Rider ID: {rider_id}  Rider Name: {rider_cp_data.name}\n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

if __name__ == "__main__":
    main()


