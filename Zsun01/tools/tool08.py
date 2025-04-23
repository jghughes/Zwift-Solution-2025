from handy_utilities import write_dict_of_cpdata, read_many_zwiftpower_graph_files_in_folder
import critical_power as cp
from zwiftrider_related_items import ZwiftPower90DayBestGraphItem, ZwiftRiderPowerItem
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

    INPUT_ZWIFTPOWER_GRAPH_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    raw_cp_dict_for_everybody_in_the_club = read_many_zwiftpower_graph_files_in_folder(None, INPUT_ZWIFTPOWER_GRAPH_FROM_DAVEK_DIRPATH)

    logger.info(f"Successfully read, validated, and loaded {len(raw_cp_dict_for_everybody_in_the_club)} power graphs from ZwiftPower files in:- \nDir : {INPUT_ZWIFTPOWER_GRAPH_FROM_DAVEK_DIRPATH}\n\n")

    total_count = 0
    skipped_modelling_count = 0
    count_of_riders_with_poor_ftp_r_squared = 0
    count_of_riders_with_poor_pull_r_squared = 0
    count_of_riders_with_high_fidelity_models = 0

    r_squared_limit = .90

    riders_with_high_fidelity : list[int] = []

    for rider_id, rider in raw_cp_dict_for_everybody_in_the_club.items():

        total_count += 1

        # skip riders with no data
        datapoints = rider.export_zwiftpower_graph_data()

        if not datapoints:
            logger.warning(f"Rider ID {rider.zwiftid} has no datapoints")
            skipped_modelling_count += 1
            continue

        #skip riders where all the datapoints are zero
        if all(value == 0 for value in datapoints.values()):
            logger.warning(f"Rider ID {rider.zwiftid} has empty data")
            skipped_modelling_count += 1
            continue
        
        # succeess - on we go

        # obtain raw xy data for the various ranges - cp, pull, and ftp

        raw_xy_data_cp = rider.export_zwiftpower_90day_best_graph_for_cp_w_prime_modelling()
        raw_xy_data_pull = rider.export_zwiftpower_90day_best_graph_for_pull_zone_modelling()
        raw_xy_data_ftp = rider.export_zwiftpower_90day_best_graph_for_ftp_modelling()

        # skip riders where any of the three datasets contain less than 3 points
        if len(raw_xy_data_cp) < 3 or len(raw_xy_data_pull) < 3 or len(raw_xy_data_ftp) < 3:
            logger.warning(f"Rider ID {rider.zwiftid} has insufficient data for modelling")
            skipped_modelling_count += 1
            continue

        # do power modelling
    
        critical_power, anaerobic_work_capacity, _, _, _  = cp.do_modelling_with_cp_w_prime_model(raw_xy_data_cp)
        coefficient_pull, exponent_pull, r_squared_pull, _, _ = cp.do_modelling_with_decay_model(raw_xy_data_pull)
        coefficient_ftp, exponent_ftp, r_squared_ftp, _, _ = cp.do_modelling_with_decay_model(raw_xy_data_ftp)

        pull_short = cp.decay_model_numpy(np.array([300]), coefficient_pull, exponent_pull)
        pull_medium = cp.decay_model_numpy(np.array([600]), coefficient_pull, exponent_pull)
        pull_long = cp.decay_model_numpy(np.array([1800]), coefficient_pull, exponent_pull)
        ftp = cp.decay_model_numpy(np.array([60*60]), coefficient_ftp, exponent_ftp)

        # load results into answer

        power_item = ZwiftRiderPowerItem(zwiftid=int(rider_id), name=rider.name)
        power_item.cp_watts = critical_power
        power_item.pull_short_watts = pull_short[0]
        power_item.pull_medium_watts = pull_medium[0]
        power_item.pull_long_watts = pull_long[0]
        power_item.ftp_watts = ftp[0]
        power_item.adjustment_watts = 0
        power_item.cp_w_prime = anaerobic_work_capacity
        power_item.ftp_coefficient = coefficient_ftp
        power_item.ftp_exponent = exponent_ftp
        power_item.pull_coefficient = coefficient_pull
        power_item.pull_exponent = exponent_pull
        power_item.ftp_r_squared = r_squared_ftp
        power_item.pull_r_squared = r_squared_pull
        power_item.when_models_fitted = datetime.now().isoformat()

        # log summary of everything

        summary_cp_w_prime  =  f"Critical Power = {round(critical_power)}W  Anaerobic Work Capacity = {round(anaerobic_work_capacity/1_000)}kJ"
        summary_pull = f"Pull power (30 - 60 - 120 seconds) = {round(pull_short[0])} - {round(pull_medium[0])} - {round(pull_long[0])}W"
        summary_ftp = f"Functional Threshold Power = {round(ftp[0])}W"

        # logger.info(f"\n{summary_cp_w_prime}")
        # logger.info(f"\n{summary_pull}")
        # logger.info(f"\n{summary_ftp}")

        if r_squared_pull < r_squared_limit:
            logger.warning(f"Rider ID {rider.zwiftid} has R-squared values worse than {r_squared_limit} for pull range: {r_squared_pull}")
            count_of_riders_with_poor_pull_r_squared += 1
        
        if r_squared_ftp < r_squared_limit:
            logger.warning(f"Rider ID {rider.zwiftid} has R-squared values worse than {r_squared_limit} for ftp range: {r_squared_ftp}")
            count_of_riders_with_poor_ftp_r_squared += 1

        if r_squared_pull >= r_squared_limit and r_squared_ftp >= r_squared_limit:
            riders_with_high_fidelity.append(rider.zwiftid)
            count_of_riders_with_high_fidelity_models += 1


    logger.info(f"\nTotal riders on ZwiftPower from DaveK: {total_count}\n\nInsufficient data : {skipped_modelling_count}\n\nR-squared value worse (less than) {r_squared_limit} : {count_of_riders_with_poor_ftp_r_squared}\n\n")

    logger.info(f"Riders with high fidelity graph : {count_of_riders_with_high_fidelity_models}\n\n")

    # # for  riders_with_high_fidelity, write out the zwiftID, name, cp, and r_squared_cp. sorted by name
    # riders_with_high_fidelity.sort(key=lambda x: x)
    # for rider in riders_with_high_fidelity:
    #     logger.info(f"Rider ID {rider.zwiftid} :  CP = {round(rider.cp_watts)}W  FTP = {round(rider.cp_model_p_1hour_extrapolated)}W  r_squared_cp = {round(rider.cp_model_r_squared,2)}")

    # OUTPUT_FILE_NAME = "extracted_input_cp_data_for_betel_rubbish.json"
    # OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    # write_dict_of_cpdata(raw_cp_dict_for_everybody_in_the_club, OUTPUT_FILE_NAME, OUTPUT_DIR_PATH)

    # from tabulate import tabulate

    # log all the x and y data for all riders in pretty tables

    # for rider_id, rider in raw_cp_dict_for_everybody_in_the_club.items():
    #     cp_data = rider.export_zwiftpower_graph_data()  # Export critical power data as a dictionary
    #     table_data = [[x, y] for x, y in cp_data.items()]  # Convert dictionary to a list of [x, y] pairs
    #     table_headers = ["Time (x) [seconds]", "Power (y) [watts]"]  # Define table headers

    #     logger.info(f"Critical Power Data for Rider ID: {rider_id}  Rider Name: {rider.name}/n" + tabulate(table_data, headers=table_headers, tablefmt="simple"))

if __name__ == "__main__":
    main()


