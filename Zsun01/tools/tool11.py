# load Dave's jgh_cp data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Any
import pandas as pd
from zsun_rider_item import ZsunRiderItem
from dataclasses import asdict
from scraped_zwift_data_repository import ScrapedZwiftDataRepository
from jgh_sanitise_string import cleanup_name_string
from handy_utilities import *
from jgh_serialization import *
from jgh_read_write import write_json_file, write_pandas_dataframe_as_xlsx

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

def main():
    
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"


    repository : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()

    repository.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 

    answer_dict = repository.get_dict_of_ZsunRiderItem(None)
    comparative_FTPs : list[tuple[float, float]] = list()

    for zsunriderItem in answer_dict.values():
        y_actual = zsunriderItem.zwiftracingapp_zpFTP
        y_pred = zsunriderItem.get_ftp_60_minute_watts()
        if y_actual == 0.0 or y_pred == 0:
            continue
        logger.info(f"zpFTP: {round(y_actual)} numpy: {round(y_pred)}")
        comparative_FTPs.append((y_actual, y_pred))






    # df = pd.DataFrame([asdict(betel) for betel in answer_dict.values()])

    # write_pandas_dataframe_as_xlsx(df,  "betels_for_copying_manually_into_ZSUN01.xlsx", OUTPUT_DIRPATH)
    # write_json_file(JghSerialization.serialise(answer_dict), "betels_for_copying_manually_into_ZSUN01.json", OUTPUT_DIRPATH)
    # logger.info(f"{len(answer_dict)} Betels saved to: {OUTPUT_DIRPATH} + betels_for_copying_manually_into_ZSUN01..")

    # jghbestpoweritems = list(repository.get_dict_of_JghBestPowerItem(betel_ids_found).values())

    # df = pd.DataFrame([asdict(jghbestpoweritem) for jghbestpoweritem in jghbestpoweritems])
    # write_pandas_dataframe_as_xlsx(df, "betels_best_power_items.xlsx", OUTPUT_DIRPATH)




if __name__ == "__main__":
    main()
