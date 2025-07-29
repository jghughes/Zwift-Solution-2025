"""
N.B. THIS CONCISE TOOL IS USED DIRECTLY IN THE BRUTE PRODUCTION
PIPELINE. It builds on all the previous tools.

Each time a batch of raw data is received from DaveK, run this tool10
to generate a JSON dictionary file of all actively racing club
members, with all relevant data aggregated in a ZsunRiderItem for each
rider. Copy the JSON file manually into the data folder in Zsun01,
carefully following the naming convention there and updating
filenames.py accordingly. Older JSON files remain in the data folder
for posterity.

This tool aggregates, models, and exports comprehensive rider data for
all eligible club members using multiple data sources and power curve
models. As long as the riders are eligible, they are included
regardless of the fidelity of their best fit curves.

The script performs the following steps:
- Configures logging for the application.
- Loads Zwift, ZwiftPower, and ZwiftRacingApp profiles, as well as best
  power data, using a unified data repository.
- Identifies the set of eligible riders with complete and valid data
  across all sources.
- Retrieves and applies precomputed power curve fitting results for
  each rider.
- Constructs a unified rider data object for each member, combining
  demographic, performance, and modeled metrics.
- Filters out riders without valid curve fitting results.
- Exports the full set of rider profiles to both JSON and Excel files
  for use by Brute in production.

This tool demonstrates large-scale data integration, model application,
and dataset preparation for club-level cycling analytics and reporting.
"""


import numpy as np
import pandas as pd
from dataclasses import asdict
from jgh_number import safe_divide
from jgh_sanitise_string import cleanup_name_string
from handy_utilities import *
from jgh_serialization import *
from jgh_read_write import write_json_file, write_pandas_dataframe_as_xlsx
from jgh_power_curve_fit_models import decay_model_numpy
from zsun_rider_item import ZsunRiderItem
from scraped_zwift_data_repository import ScrapedZwiftDataRepository

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

def main():
    
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/power-graph-watts/"


    repository : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()
    repository.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 
    eligible_IDs = repository.get_list_of_filtered_intersections_of_sets("y","y_or_n","y_or_n","y") 

    logger.info(f"Imported {len(repository.dict_of_ZwiftProfileItem)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(repository.dict_of_ZwiftrRacingAppProfileItem)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(repository.dict_of_ZwiftPowerProfileItem)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(repository.dict_of_ZwiftPowerBestPowerDTO_as_ZsunBestPowerItem)} zwiftpower CP graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")

    # do everybody
    rider_ids_found = eligible_IDs
    logger.info(f"Using all {len(eligible_IDs)} eligible IDs from repository. Subset of rider IDs not requested. No filtering required.")
    filename_without_ext = "everyone_ZsunRiderItems_for_copying_manually_into_ZSUN01"

    # # just do betel
    # rider_IDs = get_betel_IDs()
    # filename_without_ext = "betel_ZsunRiderItems_for_copying_manually_into_ZSUN01"
    # rider_ids_not_found = [rider_id for rider_id in rider_IDs if rider_id not in eligible_IDs]
    # rider_ids_found = list(set(rider_IDs) - set(rider_ids_not_found))
    # logger.info(f"Betel/rider IDs not found in repository: {len(rider_ids_not_found)}\n{rider_ids_not_found}\n")
    # logger.info(f"Betel/rider IDs found in repository:{len(rider_ids_found)}\n {rider_ids_found}\n")

    answer_dict : dict[str, ZsunRiderItem] = dict[str, ZsunRiderItem]()

    dict_of_curve_fits = repository.get_dict_of_CurveFittingResult(rider_ids_found)
    
    for key in repository.get_dict_of_ZwiftProfileItem(rider_ids_found):
        zwift = repository.dict_of_ZwiftProfileItem[key]
        zwiftpower = repository.dict_of_ZwiftPowerProfileItem[key]
        zwiftracingapp = repository.dict_of_ZwiftrRacingAppProfileItem[key]

        if key in repository.dict_of_ZwiftrRacingAppProfileItem:
            name = repository.dict_of_ZwiftrRacingAppProfileItem[key].fullname or f"{zwift.first_name} {zwift.last_name}"
        else:
            name = f"{zwift.first_name} {zwift.last_name}"

        zsun_curve_fit = dict_of_curve_fits[key]

        p60 = decay_model_numpy(np.array([3_600]), zsun_curve_fit.one_hour_curve_coefficient, zsun_curve_fit.one_hour_curve_exponent)
        one_hour_watts =  p60[0]

        zwift = ZsunRiderItem(
            zwift_id                          = zwift.zwift_id,
            name                              = cleanup_name_string(name),
            weight_kg                         = round(         safe_divide(zwift.weight_grams,1_000.0)          , 1),
            height_cm                         = round(safe_divide(zwift.height_mm,10.0)),
            gender                            = "m" if zwift.male else "f",
            age_years                         = zwift.age_years,
            age_group                          = zwiftracingapp.age_group,
            zwift_ftp                         = round(zwift.ftp),
            zwiftpower_zFTP                   = round(zwiftpower.zftp),
            zwiftracingapp_zpFTP              = round(zwiftracingapp.zp_FTP),
            zsun_one_hour_watts               = round(one_hour_watts),
            zsun_CP                           = zsun_curve_fit.CP,
            zsun_AWC                          = zsun_curve_fit.AWC,
            zwift_zrs                         = round(zwift.competitionMetrics.racingScore),
            zwift_cat                         = zwift.competitionMetrics.category,
            zwiftracingapp_score              = round(zwiftracingapp.raceitem.max90.rating),
            zwiftracingapp_cat_num            = zwiftracingapp.raceitem.max90.mixed.number,
            zwiftracingapp_cat_name           = zwiftracingapp.raceitem.max90.mixed.category,
            zwiftracingapp_CP                 = round(zwiftracingapp.poweritem.CP),
            zwiftracingapp_AWC                = round(safe_divide(zwiftracingapp.poweritem.AWC,1_000.0)),
            zsun_one_hour_curve_coefficient   = zsun_curve_fit.one_hour_curve_coefficient,
            zsun_one_hour_curve_exponent      = zsun_curve_fit.one_hour_curve_exponent,
            zsun_TTT_pull_curve_coefficient   = zsun_curve_fit.TTT_pull_curve_coefficient,
            zsun_TTT_pull_curve_exponent      = zsun_curve_fit.TTT_pull_curve_exponent,
            zsun_TTT_pull_curve_fit_r_squared = round(zsun_curve_fit.TTT_pull_curve_r_squared,2),
            zsun_when_curves_fitted           = zsun_curve_fit.when_curves_fitted,
        )

        answer_dict[key] = zwift

    # filter out all items in dict where item.zsun_when_curves_fitted is blank
    answer_dict = {k: v for k, v in answer_dict.items() if v.zsun_when_curves_fitted != ""}

    write_json_file(JghSerialization.serialise(answer_dict), f"{filename_without_ext}.json", OUTPUT_DIRPATH)
    logger.info(f"Saved {len(answer_dict)} line-items in: {filename_without_ext}.json  DirPath: {OUTPUT_DIRPATH}")

    df = pd.DataFrame([asdict(rider) for rider in answer_dict.values()])
    write_pandas_dataframe_as_xlsx(df,  f"{filename_without_ext}.xlsx", OUTPUT_DIRPATH)
    logger.info(f"Saved {len(answer_dict)} line-items in: {filename_without_ext}.xlsx  DirPath: {OUTPUT_DIRPATH}")


if __name__ == "__main__":
    main()
