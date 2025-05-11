from handy_utilities import *
from critical_power import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model, decay_model_numpy 
from datetime import datetime
from jgh_read_write import write_pandas_dataframe_as_xlsx
from scraped_zwift_data_repository import ScrapedZwiftDataRepository
from computation_classes import CurveFittingResult
from bestpower_for_model_training_item import BestPowerModelTrainingItem


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

    sample_IDs = None
    # sample_IDs = get_betel_IDs()

    dict_of_zwift_profiles_for_everybody = read_many_zwift_profile_files_in_folder(sample_IDs, ZWIFT_PROFILES_DIRPATH)

    dict_of_bestpower_for_everybody = read_many_zwiftpower_bestpower_files_in_folder(sample_IDs, ZWIFTPOWER_GRAPHS_DIRPATH)

    logger.info(f"Successfully read, validated, and loaded {len(dict_of_bestpower_for_everybody)} bestpower graphs from ZwiftPower files in:- \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n\n")

    # create a list of zwiftrider objects from the raw data

    total_count = 0
    skipped_modelling_count = 0
    valid_count = 0
    count_of_riders_with_high_fidelity_models = 0
    count_of_riders_with_low_fidelity_models = 0


    zwiftIds_with_high_fidelity : list[str] = []
    zwiftids_with_low_fidelity : list[str] = []

    power_curves_for_everybody : dict[str, CurveFittingResult] = {}

    for my_zwiftID, my_jghbestpoweritem in dict_of_bestpower_for_everybody.items():

        my_jghbestpoweritem.zwift_id = my_zwiftID

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
        raw_xy_data_ftp = my_jghbestpoweritem.export_x_y_ordinates_for_one_hour_zone_modelling()

        # skip riders where any of the three datasets contain less than 5 points
        if len(raw_xy_data_cp) < 5 or len(raw_xy_data_pull) < 5 or len(raw_xy_data_ftp) < 5:
            logger.warning(f"ZwiftID {my_jghbestpoweritem.zwift_id} has insufficient data for curve fitting")
            skipped_modelling_count += 1
            continue

        # do power modelling
    
        critical_power, anaerobic_work_capacity, _, _, _  = do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)
        coefficient_pull, exponent_pull, r_squared_pull, _, _ = do_curve_fit_with_decay_model(raw_xy_data_pull)
        coefficient_ftp, exponent_ftp, r_squared_ftp, _, _ = do_curve_fit_with_decay_model(raw_xy_data_ftp)

        pull_short = decay_model_numpy(np.array([300]), coefficient_pull, exponent_pull)
        pull_medium = decay_model_numpy(np.array([600]), coefficient_pull, exponent_pull)
        pull_long = decay_model_numpy(np.array([1800]), coefficient_pull, exponent_pull)
        ftp = decay_model_numpy(np.array([60*60]), coefficient_ftp, exponent_ftp)

        # load results into answer

        #load results into a dataclass
        curve = CurveFittingResult(
            zwift_id=my_zwiftID,
            one_hour_curve_coefficient=coefficient_ftp,
            one_hour_curve_exponent=exponent_ftp,
            one_hour_curve_r_squared=round(r_squared_ftp, 2),
            TTT_pull_curve_coefficient=coefficient_pull,
            TTT_pull_curve_exponent=exponent_pull,
            TTT_pull_curve_r_squared=round(r_squared_pull, 2),
            CP=round(critical_power),
            AWC=round((anaerobic_work_capacity / 1_000.0), 1),
            when_curves_fitted=datetime.now().isoformat()  # Add timestamp
        )
        power_curves_for_everybody[str(my_jghbestpoweritem.zwift_id)] = curve

        # log results for my_jghbestpoweritem

        summary_cp_w_prime  =  f"Zsun CP = {round(critical_power)}W  AWC = {round(anaerobic_work_capacity/1_000)}kJ"
        summary_pull = f"TTT pull power (30 - 60 - 120 seconds) = {round(pull_short[0])} - {round(pull_medium[0])} - {round(pull_long[0])}W"
        summary_ftp = f"One hour power = {round(ftp[0])}W"

        logger.info(f"\n{summary_cp_w_prime}")
        logger.info(f"{summary_pull}")
        logger.info(f"{summary_ftp}")

        r_squared_limit = .90

        if r_squared_ftp >= r_squared_limit:
        # if r_squared_pull >= r_squared_limit and r_squared_ftp >= r_squared_limit:
            zwiftIds_with_high_fidelity.append(my_jghbestpoweritem.zwift_id)
            count_of_riders_with_high_fidelity_models += 1
        else:
            zwiftids_with_low_fidelity.append(my_jghbestpoweritem.zwift_id)
            count_of_riders_with_low_fidelity_models += 1

        valid_count += 1

    modelled_count = total_count - skipped_modelling_count

    logger.info(f"\nTotal riders on ZwiftPower from DaveK: {total_count}  Insufficient data : {skipped_modelling_count}  Modelled count: {modelled_count}\n")

    # logger.info(f"Riders with lower fidelity models [r_squared < {r_squared_limit}]: {count_of_riders_with_low_fidelity_models} ({round(100.0 * count_of_riders_with_low_fidelity_models/modelled_count)}%)")
    logger.info(f"Riders with excellent TTT pull curve fits [r_squared > {r_squared_limit}] : {count_of_riders_with_high_fidelity_models} ({round(100.0*count_of_riders_with_high_fidelity_models/modelled_count)}%)")

    # for  zwiftIds_with_high_fidelity, write out the zwiftID, name, critical_power, and r_squared_cp. sorted by name
    zwiftIds_with_high_fidelity.sort(key=lambda x: x)
    for zwift_id in zwiftIds_with_high_fidelity:
        logger.info(f"ZwiftID {zwift_id} {dict_of_zwift_profiles_for_everybody[zwift_id].first_name} {dict_of_zwift_profiles_for_everybody[zwift_id].last_name}")
        # betel = get_betel_zsunriderItem(zwift_id)
        # logger.info(f"ZwiftID {zwift_id} : {betel.name}")

    logger.info(f"\nTotal in sample : {total_count} Total valid: {valid_count} Total excellent one hr r2: {count_of_riders_with_high_fidelity_models} % excellent/valid: {round(count_of_riders_with_high_fidelity_models *100/valid_count)}%\n")

    # load dict_of_zwift_profiles_for_everybody into pandas dataframe, sort by ftp_watts, and write to csv file

    import pandas as pd
    from dataclasses import asdict

    # Create the first DataFrame from dict_of_zwift_profiles_for_everybody
    df1 = pd.DataFrame([asdict(value) for value in dict_of_zwift_profiles_for_everybody.values()])

    # Create the second DataFrame from power_curves_for_everybody
    df2 = pd.DataFrame([asdict(value) for value in power_curves_for_everybody.values()])

    # Merge the two DataFrames on the identifier columns
    merged_df = pd.merge(df1, df2, left_on="zwift_id", right_on="zwift_id", suffixes=('_profile', '_power'))

    # write to excel
    OUTPUT_FILE_NAME = "power_curve_fitting_results_for_club_by_jgh.xlsx"
    write_pandas_dataframe_as_xlsx(merged_df, OUTPUT_FILE_NAME, OUTPUT_DIRPATH)
    logger.info(f"\nSaved {len(merged_df)} power curve fitting results to: {OUTPUT_DIRPATH + OUTPUT_FILE_NAME}\n")

    # map zwiftIds_with_high_fidelity into a list of custom objects and save to json file for use for sophisicated machine learning to determine zFTP

    repository : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()
    repository.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 
    dict_of_zsunriderItems : defaultdict[str, ZsunRiderItem] = repository.get_dict_of_ZsunRiderItem(zwiftIds_with_high_fidelity)
    dict_of_zp_90day_graph_watts : defaultdict[str,ZsunBestPowerItem] = repository.get_dict_of_ZwiftPowerBestPowerDTO_as_ZsunBestPowerItem(zwiftIds_with_high_fidelity)
    
    
    dict_of_riders_with_high_fidelity : defaultdict[str, BestPowerModelTrainingItem] = defaultdict(BestPowerModelTrainingItem)

    for ID in zwiftIds_with_high_fidelity:
        zwift = dict_of_zwift_profiles_for_everybody[ID]
        zsun = dict_of_zsunriderItems[ID]
        zp_90day_best = dict_of_zp_90day_graph_watts[ID]
        dict_of_riders_with_high_fidelity[ID] = BestPowerModelTrainingItem(
            zwift_id                   = ID,
            name                       = zsun.name,
            gender                     = zsun.gender,
            weight_kg                  = zsun.weight_kg,
            height_cm                  = zsun.height_cm,
            age_years                  = zsun.age_years,
            zwift_zrs                  = zsun.zwift_zrs,
            zwift_cat                  = zsun.zwift_cat,
            zwift_ftp                  = zwift.ftp,
            zsun_one_hour_watts        = round(zsun.get_n_second_watts(2400)),
            zwiftracingapp_zpFTP       = zsun.zwiftracingapp_zpFTP,
            zwiftracingapp_score       = zsun.zwiftracingapp_score,
            zwiftracingapp_cat_num     = zsun.zwiftracingapp_cat_num,
            zwiftracingapp_cat_name    = zsun.zwiftracingapp_cat_name,
            bp_5                       = zp_90day_best.bp_5,
            bp_15                      = zp_90day_best.bp_15,
            bp_30                      = zp_90day_best.bp_30,
            bp_60                      = zp_90day_best.bp_60,
            bp_180                     = zp_90day_best.bp_180,
            bp_300                     = zp_90day_best.bp_300,
            bp_600                     = zp_90day_best.bp_600,
            bp_720                     = zp_90day_best.bp_720,
            bp_900                     = zp_90day_best.bp_900,
            bp_1200                    = zp_90day_best.bp_1200,
            bp_1800                    = zp_90day_best.bp_1800,
            bp_2400                    = zp_90day_best.bp_2400,
        )

    # Create the third DataFrame from dict_of_riders_with_high_fidelity
    riders = dict_of_riders_with_high_fidelity.values()
    df3 = pd.DataFrame([asdict(modelTrainingItem) for modelTrainingItem in riders])

    file_name = "bestpower_dataset_for_model_training.xlsx"
    write_pandas_dataframe_as_xlsx(df3, file_name, OUTPUT_DIRPATH)
    logger.info(f"\nSaved {len(df3)} correlation data-set items to: {OUTPUT_DIRPATH}{file_name}\n")

    file_name = "bestpower_dataset_for_model_training.json"

    write_dict_of_bestpowermodeltrainingItems(dict_of_riders_with_high_fidelity, file_name, OUTPUT_DIRPATH)



if __name__ == "__main__":
    main()


