# load Dave's critical_power data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Dict, Optional, List, Tuple, Any
import pandas as pd
from dataclasses import asdict


from handy_utilities import write_dict_of_cpdata, read_many_zwiftpower_graph_files_in_folder, get_betel_zwift_ids, get_betel, read_many_zwiftpower_profile_files_in_folder, read_many_zwiftracingapp_profile_files_in_folder
import critical_power as cp
from zsun_rider_item import ZsunRiderItem
from datetime import datetime
from dataclasses import dataclass
from dataclasses import dataclass,  asdict
from omnibus_profile_dto import OmnibusProfileDTO  # Import the DTO class

# configure logging

import logging
import numpy as np
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
    # get all the data
    INPUT_ZWIFTPOWER_PROFILES_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"
    INPUT_ZWIFTRACINGAPP_PROFILES_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    
    zwiftpower_profiles_for_everybody = read_many_zwiftpower_profile_files_in_folder(None, INPUT_ZWIFTPOWER_PROFILES_FROM_DAVEK_DIRPATH)
    logger.info(f"Imported {len(zwiftpower_profiles_for_everybody)} zwiftpower profile files from : - \nDir : {INPUT_ZWIFTPOWER_PROFILES_FROM_DAVEK_DIRPATH}\n")

    zwiftpower_90daybest_graph_for_everybody = read_many_zwiftpower_graph_files_in_folder(None, INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH)
    logger.info(f"Imported {len(zwiftpower_90daybest_graph_for_everybody)} zwiftpower cp graphs from : - \nDir : {INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH}\n")

    zwiftracingapp_profiles_for_everybody = read_many_zwiftracingapp_profile_files_in_folder(None, INPUT_ZWIFTRACINGAPP_PROFILES_FROM_DAVEK_DIRPATH)
    logger.info(f"Imported {len(zwiftracingapp_profiles_for_everybody)} zwiftracingapp profile files from : - \nDir :{INPUT_ZWIFTRACINGAPP_PROFILES_FROM_DAVEK_DIRPATH}\n")

    # Step 1: Find keys in zwiftpower_profiles_for_everybody not in zwiftpower_90daybest_graph_for_everybody
    missing_keys_in_90daybest = [
        key for key in zwiftpower_profiles_for_everybody.keys()
        if key not in zwiftpower_90daybest_graph_for_everybody
    ]
    logger.info(f"Step 1: Found {len(missing_keys_in_90daybest)} keys missing in zwiftpower_90daybest_graph_for_everybody.")
    for key in missing_keys_in_90daybest:
        name = zwiftpower_profiles_for_everybody[key].zwift_name
        logger.info(f"Missing Key: {key}, Name: {name}")

    # # Step 2: Find keys in zwiftpower_profiles_for_everybody not in zwiftracingapp_profiles_for_everybody
    # missing_keys_in_racingapp = [
    #     key for key in zwiftpower_profiles_for_everybody.keys()
    #     if key not in zwiftracingapp_profiles_for_everybody
    # ]
    # logger.info(f"Step 2: Found {len(missing_keys_in_racingapp)} keys missing in zwiftracingapp_profiles_for_everybody.")
    # for key in missing_keys_in_racingapp:
    #     name = zwiftpower_profiles_for_everybody[key].zwift_name
    #     logger.info(f"Missing Key: {key}, Name: {name}")

    # # Step 3: Create a list of keys that exist in all three datasets
    # list_of_valid_keys = [
    #     key for key in zwiftpower_profiles_for_everybody.keys()
    #     if key in zwiftpower_90daybest_graph_for_everybody and key in zwiftracingapp_profiles_for_everybody
    # ]
    # logger.info(f"Step 3: Found {len(list_of_valid_keys)} valid keys that exist in all three datasets.")

    # # Step 4: Instantiate and initialize a Dict[str, OmnibusProfileDTO]
    # dict_of_valid_keys : Dict[str, OmnibusProfileDTO] = {}
    # for key in list_of_valid_keys:
    #     # Create a new OmnibusProfileDTO instance
    #     omnibus_profile = OmnibusProfileDTO()

    #     z = zwiftpower_profiles_for_everybody[key]
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
