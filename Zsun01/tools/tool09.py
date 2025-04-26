# load Dave's critical_power data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!

from handy_utilities import write_dict_of_cpdata, read_many_zwiftpower_graph_files_in_folder, get_betel_zwift_ids, get_betel, read_many_zwiftpower_profile_files_in_folder, read_many_zwiftracingapp_files_in_folder
import critical_power as cp
from zwiftrider_related_items import ZsunRiderItem
from datetime import datetime
from dataclasses import dataclass
from dataclasses import dataclass,  asdict

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

    INPUT_ZWIFTRACINGAPP_PROFILES_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    INPUT_ZWIFTPOWER_PROFILES_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    # raw_zwiftracingapp_profiles = read_many_zwiftracingapp_files_in_folder(None, INPUT_ZWIFTRACINGAPP_PROFILES_FROM_DAVEK_DIRPATH)
    raw_profiles_for_everybody = read_many_zwiftpower_profile_files_in_folder(None, INPUT_ZWIFTPOWER_PROFILES_FROM_DAVEK_DIRPATH)
    # raw_cp_dict_for_everybody = read_many_zwiftpower_graph_files_in_folder(None, INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH)


    # logger.info(f"Imported {len(raw_zwiftracingapp_profiles)} zwiftracingapp profile files from:- \nDir : {INPUT_ZWIFTRACINGAPP_PROFILES_FROM_DAVEK_DIRPATH}\n")
    logger.info(f"Imported {len(raw_profiles_for_everybody)} zwiftpower profile files from:- \nDir : {INPUT_ZWIFTPOWER_PROFILES_FROM_DAVEK_DIRPATH}\n")
    # logger.info(f"Imported {len(raw_cp_dict_for_everybody)} ZwiftPower graphs from:- \nDir : {INPUT_ZWIFTPOWER_GRAPHS_FROM_DAVEK_DIRPATH}\n")


if __name__ == "__main__":
    main()



