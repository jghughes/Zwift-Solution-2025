from handy_utilities import read_many_zwiftpower_bestpower_files_in_folder, read_many_zwift_profile_files_in_folder
import critical_power as cp
from dataclasses import dataclass


@dataclass
class CurveFittingResult:
    zwift_id: str
    name: str
    ftp_watts: float
    pull_watts: float
    pull_percent : float
    critical_power_watts: float
    anaerobic_work_capacity_kJ: float
    r_squared_pull: float
    r_squared_ftp: float

def main():
    # configure logging

    import logging
    import numpy as np
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # get all the data
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    dict_of_profiles_for_everybody = read_many_zwift_profile_files_in_folder(None, ZWIFT_PROFILES_DIRPATH)

    dict_of_bestpower_for_everybody = read_many_zwiftpower_bestpower_files_in_folder(None, ZWIFTPOWER_GRAPHS_DIRPATH)

    logger.info(f"Successfully read, validated, and loaded {len(dict_of_bestpower_for_everybody)} bestpower graphs from ZwiftPower files in:- \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n\n")

    # create a list of zwiftrider objects from the raw data

    total_count = 0
    skipped_modelling_count = 0
    count_of_riders_with_high_fidelity_models = 0
    count_of_riders_with_low_fidelity_models = 0

    r_squared_limit = .90

    zwiftIds_with_high_fidelity : list[str] = []
    zwiftids_with_low_fidelity : list[str] = []

    power_curves_for_everybody : dict[str, CurveFittingResult] = {}

    for my_zwift_id, my_jghbestpoweritem in dict_of_bestpower_for_everybody.items():

        my_jghbestpoweritem.zwift_id = my_zwift_id

        total_count += 1

        # skip riders with no data
        datapoints = my_jghbestpoweritem.export_all_x_y_ordinates()

        if not datapoints:
            logger.warning(f"ZwiftID {my_jghbestpoweritem.zwift_id} has no datapoints")
            skipped_modelling_count += 1
            continue

        #skip riders where all the datapoints are zero
        if all(value == 0 for value in datapoints.values()):
            logger.warning(f"ZwiftID {my_jghbestpoweritem.zwift_id} has empty data")
            skipped_modelling_count += 1
            continue
        
        # succeess - on we go

        # obtain raw xy data for the various ranges - critical_power, pull, and ftp

        raw_xy_data_cp = my_jghbestpoweritem.export_x_y_ordinates_for_cp_w_prime_modelling()
        raw_xy_data_pull = my_jghbestpoweritem.export_x_y_ordinates_for_pull_zone_modelling()
        raw_xy_data_ftp = my_jghbestpoweritem.export_x_y_ordinates_for_ftp_modelling()

        # skip riders where any of the three datasets contain less than 5 points
        if len(raw_xy_data_cp) < 5 or len(raw_xy_data_pull) < 5 or len(raw_xy_data_ftp) < 5:
            logger.warning(f"ZwiftID {my_jghbestpoweritem.zwift_id} has insufficient data for modelling")
            skipped_modelling_count += 1
            continue

        # do power modelling
    
        critical_power, anaerobic_work_capacity, _, _, _  = cp.do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)
        coefficient_pull, exponent_pull, r_squared_pull, _, _ = cp.do_curve_fit_with_decay_model(raw_xy_data_pull)
        coefficient_ftp, exponent_ftp, r_squared_ftp, _, _ = cp.do_curve_fit_with_decay_model(raw_xy_data_ftp)

        pull_short = cp.decay_model_numpy(np.array([300]), coefficient_pull, exponent_pull)
        pull_medium = cp.decay_model_numpy(np.array([600]), coefficient_pull, exponent_pull)
        pull_long = cp.decay_model_numpy(np.array([1800]), coefficient_pull, exponent_pull)
        ftp = cp.decay_model_numpy(np.array([60*60]), coefficient_ftp, exponent_ftp)

        # load results into answer

        #load results into a dataclass
        curve = CurveFittingResult(
            zwift_id=my_zwift_id,
            name=dict_of_profiles_for_everybody[my_zwift_id].first_name + " " + dict_of_profiles_for_everybody[my_zwift_id].last_name,
            ftp_watts= round(ftp[0]), 
            pull_watts = round(pull_short[0]),
            pull_percent = round(100*pull_short[0]/ftp[0]),
            critical_power_watts=round(critical_power),
            anaerobic_work_capacity_kJ=round((anaerobic_work_capacity/1_000.0),1),
            r_squared_pull=round(r_squared_pull,2),
            r_squared_ftp=round(r_squared_ftp,2),
        )

        power_curves_for_everybody[str(my_jghbestpoweritem.zwift_id)] = curve

        # log results for my_jghbestpoweritem

        summary_cp_w_prime  =  f"Critical Power = {round(critical_power)}W  Anaerobic Work Capacity = {round(anaerobic_work_capacity/1_000)}kJ"
        summary_pull = f"Pull power (30 - 60 - 120 seconds) = {round(pull_short[0])} - {round(pull_medium[0])} - {round(pull_long[0])}W"
        summary_ftp = f"Functional Threshold Power = {round(ftp[0])}W"

        logger.info(f"\n{summary_cp_w_prime}")
        logger.info(f"{summary_pull}")
        logger.info(f"{summary_ftp}")

        if r_squared_pull >= r_squared_limit and r_squared_ftp >= r_squared_limit:
            zwiftIds_with_high_fidelity.append(my_jghbestpoweritem.zwift_id)
            count_of_riders_with_high_fidelity_models += 1
        else:
            zwiftids_with_low_fidelity.append(my_jghbestpoweritem.zwift_id)
            count_of_riders_with_low_fidelity_models += 1

    modelled_count = total_count - skipped_modelling_count

    logger.info(f"\nTotal riders on ZwiftPower from DaveK: {total_count}  Insufficient data : {skipped_modelling_count}  Modelled count: {modelled_count}")

    logger.info(f"Riders with lower fidelity models [r_squared < {r_squared_limit}]: {count_of_riders_with_low_fidelity_models} ({round(100.0 * count_of_riders_with_low_fidelity_models/modelled_count)}%)")
    logger.info(f"Riders with high fidelity models [r_squared > {r_squared_limit}] : {count_of_riders_with_high_fidelity_models} ({round(100.0*count_of_riders_with_high_fidelity_models/modelled_count)}%)\n\n")

    # for  zwiftIds_with_high_fidelity, write out the zwiftID, name, critical_power, and r_squared_cp. sorted by name
    zwiftIds_with_high_fidelity.sort(key=lambda x: x)
    for zwift_id in zwiftIds_with_high_fidelity:
        logger.info(f"ZwiftID {zwift_id}")
        # betel = get_betel(zwift_id)
        # logger.info(f"ZwiftID {zwift_id} : {betel.name}")

    # load power_curves_for-everybody into pandas dataframe, sort by ftp_watts, and write to csv file

    import pandas as pd
    from dataclasses import asdict

    # Create the first DataFrame from dict_of_profiles_for_everybody
    df1 = pd.DataFrame([asdict(value) for value in dict_of_profiles_for_everybody.values()])

    # Create the second DataFrame from power_curves_for_everybody
    df2 = pd.DataFrame([asdict(value) for value in power_curves_for_everybody.values()])

    # Merge the two DataFrames on the identifier columns
    merged_df = pd.merge(df1, df2, left_on="zwift_id", right_on="zwift_id", suffixes=('_profile', '_power'))

    # Sort the merged DataFrame by the "ftp_watts" column
    merged_df = merged_df.sort_values(by="ftp_watts", ascending=False)

    # # Add an index column
    # merged_df.insert(0, 'index', range(1, len(merged_df) + 1))

    # write to excel
    OUTPUT_FILE_NAME = "power_curve_fitting_results_for_club_by_jgh.xlsx"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    merged_df.to_excel(OUTPUT_DIR_PATH + OUTPUT_FILE_NAME, index=True)

if __name__ == "__main__":
    main()


