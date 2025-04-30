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

    betel_zwift_ids = get_betel_zwift_ids()

    rep : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()

    rep.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 

    logger.info(f"Imported {len(rep.dict_of_zwift_profileDTO)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftracingapp_profileDTO)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpower_profileDTO)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpower_90daybest_graph_item)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")


    df = rep.get_filtered_table_of_intersections_of_sets("y","y","y","y")

   # Step 3: Extract Zwift IDs from the DataFrame
    zwift_ids : list[str] = df[ScrapedZwiftDataRepository.COL_ZWIFT_ID].tolist()

    # Step 4: Lookup corresponding entries in dict_of_zwift_profileDTO
    profile_objects = [
        rep.dict_of_zwift_profileDTO[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in rep.dict_of_zwift_profileDTO
    ]

    profiles_as_attr_dicts : list[dict[str, Any]]= [profile.model_dump() for profile in profile_objects]

    df = pd.DataFrame(profiles_as_attr_dicts)

    output_file_name = "beautiful_zwift_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")

    logger.info(f"Saved {len(profile_objects)} zwift profiles to: {output_file_path}")


    # Step 5: Lookup corresponding entries in dict_of_zwiftpower_profileDTO
    profile_objects = [
        rep.dict_of_zwiftpower_profileDTO[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in rep.dict_of_zwiftpower_profileDTO
    ]

    profiles_as_attr_dicts : list[dict[str, Any]]= [profile.model_dump() for profile in profile_objects]

    df = pd.DataFrame(profiles_as_attr_dicts)

    output_file_name = "beautiful_zwiftpower_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")

    logger.info(f"Saved {len(profile_objects)} zwiftpower profiles to: {output_file_path}")


    # Step 6: Lookup corresponding entries in dict_of_zwiftracingapp_profileDTO
    profile_objects = [
        rep.dict_of_zwiftracingapp_profileDTO[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in rep.dict_of_zwiftracingapp_profileDTO
    ]

    profiles_as_attr_dicts : list[dict[str, Any]]= [profile.model_dump() for profile in profile_objects]

    df = pd.DataFrame(profiles_as_attr_dicts)

    output_file_name = "beautiful_zwiftracingapp_profiles.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")

    logger.info(f"Saved {len(profile_objects)} zwiftracingapp profiles to: {output_file_path}")

    # Step 7: Lookup corresponding entries in dict_of_zwiftpower_90daybest_graph_item
    profile_objects = [
        rep.dict_of_zwiftpower_90daybest_graph_item[zwift_id]
        for zwift_id in zwift_ids
        if zwift_id in rep.dict_of_zwiftpower_90daybest_graph_item
    ]

    profiles_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in profile_objects]

    df = pd.DataFrame(profiles_as_attr_dicts)

    output_file_name = "beautiful_zwiftpower_90day_bests.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")

    logger.info(f"Saved {len(profile_objects)} zwiftpower 90day bests to: {output_file_path}")


























    # # Step 4: Instantiate and initialize a Dict[str, OmnibusProfileDTO]
    # dict_of_valid_keys : dict[str, OmnibusProfileDTO] = 
    # for key, value in zwiftracingapp_profiles:
    #     # Create a new OmnibusProfileDTO instance
    #     omnibus_profile = OmnibusProfileDTO()

    #     z = zwiftpower_profiles[key]
    #     # Directly assign values to attributes
    #     omnibus_profile.zwift_id = z.zwift_id
    #     omnibus_profile.profile_url = z.profile_url
    #     omnibus_profile.zwift_name = z.zwift_name
    #     omnibus_profile.race_ranking = z.race_ranking
    #     omnibus_profile.zwift_racing_score = z.zwift_racing_score
    #     omnibus_profile.zwift_racing_category = z.zwift_racing_category
    #     omnibus_profile.team = z.team
    #     omnibus_profile.zftp = z.zftp
    #     omnibus_profile.weight = z.weight
    #     omnibus_profile.age_group = z.age_group
    #     omnibus_profile.zpoints = z.zpoints
    #     omnibus_profile.country = z.country
    #     omnibus_profile.profile_image = z.profile_image
    #     omnibus_profile.strava_profile = z.strava_profile
    #     omnibus_profile.level = z.level

    #     # Add the OmnibusProfileDTO to the dictionary
    #     dict_of_valid_keys[key] = omnibus_profile

    # logger.info(f"Step 4: Created dict_of_valid_keys with {len(dict_of_valid_keys)} entries.")

    # sorted_profiles = sorted(dict_of_valid_keys.values(), key=lambda profile: profile.zwift_name or "")

    # df = pd.DataFrame([asdict(profile) for profile in sorted_profiles])

    # # Step 8: Save the DataFrame to an Excel file
    # OUTPUT_FILE_NAME = "omnibus_zsun_profiles_from_zwiftpower_and_zwiftracingapp.xlsx"
    # OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    # df.to_excel(OUTPUT_DIR_PATH + OUTPUT_FILE_NAME, index=True)
    # logger.info(f"Step 5: Saved the DataFrame to : - \nFilepath: {OUTPUT_DIR_PATH + OUTPUT_FILE_NAME}")



if __name__ == "__main__":
    main()
