# load Dave's jgh_cp data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Dict, Optional, List, Tuple, Any
from collections import defaultdict
import pandas as pd
import numpy as np
from sympy import ZZ

from handy_utilities import get_betel_zwift_ids
import jgh_cp as cp
from zsun_rider_item import ZsunRiderItem
from dataclasses import dataclass,  asdict
from scraped_zwift_data_repository import ScrapedZwiftDataRepository# configure logging

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO


@dataclass
class CurveFittingResult:
    zwiftid: int
    name: str
    ftp_watts: float
    pull_watts: float
    pull_percent : float
    critical_power_watts: float
    anaerobic_work_capacity_kJ: float
    r_squared_pull: float
    r_squared_ftp: float

def main():
    
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"


    rep : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()

    rep.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 

    logger.info(f"Imported {len(rep.dict_of_zwiftprofileitem)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftracingappprofileitem)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpowerprofileitem)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpowercurveof90daybestpoweritem)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")


    zwift_ids = rep.get_list_of_filtered_intersections_of_sets("y","y_or_n","y_or_n","y")

    zwift_profiles = [
        rep.dict_of_zwiftprofileitem[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in rep.dict_of_zwiftprofileitem
    ]
    items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in zwift_profiles]
    df = pd.DataFrame(items_as_attr_dicts)
    output_file_name = "candidate_zwift_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")
    logger.info(f"Saved {len(zwift_profiles)} zwift profiles to: {output_file_path}")

    # items = [
    #     rep.dict_of_zwiftracingappprofileitem[zwift_id]
    #     for zwift_id in zwift_ids
    #     if zwift_id in rep.dict_of_zwiftracingappprofileitem
    # ]
    # items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in items]
    # df = pd.DataFrame(items_as_attr_dicts)
    # output_file_name = "candidate_zwiftracingapp_profiles.xlsx"
    # output_file_path = OUTPUT_DIRPATH + output_file_name
    # df.to_excel(output_file_path, index=False, engine="openpyxl")
    # logger.info(f"Saved {len(items)} zwiftracingapp profiles to: {output_file_path}")



    # items = [
    #     rep.dict_of_zwiftpowerprofileitem[zwift_id]
    #     for zwift_id in zwift_ids
    #     if zwift_id in rep.dict_of_zwiftpowerprofileitem
    # ]
    # items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in items]
    # df = pd.DataFrame(items_as_attr_dicts)
    # output_file_name = "candidate_zwiftpower_profiles.xlsx"
    # output_file_path = OUTPUT_DIRPATH + output_file_name
    # df.to_excel(output_file_path, index=False, engine="openpyxl")
    # logger.info(f"Saved {len(items)} zwiftpower profiles to: {output_file_path}")


    # items = [
    #     rep.dict_of_zwiftpowercurveof90daybestpoweritem[zwift_id]
    #     for zwift_id in zwift_ids
    #     if zwift_id in rep.dict_of_zwiftpowercurveof90daybestpoweritem
    # ]
    # items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in items]
    # df = pd.DataFrame(items_as_attr_dicts)
    # output_file_name = "candidate_zwiftpower_90day_bests.xlsx"
    # output_file_path = OUTPUT_DIRPATH + output_file_name
    # df.to_excel(output_file_path, index=False, engine="openpyxl")
    # logger.info(f"Saved {len(items)} zwiftpower 90day bests to: {output_file_path}")



















    # Step 4: Instantiate and initialize a Dict[str, OmnibusProfileDTO]
    dict_of_zsun_riders : dict[str, ZsunRiderItem] = dict[str, ZsunRiderItem]()
    
    for key in rep.dict_of_zwiftprofileitem:
        zwift_profile = rep.dict_of_zwiftprofileitem[key]
        if zwift_profile.zftp < 50 or zwift_profile.zwift_racing_score < 80:            
            # logger.warning(f"Skipped: low zFTP or poor ZRS: {zwift_profile.first_name} {zwift_profile.last_name}")
            continue
        jgh_best_power = rep.dict_of_zwiftpowercurveof90daybestpoweritem[key]
        if jgh_best_power.cp_10 == 0:
            # logger.warning(f"Skipped: no 90-day-best curve: {zwift_profile.first_name} {zwift_profile.last_name}")
            continue

        velo_profile = rep.dict_of_zwiftracingappprofileitem[key]
        velo_powerinfo = velo_profile.power

        zp_profile = rep.dict_of_zwiftpowerprofileitem[key]

        item = ZsunRiderItem(
            zwift_id                   = zwift_profile.zwift_id or "",
            name                       = f"{zwift_profile.last_name or ''}, {zwift_profile.first_name or ''}",
            weight_kg                  = (zwift_profile.weight_grams or 0.0) / 1_000.0,
            height_cm                  = (zwift_profile.height_mm or 0.0) / 10.0,
            gender                     = "m" if zwift_profile.male else "f",
            age_years                  = zwift_profile.age_years or 0.0,
            agegroup                   = zp_profile.age_group or "",
            zwift_zftp                 = zwift_profile.zftp or 0.0,
            zwift_zrs                  = zwift_profile.zwift_racing_score or 0,
            zwift_cat                  = zwift_profile.zwift_racing_category or "",
            velo_score                  = velo_powerinfo.compoundScore or 0.0,
            velo_cat_num                = velo_profile.race["90days"]. or 0,
            velo_cat_name               = zra_powerinfo.categoryName or "",
            velo_cp                     = zra_powerinfo.cp or 0.0,
            velo_awc                    = zra_powerinfo.awc or 0.0,
            # jgh_pull_adjustment_watts  = 
            # jgh_cp                     = 
            # jgh_w_prime                = 
            # jgh_ftp_curve_coefficient  = 
            # jgh_ftp_curve_exponent     = 
            # jgh_pull_curve_coefficient = 
            # jgh_pull_curve_exponent    = 
            # jgh_when_curves_fitted     = 
        )

        dict_of_zsun_riders[key] = item

    # logger.info(f"Step 4: Created dict_of_zsun_riders with {len(dict_of_zsun_riders)} entries.")

    # sorted_profiles = sorted(dict_of_zsun_riders.values(), key=lambda profile: profile.zwift_name or "")

    # df = pd.DataFrame([asdict(profile) for profile in sorted_profiles])

    # # Step 8: Save the DataFrame to an Excel file
    # OUTPUT_FILE_NAME = "omnibus_zsun_profiles_from_zwiftpower_and_zwiftracingapp.xlsx"
    # OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    # df.to_excel(OUTPUT_DIR_PATH + OUTPUT_FILE_NAME, index=True)
    # logger.info(f"Step 5: Saved the DataFrame to : - \nFilepath: {OUTPUT_DIR_PATH + OUTPUT_FILE_NAME}")



if __name__ == "__main__":
    main()
