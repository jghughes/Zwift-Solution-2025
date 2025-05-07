# load Dave's zsun_cp data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Any
import pandas as pd
from zsun_rider_item import ZsunRiderItem
from dataclasses import asdict
from scraped_zwift_data_repository import ScrapedZwiftDataRepository
from handy_utilities import *
from jgh_serialization import *
from jgh_read_write import write_pandas_dataframe_as_xlsx

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)


@dataclass()
class DummyItem:

    zwift_id                   : str   = ""    # Zwift ID of the rider
    name                       : str   = ""    # Name of the rider
    gender                     : str   = ""    # Gender of the rider
    age_years                  : float = 0.0   # Age of the rider in years
    curve_fit_ftp    : float = 0.0
    # o1_zwift_ftp                  : float = 0.0   # Originates in Zwift profile
    # o1_delta                 : float = 0.0   # Difference between Zwift FTP and JGH FTP
    # o1_percent               : float = 0.0   # Percentage difference between Zwift FTP and JGH FTP
    zwiftracingapp_zpFTP       : float = 0.0    #Originates in Zwiftracingapp profile
    delta                 : float = 0.0   # Difference between Zwift FTP and JGH FTP
    percent               : float = 0.0   # Percentage difference between Zwift FTP and JGH FTP
    r_squared_ftp_curve_fit : float = 0.0   # R-squared value for the curve fit of the FTP data
    zwift_zrs                  : float   = 0.0     # Zwift racing score
    zwift_cat                  : str   = ""    # A+, A, B, C, D, E
    zwiftracingapp_score        : float = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num      : int   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name     : str   = ""    # Copper, Silver, Gold etc

def main():
    
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    betel_IDs = get_betel_zwift_ids()

    repository : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()
    repository.populate_repository(betel_IDs, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 

    comparative_FTPs : list[DummyItem] = list()

    for zsunriderItem in repository.get_dict_of_ZsunRiderItem(betel_IDs).values():
        y_pred = round(zsunriderItem.get_n_second_watts(3600))
        y_actual = zsunriderItem.zwiftracingapp_zpFTP
        if y_pred == 0.0 or y_actual == 0 or zsunriderItem.zwift_zrs == 0 or zsunriderItem.zwiftracingapp_score == 0:
            continue
        delta = round(y_pred - y_actual)
        percent = abs(round(((y_pred - y_actual) * 100) / y_actual))
        logger.info(f"zpFTP/jgh: {round(y_actual)}/{round(y_pred)} delta = {delta} ({percent}%)")

        item = DummyItem(
            zwift_id=zsunriderItem.zwift_id,
            name=zsunriderItem.name,
            gender=zsunriderItem.gender,
            age_years=zsunriderItem.age_years,
            curve_fit_ftp=y_pred,
            zwiftracingapp_zpFTP= y_actual,
            delta=delta,
            percent=percent,
            r_squared_ftp_curve_fit = round(zsunriderItem.zsun_ftp_curve_fit_r_squared,2),
            zwift_zrs=zsunriderItem.zwift_zrs,
            zwift_cat=zsunriderItem.zwift_cat,
            zwiftracingapp_score=zsunriderItem.zwiftracingapp_score,
            zwiftracingapp_cat_num=zsunriderItem.zwiftracingapp_cat_num,
            zwiftracingapp_cat_name=zsunriderItem.zwiftracingapp_cat_name
        )
        comparative_FTPs.append(item)

    df = pd.DataFrame([asdict(item) for item in comparative_FTPs])

    write_pandas_dataframe_as_xlsx(df,  "comparative_FTP_analysis.xlsx", OUTPUT_DIRPATH)
    # write_json_file(JghSerialization.serialise(answer_dict), "betels_for_copying_manually_into_ZSUN01.json", OUTPUT_DIRPATH)
    logger.info(f"\n{len(comparative_FTPs)} line items saved to: {OUTPUT_DIRPATH}/comparative_FTP_analysis.xlsx\n")

    # jghbestpoweritems = list(repository.get_dict_of_JghBestPowerItem(betel_ids_found).values())

    # df = pd.DataFrame([asdict(ZsunBestPowerItem) for ZsunBestPowerItem in jghbestpoweritems])
    # write_pandas_dataframe_as_xlsx(df, "betels_best_power_items.xlsx", OUTPUT_DIRPATH)




if __name__ == "__main__":
    main()
