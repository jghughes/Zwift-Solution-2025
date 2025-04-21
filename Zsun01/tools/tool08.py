from handy_utilities import write_dict_of_cpdata, read_many_zwiftpower_cp_graph_files_in_folder
import  critical_power as cp
from zwiftrider_related_items import ZwiftRiderCriticalPowerItem

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

    r_squared_limit = .98
    rmse_limit = 10.0

    riders_with_high_cp_fidelity : list[ZwiftRiderCriticalPowerItem] = []


    for rider_id, rider_cp_data in raw_cp_dict_for_everybody_in_the_club.items():

        rider_cp_data.zwiftid = int(rider_id) # Ensure zwiftid is an integer and fill in the blank in the rider_cp_data item

        raw_xy_data = rider_cp_data.export_cp_data_for_best_fit_modelling()

        if len(raw_xy_data) < 2:
            logger.warning(f"Rider ID {rider_cp_data.zwiftid} has less than 2 data points. Skipping modelling.")
            skipped_modelling_count += 1
            continue

        # do CP modelling
    
        critical_power, anaerobic_work_capacity, r_squared, rmse, answer  = cp.do_modelling_with_cp_w_prime_model(raw_xy_data)
        p1hour_data= cp.cp_w_prime_model_numpy(np.array([60*60]), critical_power, anaerobic_work_capacity)

        rider_cp_data.critical_power = critical_power
        rider_cp_data.anaerobic_work_capacity = anaerobic_work_capacity
        rider_cp_data.critical_power_model_r_squared = r_squared
        rider_cp_data.critical_power_p_1hour_predicted = p1hour_data[0]


        summary = f"Critical power model: CP={round(critical_power)}W  AWC={round(anaerobic_work_capacity/1_000)}kJ  R_squared={round(r_squared,2)}  RMSE={round(rmse)}W  P_1hour={round(p1hour_data[0])}W"

        logger.info(f"\n{summary}")

        # do Inverse modelling

        coefficient, exponent, r_squared2, rmse2, answer2 = cp.do_modelling_with_inverse_model(raw_xy_data)
        p2hour_data= cp.inverse_model_numpy(np.array([60*60]), coefficient, exponent)
        rider_cp_data.inverse_coefficient = coefficient
        rider_cp_data.inverse_exponent = exponent
        rider_cp_data.inverse_power_model_r_squared = r_squared2
        rider_cp_data.inverse_power_p_1hour_predicted = p2hour_data[0]

        summary2 = f"Inverse model: c={round(coefficient,0)}  e={round(exponent,4)}  R_squared={round(r_squared2,2)}  RMSE={round(rmse2)}W P_1hour={round(p2hour_data[0])}W"

        logger.info(f"\n{summary2}")

        # do Combined modelling


        rider_cp_data.model_applied = "critical_power" if r_squared > r_squared2 else "inverse"

        if max(r_squared, r_squared2) < r_squared_limit:
            logger.warning(f"Rider ID {rider_cp_data.zwiftid} has R-squared values worse than {r_squared_limit} for both models.")
            count_of_riders_with_poor_r_squared += 1

        if min(rmse, rmse2) > rmse_limit:
            logger.warning(f"Rider ID {rider_cp_data.zwiftid} has RMSE values worse than than {rmse_limit} for both models.")
            count_of_riders_with_poor_rmse += 1

        if rider_cp_data.model_applied == "critical_power":
            rider_cp_data.anaerobic_work_capacity = anaerobic_work_capacity
            cp_count += 1

        if rider_cp_data.model_applied == "inverse":
            rider_cp_data.inverse_coefficient = coefficient
            rider_cp_data.inverse_exponent = exponent
            inverse_count += 1

        if rider_cp_data.model_applied == "critical_power":
            if r_squared >= r_squared_limit:
                riders_with_high_cp_fidelity.append(rider_cp_data)
                count_of_riders_with_high_fidelity_cp_data += 1

        logger.info(f"Rider ID {rider_cp_data.zwiftid} model preferred: {rider_cp_data.model_applied}")

    logger.info(f"\nTotal riders on ZwiftPower from DaveK: {cp_count + inverse_count}\n\nCP model superior : {cp_count}\n\nInverse model superior : {inverse_count}\n\nInsufficient data : {skipped_modelling_count}\n\nR-squared value worse (less than) {r_squared_limit} : {count_of_riders_with_poor_r_squared}\n\nRMSE value worse (more than) {rmse_limit}W : {count_of_riders_with_poor_rmse}\n\n")

    logger.info(f"Riders with high fidelity CP data (R-squared >= {r_squared_limit}) : {count_of_riders_with_high_fidelity_cp_data}\n\n")

    # for  riders_with_high_cp_fidelity, write out the zwiftID, name, cp, and r_squared. sorted by name
    riders_with_high_cp_fidelity.sort(key=lambda x: x.name)
    for rider in riders_with_high_cp_fidelity:
        logger.info(f"Rider ID {rider.zwiftid} :  CP = {round(rider.critical_power)}W  P60min = {round(rider.critical_power_p_1hour_predicted)}W  r_squared = {round(rider.critical_power_model_r_squared,2)}")

    OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betelV3.json"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    write_dict_of_cpdata(raw_cp_dict_for_everybody_in_the_club, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    # for rider_id, rider_cp_data in raw_cp_dict_for_everybody_in_the_club.items():
    #     cp_data = rider_cp_data.export_cp_data()  # Export critical power data as a dictionary
    #     table_data = [[x, y] for x, y in cp_data.items()]  # Convert dictionary to a list of [x, y] pairs
    #     table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

    #     logger.info(f"Critical Power Data for Rider ID: {rider_id}  Rider Name: {rider_cp_data.name}/n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

if __name__ == "__main__":
    main()


