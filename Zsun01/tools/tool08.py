from handy_utilities import write_dict_of_cpdata, read_many_zwiftpower_cp_graph_files_in_folder
import critical_power as cp
from zwiftrider_related_items import ZwiftRiderCriticalPowerItem
from datetime import datetime

# Module-level constants



def main():
    # configure logging

    import logging
    import numpy as np
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    
    # do work

    INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    raw_cp_dict_for_everybody_in_the_club = read_many_zwiftpower_cp_graph_files_in_folder(None, INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH)

    logger.info(f"Successfully read, validated, and loaded {len(raw_cp_dict_for_everybody_in_the_club)} riders' critical power data from ZwiftPower JSON files in:- \nDir : {INPUT_ZWIFTPOWER_CPDATA_FROM_DAVEK_DIRPATH}")

    cp_count = 0
    inverse_count = 0
    skipped_modelling_count = 0
    count_of_riders_with_poor_r_squared = 0
    count_of_riders_with_poor_rmse = 0
    count_of_riders_with_high_fidelity_cp_data = 0

    r_squared_limit = .95
    rmse_limit = 10.0

    riders_with_high_cp_fidelity : list[ZwiftRiderCriticalPowerItem] = []


    for rider_id, rider in raw_cp_dict_for_everybody_in_the_club.items():

        rider.zwiftid = int(rider_id) # Ensure zwiftid is an integer and fill in the blank in the rider item

        raw_xy_data_cp = rider.export_zwiftpower_90day_best_data_for_cp_w_prime_modelling()
        raw_xy_data_pull = rider.export_zwiftpower_90day_best_data_for_pull_zone_modelling()
        raw_xy_data_ftp = rider.export_zwiftpower_90day_best_data_for_ftp_modelling()

        # do CP modelling
    
        critical_power, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  = cp.do_modelling_with_cp_w_prime_model(raw_xy_data_cp)
        p1hour_data= cp.cp_w_prime_model_numpy(np.array([60*60]), critical_power, anaerobic_work_capacity)

        rider.cp_model_cp_watts = critical_power
        rider.cp_model_w_prime= anaerobic_work_capacity
        rider.cp_model_r_squared = r_squared_cp
        rider.cp_model_p_1hour_extrapolated = p1hour_data[0]


        summary = f"CP model: CP = {round(critical_power)}W  AWC={round(anaerobic_work_capacity/1_000)}kJ  R_squared={round(r_squared_cp,2)}"

        logger.info(f"\n{summary}")


        # determine some sensible pull power targets

        coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = cp.do_modelling_with_decay_model(raw_xy_data_pull)

        pull_short = cp.decay_model_numpy(np.array([300]), coefficient_pull, exponent_pull)
        pull_medium = cp.decay_model_numpy(np.array([600]), coefficient_pull, exponent_pull)
        pull_long = cp.decay_model_numpy(np.array([1800]), coefficient_pull, exponent_pull)

        summary_pull = f"Pull power (30 - 60 - 120 seconds) = {round(pull_short[0])} - {round(pull_medium[0])} - {round(pull_long[0])}W"

        logger.info(f"\n{summary_pull}")

        # do FTP modelling

        coefficient, exponent, r_squared_ftp, rmse_ftp, answer_ftp = cp.do_modelling_with_decay_model(raw_xy_data_ftp)
        ftp= cp.decay_model_numpy(np.array([60*60]), coefficient, exponent)
        rider.ftp_model_coefficient = coefficient
        rider.ftp_model_exponent = exponent
        rider.ftp_model_r_squared = r_squared_ftp
        rider.ftp_model_ftp_watts = ftp[0]
        rider.when_models_generated = datetime.now().isoformat()

        summary_ftp = f"FTP model: FTP = {round(ftp[0])}W  R_squared = {round(r_squared_ftp,2)}"

        logger.info(f"\n{summary_ftp}")


        if max(r_squared_cp, r_squared_ftp) < r_squared_limit:
            logger.warning(f"Rider ID {rider.zwiftid} has R-squared values worse than {r_squared_limit} for both models.")
            count_of_riders_with_poor_r_squared += 1

        if min(rmse_cp, rmse_ftp) > rmse_limit:
            logger.warning(f"Rider ID {rider.zwiftid} has RMSE values worse than than {rmse_limit} for both models.")
            count_of_riders_with_poor_rmse += 1

        if rider.when_models_generated == "critical_power":
            rider.cp_model_w_prime= anaerobic_work_capacity
            cp_count += 1

        if rider.when_models_generated == "inverse":
            rider.ftp_model_coefficient = coefficient
            rider.ftp_model_exponent = exponent
            inverse_count += 1

        if rider.when_models_generated == "critical_power":
            if r_squared_cp >= r_squared_limit:
                riders_with_high_cp_fidelity.append(rider)
                count_of_riders_with_high_fidelity_cp_data += 1

        logger.info(f"Rider ID {rider.zwiftid} model preferred: {rider.when_models_generated}")

    logger.info(f"\nTotal riders on ZwiftPower from DaveK: {cp_count + inverse_count}\n\nCP model superior : {cp_count}\n\nInverse model superior : {inverse_count}\n\nInsufficient data : {skipped_modelling_count}\n\nR-squared value worse (less than) {r_squared_limit} : {count_of_riders_with_poor_r_squared}\n\n")

    logger.info(f"Riders with high fidelity CP data (R-squared >= {r_squared_limit}) : {count_of_riders_with_high_fidelity_cp_data}\n\n")

    # for  riders_with_high_cp_fidelity, write out the zwiftID, name, cp, and r_squared_cp. sorted by name
    riders_with_high_cp_fidelity.sort(key=lambda x: x.name)
    for rider in riders_with_high_cp_fidelity:
        logger.info(f"Rider ID {rider.zwiftid} :  CP = {round(rider.cp_model_cp_watts)}W  FTP = {round(rider.cp_model_p_1hour_extrapolated)}W  r_squared_cp = {round(rider.cp_model_r_squared,2)}")

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betel_rubbish.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_cpdata(raw_cp_dict_for_everybody_in_the_club, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    # from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    # for rider_id, rider in raw_cp_dict_for_everybody_in_the_club.items():
    #     cp_data = rider.export_zwiftpower_cp_graph_data()  # Export critical power data as a dictionary
    #     table_data = [[x, y] for x, y in cp_data.items()]  # Convert dictionary to a list of [x, y] pairs
    #     table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

    #     logger.info(f"Critical Power Data for Rider ID: {rider_id}  Rider Name: {rider.name}/n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

if __name__ == "__main__":
    main()


