# load Dave's critical_power data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Dict, Optional, List, Tuple, Any
from collections import defaultdict
import pandas as pd
import numpy as np

from handy_utilities import get_betel_zwift_ids
import critical_power as cp
from zsun_rider_item import ZsunRiderItem
from datetime import datetime
from dataclasses import dataclass,  asdict
from omnibus_profile_dto import OmnibusProfileDTO  # Import the DTO class
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

    logger.info(f"Imported {len(rep.dict_of_zwift_profileitem)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftracingapp_profileitem)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpower_profileitem)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpower_90daybest_poweritem)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")


    zwift_ids = rep.get_filtered_list_of_intersections_of_sets("y","y_or_n","y_or_n","y")

    zwift_profiles = [
        rep.dict_of_zwift_profileitem[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in rep.dict_of_zwift_profileitem
    ]
    items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in zwift_profiles]
    df = pd.DataFrame(items_as_attr_dicts)
    output_file_name = "candidate_zwift_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")
    logger.info(f"Saved {len(zwift_profiles)} zwift profiles to: {output_file_path}")

    # items = [
    #     rep.dict_of_zwiftracingapp_profileitem[zwift_id]
    #     for zwift_id in zwift_ids
    #     if zwift_id in rep.dict_of_zwiftracingapp_profileitem
    # ]
    # items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in items]
    # df = pd.DataFrame(items_as_attr_dicts)
    # output_file_name = "candidate_zwiftracingapp_profiles.xlsx"
    # output_file_path = OUTPUT_DIRPATH + output_file_name
    # df.to_excel(output_file_path, index=False, engine="openpyxl")
    # logger.info(f"Saved {len(items)} zwiftracingapp profiles to: {output_file_path}")



    # items = [
    #     rep.dict_of_zwiftpower_profileitem[zwift_id]
    #     for zwift_id in zwift_ids
    #     if zwift_id in rep.dict_of_zwiftpower_profileitem
    # ]
    # items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in items]
    # df = pd.DataFrame(items_as_attr_dicts)
    # output_file_name = "candidate_zwiftpower_profiles.xlsx"
    # output_file_path = OUTPUT_DIRPATH + output_file_name
    # df.to_excel(output_file_path, index=False, engine="openpyxl")
    # logger.info(f"Saved {len(items)} zwiftpower profiles to: {output_file_path}")


    # items = [
    #     rep.dict_of_zwiftpower_90daybest_poweritem[zwift_id]
    #     for zwift_id in zwift_ids
    #     if zwift_id in rep.dict_of_zwiftpower_90daybest_poweritem
    # ]
    # items_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in items]
    # df = pd.DataFrame(items_as_attr_dicts)
    # output_file_name = "candidate_zwiftpower_90day_bests.xlsx"
    # output_file_path = OUTPUT_DIRPATH + output_file_name
    # df.to_excel(output_file_path, index=False, engine="openpyxl")
    # logger.info(f"Saved {len(items)} zwiftpower 90day bests to: {output_file_path}")



















    # Step 4: Instantiate and initialize a Dict[str, OmnibusProfileDTO]
    dict_of_zsun_riders : dict[str, ZsunRiderItem] = dict[str, ZsunRiderItem]()
    
    for key in rep.dict_of_zwift_profileitem:
        zwift_profile = rep.dict_of_zwift_profileitem[key]
        if zwift_profile.zftp is None or zwift_profile.zftp < 100 or zwift_profile.zwift_racing_score is None or zwift_profile.zwift_racing_score < 50:            
            logger.warning(f"{zwift_profile.first_name} {zwift_profile.last_name} has poor zFTP or poor ZRS. Skipped")
            continue
        zwift_power_best_power = rep.dict_of_zwiftpower_90daybest_poweritem[key]

        if zwift_power_best_power.cp_10 == 0:
            logger.warning(f"{zwift_profile.first_name} {zwift_profile.last_name} has no 90-day data.")
            continue

        zwift_racingapp_profile = rep.dict_of_zwiftracingapp_profileitem[key]
        zwift_power_profile = rep.dict_of_zwiftpower_profileitem[key]
        item = ZsunRiderItem(
            zwift_id                = zwift_profile.zwift_id or "",
            name                    = f"{zwift_profile.first_name or ''} {zwift_profile.last_name or ''}",
            weight_kg               = (zwift_profile.weight_grams or 0.0)/1_000.0,
            height_cm               = (zwift_profile.height_mm or 0.0)/10.0,
            gender                  = zwift_profile.gender or "",
            age_years               = zwift_profile.age_years or 0.0,
            age_group               = zwift_profile.age_group or "",
            zftp                    = zwift_profile.zftp or 0.0,
            zwift_racing_score      = zwift_profile.zwift_racing_score or 0,
            zwift_racing_category   = zwift_profile.zwift_racing_category or "",
            velo_rating             = zwift_power_profile.velo_rating or 0,
            pull_adjustment_watts   = zwift_power_profile.pull_adjustment_watts or 0.0,
            critical_power          = zwift_power_best_power.critical_power or 0.0,
            critical_power_w_prime  = zwift_power_best_power.critical_power_w_prime or 0.0,
            ftp_curve_coefficient   = zwift_power_profile.ftp_curve_coefficient or 0.0,
            ftp_curve_exponent      = zwift_power_profile.ftp_curve_exponent or 0.0,
            pull_curve_coefficient  = zwift_power_profile.pull_curve_coefficient or 0.0,
            pull_curve_exponent     = zwift_power_profile.pull_curve_exponent or 0.0,
            when_curves_fitted      = zwift_power_profile.when_curves_fitted or ""
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
