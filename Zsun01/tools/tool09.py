# load Dave's jgh_cp data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Any
import pandas as pd
from zsun_rider_item import ZsunRiderItem
from dataclasses import asdict
from scraped_zwift_data_repository import ScrapedZwiftDataRepository
from jgh_sanitise_string import cleanup_name_string

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO


# @dataclass
# class CurveFittingResult:
#     zwiftid: str
#     name: str
#     ftp_watts: float
#     pull_watts: float
#     pull_percent : float
#     critical_power_watts: float
#     anaerobic_work_capacity_kJ: float
#     r_squared_pull: float
#     r_squared_ftp: float

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
    logger.info(f"Imported {len(rep.dict_of_jghbestpoweritem)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")


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

    dict_of_zsun_riders : dict[str, ZsunRiderItem] = dict[str, ZsunRiderItem]()
    
    for key in rep.dict_of_zwiftprofileitem:
        z = rep.dict_of_zwiftprofileitem[key]
        # if z.zftp < 50 or z.competitionMetrics.racingScore < 80:            
        #     logger.warning(f"Skipped: low zFTP or poor ZRS: {z.first_name} {z.last_name}")
        #     continue
        # jgh_best_power = rep.dict_of_jghbestpoweritem[key]
        # if jgh_best_power.cp_10 == 0:
        #     logger.warning(f"Skipped: no 90-day-best curve: {z.first_name} {z.last_name}")
        #     continue

        v = rep.dict_of_zwiftracingappprofileitem[key]
        
        zp = rep.dict_of_zwiftpowerprofileitem[key]

        if key in rep.dict_of_zwiftracingappprofileitem:
            name = rep.dict_of_zwiftracingappprofileitem[key].fullname or f"{z.first_name} {z.last_name}"
        else:
            name = f"{z.first_name} {z.last_name}"

        item = ZsunRiderItem(
            zwift_id                   = z.zwift_id,
            name                       = cleanup_name_string(name),
            weight_kg                  = (z.weight_grams or 0.0) / 1_000.0,
            height_cm                  = (z.height_mm or 0.0) / 10.0,
            gender                     = "m" if z.male else "f",
            age_years                  = z.age_years,
            agegroup                   = zp.age_group,
            zwift_zftp                 = z.zftp,
            zwift_zrs                  = z.competitionMetrics.racingScore,
            zwift_cat                  = z.competitionMetrics.category,
            velo_score                 = v.raceitem.max90.rating,
            velo_cat_num               = v.raceitem.max90.mixed.number,
            velo_cat_name              = v.raceitem.max90.mixed.category,
            velo_cp                    = v.poweritem.CP,
            velo_awc                   = v.poweritem.AWC,
            jgh_pull_adjustment_watts  = 0.0,
            jgh_cp                     = 0.0,
            jgh_w_prime                = 0.0,
            jgh_ftp_curve_coefficient  = 0.0,
            jgh_ftp_curve_exponent     = 0.0,
            jgh_pull_curve_coefficient = 0.0,
            jgh_pull_curve_exponent    = 0.0,
            jgh_when_curves_fitted     = ""
        )

        dict_of_zsun_riders[key] = item


    riders = dict_of_zsun_riders.values()

    logger.info(f"Created a minimally valid subset of zsun riders:  {len(dict_of_zsun_riders)}")

    df = pd.DataFrame([asdict(rider) for rider in riders])

    # Step 8: Save the DataFrame to an Excel file
    OUTPUT_FILE_NAME = "minimally_valid_zsun_riders.xlsx"
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    df.to_excel(OUTPUT_DIR_PATH + OUTPUT_FILE_NAME, index=True)
    logger.info(f"Saved the DataFrame to:  {OUTPUT_DIR_PATH + OUTPUT_FILE_NAME}")



if __name__ == "__main__":
    main()
