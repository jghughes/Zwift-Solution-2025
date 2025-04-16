from math import log
from handy_utilities import write_dict_of_cpdata, read_many_zwiftpower_cp_graph_files_in_folder
from power_duration_modelling import cp_w_prime_model, inverse_model, do_modelling_with_cp_w_prime_model, do_modelling_with_inverse_model


# Module-level constants



def main():
    """
    Main function to process ZwiftPower critical power data for a predefined list of riders (Betel IDs).

    This function performs the following tasks:
    1. Configures logging for the application.
    2. Reads critical power data from ZwiftPower JSON files in a specified directory.
    3. Reads Zwift rider data from a predefined JSON file.
    4. Updates the critical power data with rider names and ensures `zwiftid` is an integer.
    5. Logs warnings for any rider IDs in the critical power data that are not found in the rider data.
    6. Writes the processed critical power data to a JSON file in the specified output directory.

    Module-level constants:
        - `INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH`: Directory path for ZwiftPower critical power data files.
        - `OUTPUT_FILE_NAME`: Name of the output JSON file.
        - `OUTPUT_DIR_PATH`: Directory path for the output JSON file.
        - `betel_IDs`: List of rider IDs to process.

    Dependencies:
        - `read_many_zwiftpower_cp_graph_files_in_folder`: Reads ZwiftPower critical power data files.
        - `read_dict_of_zwiftriders`: Reads Zwift rider data.
        - `write_dict_of_cpdata`: Writes processed critical power data to a JSON file.
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

    
    # do work

    INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    raw_cp_dict_for_the_world = read_many_zwiftpower_cp_graph_files_in_folder([], INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH)

    for rider_id, rider_cp_data in raw_cp_dict_for_the_world.items():

        rider_cp_data.zwiftid = int(rider_id) # Ensure zwiftid is an integer and fill in the blank
        raw_xy_data = rider_cp_data.export_cp_data_for_best_fit_modelling()

        # do modelling

        cp, awc, r_squared, answer  = do_modelling_with_cp_w_prime_model(raw_xy_data)
        summary = f"Critical power model: CP={round(cp)}W  AWC={round(awc/1_000)}kJ  R_squared={round(r_squared,2)}  P_1hour={round(cp_w_prime_model(60*60, cp, awc))}W"
        logger.info(f"/n{summary}")

        constant, exponent, r_squared2, answer2 = do_modelling_with_inverse_model(raw_xy_data)
        summary2 = f"Inverse model: c={round(constant,0)}  e={round(exponent,4)}  R_squared={round(r_squared2,2)}  P_1hour={round(inverse_model(60*60, constant, exponent))}W"
        logger.info(f"/n{summary2}")


        rider_cp_data.model_applied = "cp" if r_squared > r_squared2 else "inverse"
        logger.info(f"Model applied: {rider_cp_data.model_applied}")

    # OUTPUT_FILE_NAME = "rubbish_v1.json"
    # OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    # write_dict_of_cpdata(raw_cp_dict_for_the_world, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    # from tabulate import tabulate

    # # log all the x and y data for all riders in pretty tables

    # for rider_id, rider_cp_data in raw_cp_dict_for_the_world.items():
    #     cp_data = rider_cp_data.export_cp_data()  # Export critical power data as a dictionary
    #     table_data = [[x, y] for x, y in cp_data.items()]  # Convert dictionary to a list of [x, y] pairs
    #     table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

    #     logger.info(f"Critical Power Data for Rider ID: {rider_id}  Rider Name: {rider_cp_data.name}/n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

if __name__ == "__main__":
    main()


