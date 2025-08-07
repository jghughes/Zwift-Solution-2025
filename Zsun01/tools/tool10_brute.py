"""
N.B. THIS CONCISE TOOL IS USED DIRECTLY IN THE BRUTE PRODUCTION
PIPELINE. It builds on all the previous tools.

Each time a batch of raw data is received from DaveK, run this tool10
to generate a master JSON dictionary file of all actively racing club
members, with all relevant data aggregated in a ZsunItem for each
rider. A batch of raw data consists of several thousand files. 
The master JSON dictionary file for July 2025 data contains 431 riders.

Copy the JSON file manually into the data folder in Zsun01,
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
from zsun_rider_item import ZsunItem
from repository_of_scraped_riders import RepositoryForScrapedDataFromDaveK
import logging
logger = logging.getLogger(__name__)

def main():

    repository : RepositoryForScrapedDataFromDaveK = RepositoryForScrapedDataFromDaveK()
    repository.populate_repository(None, ZWIFT_DIRPATH, ZWIFTRACINGAPP_DIRPATH, ZWIFTPOWER_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 

    eligible_IDs = repository.get_list_of_filtered_intersections_of_sets("y","y_or_n","y_or_n","y")

    logger.info(f"Using all {len(eligible_IDs)} eligible IDs from repository.")

    dict_of_zwiftItem = repository.get_dict_of_ZwiftItem(eligible_IDs)
    dict_of_ZwiftRacingAppItem = repository.get_dict_of_ZwiftRacingAppItem(eligible_IDs)
    dict_of_ZwiftPowerItem = repository.get_dict_of_ZwiftPowerItem(eligible_IDs)
    dict_of_ZsunWattsItem = repository.get_dict_of_ZsunWattsItem(eligible_IDs)
    dict_of_curve_fits = repository.get_dict_of_CurveFittingResultItem(eligible_IDs)

    logger.info(f"Imported {len(dict_of_zwiftItem)} zwift profiles from : - \nDir : {ZWIFT_DIRPATH}\n")
    logger.info(f"Imported {len(dict_of_ZwiftRacingAppItem)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_DIRPATH}\n")
    logger.info(f"Imported {len(dict_of_ZwiftPowerItem)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_DIRPATH}\n")
    logger.info(f"Imported {len(dict_of_ZsunWattsItem)} zwiftpower 90-day best graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")

    answer_dict : dict[str, ZsunItem] = dict[str, ZsunItem]()

   
    for key in dict_of_zwiftItem:
        zwift = dict_of_zwiftItem[key]
        zwiftpower = dict_of_ZwiftPowerItem[key]
        zwiftracingapp = dict_of_ZwiftRacingAppItem[key]

        if key in dict_of_ZwiftRacingAppItem:
            name = dict_of_ZwiftRacingAppItem[key].fullname or f"{zwift.first_name} {zwift.last_name}"
        else:
            name = f"{zwift.first_name} {zwift.last_name}"

        zsun_curve_fit = dict_of_curve_fits[key]

        p60 = decay_model_numpy(np.array([3_600]), zsun_curve_fit.one_hour_curve_coefficient, zsun_curve_fit.one_hour_curve_exponent)
        one_hour_watts =  p60[0]

        zwift = ZsunItem(
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

    write_json_file(JghSerialization.serialise(answer_dict), f"{OUTPUT_FILENAME_WITHOUT_EXT}.json", OUTPUT_DIRPATH)
    logger.info(f"Saved {len(answer_dict)} line-items in: {OUTPUT_FILENAME_WITHOUT_EXT}.json  DirPath: {OUTPUT_DIRPATH}")

    df = pd.DataFrame([asdict(rider) for rider in answer_dict.values()])
    write_pandas_dataframe_as_xlsx(df,  f"{OUTPUT_FILENAME_WITHOUT_EXT}.xlsx", OUTPUT_DIRPATH)
    logger.info(f"Saved {len(answer_dict)} line-items in: {OUTPUT_FILENAME_WITHOUT_EXT}.xlsx  DirPath: {OUTPUT_DIRPATH}")

if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logging.getLogger("numba").setLevel(logging.ERROR) # numba is noisy at INFO level

    from dirpaths import ZWIFT_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH, ZWIFTRACINGAPP_DIRPATH, ZWIFTPOWER_DIRPATH

    OUTPUT_FILENAME_WITHOUT_EXT = "everyone_ZsunItems_for_copying_manually_into_ZSUN01_data_folder" # the meat

    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"

    main()
