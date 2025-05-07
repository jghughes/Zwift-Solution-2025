# load Dave's zsun_cp data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Any
import pandas as pd
from zsun_rider_item import ZsunRiderItem
from dataclasses import asdict
from scraped_zwift_data_repository import ScrapedZwiftDataRepository
from jgh_sanitise_string import cleanup_name_string
from handy_utilities import *
from jgh_read_write import write_pandas_dataframe_as_xlsx
import numpy as np
from jgh_power_curve_fit_models import decay_model_numpy



import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO


def main():
  
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    repository : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()
    repository.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 
    zwift_ids = repository.get_list_of_filtered_intersections_of_sets("y","y_or_n","y_or_n","y")
    dict_of_curve_fits = repository.get_dict_of_CurveFittingResult(None)

    logger.info(f"Imported {len(repository.dict_of_zwiftprofileitem)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(repository.dict_of_zwiftracingappprofileitem)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(repository.dict_of_zwiftpowerprofileitem)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(repository.dict_of_jghbestpoweritem)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")

    zwift_profiles = [
        repository.dict_of_zwiftprofileitem[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in repository.dict_of_zwiftprofileitem
    ]
    items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in zwift_profiles]
    df = pd.DataFrame(items_as_attr_dicts)
    output_file_name = "candidate_zwift_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")
    logger.info(f"Saved {len(zwift_profiles)} zwift profiles to: {output_file_path}")

    answer_dict : dict[str, ZsunRiderItem] = dict[str, ZsunRiderItem]()

    for key in repository.dict_of_zwiftprofileitem:
        zwift = repository.dict_of_zwiftprofileitem[key]
        zwiftpower = repository.dict_of_zwiftpowerprofileitem[key]
        zwiftracingapp = repository.dict_of_zwiftracingappprofileitem[key]

        if key in repository.dict_of_zwiftracingappprofileitem:
            name = repository.dict_of_zwiftracingappprofileitem[key].fullname or f"{zwift.first_name} {zwift.last_name}"
        else:
            name = f"{zwift.first_name} {zwift.last_name}"

        zsun_curve_fit = dict_of_curve_fits[key]

        p60 = decay_model_numpy(np.array([3_600]), zsun_curve_fit.ftp_curve_coefficient, zsun_curve_fit.ftp_curve_exponent)

        one_hour_watts =  p60[0]


        zwift = ZsunRiderItem(
            zwift_id                   = zwift.zwift_id,
            name                       = cleanup_name_string(name),
            weight_kg                  = round((zwift.weight_grams or 0.0) / 1_000.0, 1),
            height_cm                  = round((zwift.height_mm or 0.0) / 10.0),
            gender                     = "m" if zwift.male else "f",
            age_years                  = zwift.age_years,
            agegroup                   = zwiftracingapp.agegroup,
            zwift_ftp                  = round(zwift.ftp),
            zwiftpower_zFTP            = round(zwiftpower.zftp),
            zwiftracingapp_zpFTP       = round(zwiftracingapp.zp_FTP),
            zsun_one_hour_watts         = round(one_hour_watts),
            zwift_zrs                  = round(zwift.competitionMetrics.racingScore),
            zwift_cat                  = zwift.competitionMetrics.category,
            zwiftracingapp_score        = round(zwiftracingapp.raceitem.max90.rating),
            zwiftracingapp_cat_num      = zwiftracingapp.raceitem.max90.mixed.number,
            zwiftracingapp_cat_name     = zwiftracingapp.raceitem.max90.mixed.category,
            zwiftracingapp_cp           = round(zwiftracingapp.poweritem.CP),
            zwiftracingapp_awc          = round(zwiftracingapp.poweritem.AWC/1000.0),
            zsun_pull_adjustment_watts  = 0.0,
            zsun_ftp_curve_coefficient  = zsun_curve_fit.ftp_curve_coefficient,
            zsun_ftp_curve_exponent     = zsun_curve_fit.ftp_curve_exponent,
            zsun_pull_curve_coefficient = zsun_curve_fit.pull_curve_coefficient,
            zsun_pull_curve_exponent    = zsun_curve_fit.pull_curve_exponent,
            zsun_cp                     = zsun_curve_fit.cp,
            zsun_w_prime                = zsun_curve_fit.w_prime,
            zsun_when_curves_fitted     = zsun_curve_fit.when_curves_fitted,
        )
        answer_dict[key] = zwift


    riders = answer_dict.values()

    logger.info(f"Created a minimally valid subset of zsun riders:  {len(answer_dict)}")

    df = pd.DataFrame([asdict(rider) for rider in riders])
    file_name = "minimally_valid_zsun_riders.xlsx"
    write_pandas_dataframe_as_xlsx(df, file_name, OUTPUT_DIRPATH)
    logger.info(f"Minimally valid subset of zsun riders: {len(answer_dict)}\nSaved to:  {OUTPUT_DIRPATH + file_name}")

    # Remove items where zwift_zrs is 0 or vvelo_cat_name is an empty string
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
    main()
