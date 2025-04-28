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
    # get all the data
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    betel_zwift_ids = get_betel_zwift_ids()

    repository : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()

    repository.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 


    zwift_profiles = repository.dict_of_zwift_profileDTO
    zwiftracingapp_profiles = repository.dict_of_zwiftracingapp_profileDTO
    zwiftpower_profiles = repository.dict_of_zwiftpower_profileDTO
    zwiftpower_90daybest_cp = repository.dict_of_zwiftpower_90daybest_graph_item

    logger.info(f"Imported {len(zwift_profiles)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(zwiftracingapp_profiles)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(zwiftpower_profiles)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(zwiftpower_90daybest_cp)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")

    # # check that the betel keys are in the zwiftpower_profiles dict

    # missing_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key not in zwiftpower_profiles
    #     ]
    # logger.info(f"Step a: Found {len(missing_betel_keys)} Betel keys missing in zwiftpower_profiles.")

    # found_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key in zwiftpower_profiles
    #     ]
    # logger.info(f"Step a: Found {len(found_betel_keys)} Betel keys in zwiftpower_profiles.")
    # for key in found_betel_keys:
    #     name = zwiftpower_profiles[key].zwift_name
    #     logger.info(f"Found Key: {key}, Name: {name}")


    # # check that the betel keys are in the zwiftpower_90daybest_cp dict

    # missing_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key not in zwiftpower_90daybest_cp
    #     ]
    # logger.info(f"Step b: Found {len(missing_betel_keys)} Betel keys missing in zwiftpower_90daybest_cp.")

    # found_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key in zwiftpower_90daybest_cp
    #     ]
    # logger.info(f"Step b: Found {len(found_betel_keys)} Betel keys in zwiftpower_90daybest_cp.")
    # for key in found_betel_keys:
    #     name = zwiftpower_profiles[key].zwift_name
    #     logger.info(f"Found Key: {key}, Name: {name}")


    # # check that the betel keys are in the zwiftracingapp_profiles dict

    # missing_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key not in zwiftracingapp_profiles
    #     ]
    # logger.info(f"Step c: Found {len(missing_betel_keys)} Betel keys missing in zwiftracingapp_profiles.")

    # found_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key in zwiftracingapp_profiles
    #     ]
    # logger.info(f"Step c: Found {len(found_betel_keys)} Betel keys in zwiftracingapp_profiles.")
    # for key in found_betel_keys:
    #     name = zwiftracingapp_profiles[key].fullname
    #     logger.info(f"Found Key: {key}, Name: {name}")


    # # Step 1: Find keys in zwiftpower_profiles not in zwiftpower_90daybest_cp
    # missing_keys_in_90daybest = [
    #     key for key in zwiftpower_profiles.keys()
    #     if key not in zwiftpower_90daybest_cp
    # ]
    # logger.info(f"Step 1: Found {len(missing_keys_in_90daybest)} keys missing in zwiftpower_90daybest_cp.")
    # for key in missing_keys_in_90daybest:
    #     name = zwiftpower_profiles[key].zwift_name
    #     logger.info(f"Missing Key: {key}, Name: {name}")

    # # Step 2: Find keys in zwiftpower_profiles not in zwiftracingapp_profiles
    # missing_keys_in_racingapp = [
    #     key for key in zwiftpower_profiles.keys()
    #     if key not in zwiftracingapp_profiles
    # ]
    # logger.info(f"Step 2: Found {len(missing_keys_in_racingapp)} keys missing in zwiftracingapp_profiles.")
    # for key in missing_keys_in_racingapp:
    #     name = zwiftpower_profiles[key].zwift_name
    #     logger.info(f"Missing Key: {key}, Name: {name}")

    # # Step 3: Create a list of keys that exist in all three datasets
    # list_of_valid_keys = [
    #     key for key in zwiftpower_profiles.keys()
    #     if key in zwiftpower_90daybest_cp and key in zwiftracingapp_profiles
    # ]
    # logger.info(f"Step 3: Found {len(list_of_valid_keys)} valid keys that exist in all three datasets.")
    # for key in list_of_valid_keys:
    #     name = zwiftpower_profiles[key].zwift_name
    #     logger.info(f"Found Key: {key}, Name: {name}")


    #  # Step 4: Create a new dict of valid keys and zwiftpower_profiles, but the items in the dict must be sorted by name 
    # sorted_list_of_valid_keys = sorted(list_of_valid_keys, key=lambda k: zwiftpower_profiles[k].zwift_name)

    # # log the dict by key and name
    # for key in sorted_list_of_valid_keys:
    #     name = zwiftpower_profiles[key].zwift_name
    #     logger.info(f"Sorted Key: {key}, Name: {name}")


    #  # check that the betel keys are in the zwiftracingapp_profiles dict

    # missing_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key not in sorted_list_of_valid_keys
    #     ]
    # logger.info(f"Step c: Found {len(missing_betel_keys)} Betel keys missing in sorted_list_of_valid_keys.")

    # found_betel_keys = [
    #     key for key in betel_zwift_ids
    #     if key in sorted_list_of_valid_keys
    #     ]
    # logger.info(f"Step c: Found {len(found_betel_keys)} Betel keys in sorted_list_of_valid_keys.")
    # for key in found_betel_keys:
    #     name = zwiftracingapp_profiles[key].fullname
    #     logger.info(f"Found Key: {key}, Name: {name}")













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
