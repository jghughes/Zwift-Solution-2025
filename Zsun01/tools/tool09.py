"""
This tool is not used directly in the Brute production pipeline. I wrote
this tool to develop a dictionary of minimally-valid ZsunItem and
save it to Excel for eyeballing. In tool08 my focus was on exploring a
suitable value to cut-off poor curve fits. In this tool09, I couldn't
care less about the quality of curve fits; instead I am concerned about
filtering and selecting riders who are deemed to be recently active
racers regardless of their curve fits.

I went to a lot of trouble to write methods in the
RepositoryForScrapedDataFromDaveK that return unions/intersections as subsets
of power data from Zwift, ZwiftPower, and ZwiftRacingApp profiles
respectively in order to discover and fine tune how many riders are or
are not common to any two or three of them and to get to the bottom of
choosing only currently active racers with a valid zwift racing score
and velo racing score who deserve to be in the JSON database for Brute
riders. One of the metrics I eyeball as a matter of curiosity in the
output is zsun_TTT_pull_curve_fit_r_squared to monitor the fidelity of
curve fits in the pull zone. Some are much better than others, but I
don't filter out any of them, as I want to see the full range of curve
fits in Excel and their r-squared values. In the April 2025 dataset,
pull r-squared values for active racers range from 0.997 at best to
0.673 at worst. In the July 2025 dataset, the comparable values are
0.994 at best and 0.528 at worst.

In the April 2025 dataset, there were 1,514 riders in the club, and 304
actively racing riders. The comparable figures for July 2025 are 1,552
riders in the club and 264 actively racing riders.

This tool loads myriad files from Zwift, ZwiftPower, and ZwiftRacingApp
obtained by DaveK. It aggregates, models, and exports comprehensive
rider data for all club members using the multiple data sources and
power curve models.

The script performs the following steps:
- Configures logging for the application.
- Loads Zwift, ZwiftPower, and ZwiftRacingApp profiles, as well as best
  power data, using a unified data repository.
- Identifies the set of riders with complete and valid data across all
  sources.
- Retrieves and applies precomputed power curve fitting results for
  each rider.
- Constructs a unified rider data object (ZsunItem) for each
  member, combining demographic, performance, and modeled metrics.
- Exports the full set of rider profiles to Excel for further analysis.
- Filters the dataset to include only recently active riders (based on
  racing score and velo category), and exports this subset to a
  separate Excel file.

This tool demonstrates large-scale data integration, model application,
and dataset preparation for club-level cycling analytics and reporting.
Note the use of Pandas for data manipulation and export to Excel, as
well as NumPy for numerical operations related to power curve modeling.
"""
from typing import Any
from dataclasses import asdict
import pandas as pd
import numpy as np
from jgh_number import safe_divide
from jgh_sanitise_string import cleanup_name_string
from handy_utilities import *
from jgh_read_write import write_pandas_dataframe_as_xlsx
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

    zwift_profiles = [
        dict_of_zwiftItem[zwift_id]
        for zwift_id in eligible_IDs
        if zwift_id in dict_of_zwiftItem
    ]
    items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in zwift_profiles]
    df = pd.DataFrame(items_as_attr_dicts)
    output_file_name = "candidate_zwift_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")
    logger.info(f"Saved {len(zwift_profiles)} zwift profiles to: {output_file_path}")

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
            weight_kg                         = round((safe_divide(zwift.weight_grams, 1_000.0)), 1),
            height_cm                         = round(safe_divide(zwift.height_mm, 10.0 )),
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
            zwiftracingapp_AWC                = round(safe_divide(zwiftracingapp.poweritem.AWC, 1_000.0)),
            zsun_one_hour_curve_coefficient   = zsun_curve_fit.one_hour_curve_coefficient,
            zsun_one_hour_curve_exponent      = zsun_curve_fit.one_hour_curve_exponent,
            zsun_TTT_pull_curve_coefficient   = zsun_curve_fit.TTT_pull_curve_coefficient,
            zsun_TTT_pull_curve_exponent      = zsun_curve_fit.TTT_pull_curve_exponent,
            zsun_TTT_pull_curve_fit_r_squared = zsun_curve_fit.TTT_pull_curve_r_squared,
            zsun_when_curves_fitted           = zsun_curve_fit.when_curves_fitted,
        )
        answer_dict[key] = zwift


    riders = answer_dict.values()

    logger.info(f"Created a eligible subset of zsun riders:  {len(answer_dict)}")

    df = pd.DataFrame([asdict(rider) for rider in riders])
    file_name = "eligible_zsun_riders.xlsx"
    write_pandas_dataframe_as_xlsx(df, file_name, OUTPUT_DIRPATH)
    logger.info(f"Eligible subset of zsun riders: {len(answer_dict)}\nSaved to:  {OUTPUT_DIRPATH + file_name}")

    # Remove items where zwift_zrs is 0 or velo_cat_name is an empty string i.e. only keep those with a valid racing score and velo registration and category
    answer_dict = {
        key: value
        for key, value in answer_dict.items()
        if value.zwift_zrs != 0 and value.zwiftracingapp_cat_name != ''
    }

    riders = answer_dict.values()
    df = pd.DataFrame([asdict(rider) for rider in riders])
    file_name = "zsun_riders_recently_active.xlsx"
    write_pandas_dataframe_as_xlsx(df, file_name, OUTPUT_DIRPATH)
    logger.info(f"Active subset of zsun racers: {len(answer_dict)}\nSaved to:  {OUTPUT_DIRPATH + file_name}")


if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logging.getLogger("numba").setLevel(logging.ERROR) # numba is noisy at INFO level
        
    from dirpaths import ZWIFT_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH, ZWIFTRACINGAPP_DIRPATH, ZWIFTPOWER_DIRPATH


    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"


    main()
