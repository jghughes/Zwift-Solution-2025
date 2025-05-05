# load Dave's jgh_cp data for everyone in the club, load all their names form somewhere else. do the modelling with the all the models. save all the data to a file I can load into excel and also save in the project data file. Then I am ready to move on!
from typing import Any
import pandas as pd
from zsun_rider_item import ZsunRiderItem
from dataclasses import asdict
from scraped_zwift_data_repository import ScrapedZwiftDataRepository
from jgh_sanitise_string import cleanup_name_string
from handy_utilities import get_betel_zwift_ids
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


    rep : ScrapedZwiftDataRepository = ScrapedZwiftDataRepository()

    rep.populate_repository(None, ZWIFT_PROFILES_DIRPATH, ZWIFTRACINGAPP_PROFILES_DIRPATH, ZWIFTPOWER_PROFILES_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 

    logger.info(f"Imported {len(rep.dict_of_zwiftprofileitem)} zwift profiles from : - \nDir : {ZWIFT_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftracingappprofileitem)} zwiftracingapp profiles from : - \nDir :{ZWIFTRACINGAPP_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_zwiftpowerprofileitem)} zwiftpower profiles from : - \nDir : {ZWIFTPOWER_PROFILES_DIRPATH}\n")
    logger.info(f"Imported {len(rep.dict_of_jghbestpoweritem)} zwiftpower cp graphs from : - \nDir : {ZWIFTPOWER_GRAPHS_DIRPATH}\n")


    zwift_ids = rep.get_list_of_filtered_intersections_of_sets("y","y_or_n","y_or_n","y") 

    betel_IDs = get_betel_zwift_ids()

    # determine which betel ids not found in repository
    betel_ids_not_found = [betel_id for betel_id in betel_IDs if betel_id not in zwift_ids]
    betel_ids_found = list(set(betel_IDs) - set(betel_ids_not_found))
    logger.info(f"Betel IDs not found in repository: {len(betel_ids_not_found)}\n{betel_ids_not_found}\n")
    logger.info(f"Betel IDs found in repository:{len(betel_ids_found)}\n {betel_ids_found}\n")

    zwift_profiles = list(rep.get_dict_of_ZwiftProfileItem(betel_ids_found).values())

    profiles_as_attr_dicts : list[dict[str, Any]]= [asdict(profile) for profile in zwift_profiles]
    df = pd.DataFrame(profiles_as_attr_dicts)
    output_file_name = "temp_candidate_betels.xlsx"
    output_file_path = OUTPUT_DIRPATH + output_file_name
    df.to_excel(output_file_path, index=False, engine="openpyxl")
    logger.info(f"Saved {len(zwift_profiles)} candidate betels to: {output_file_path}")

    answer_dict : dict[str, ZsunRiderItem] = dict[str, ZsunRiderItem]()

    curve_parameters = rep.get_dict_of_CurveFittingResults(betel_ids_found)
    
    for key in rep.get_dict_of_ZwiftProfileItem(betel_ids_found):
        item = rep.dict_of_zwiftprofileitem[key]
        # if item.zftp < 50 or item.competitionMetrics.racingScore < 80:            
        #     logger.warning(f"Skipped: low zFTP or poor ZRS: {item.first_name} {item.last_name}")
        #     continue
        # jgh_best_power = rep.dict_of_jghbestpoweritem[key]
        # if jgh_best_power.cp_10 == 0:
        #     logger.warning(f"Skipped: no 90-day-best curve: {item.first_name} {item.last_name}")
        #     continue

        velo = rep.dict_of_zwiftracingappprofileitem[key]
        
        zp = rep.dict_of_zwiftpowerprofileitem[key]

        if key in rep.dict_of_zwiftracingappprofileitem:
            name = rep.dict_of_zwiftracingappprofileitem[key].fullname or f"{item.first_name} {item.last_name}"
        else:
            name = f"{item.first_name} {item.last_name}"

        item = ZsunRiderItem(
            zwift_id                   = item.zwift_id,
            name                       = cleanup_name_string(name),
            weight_kg                  = (item.weight_grams or 0.0) / 1_000.0,
            height_cm                  = (item.height_mm or 0.0) / 10.0,
            gender                     = "m" if item.male else "f",
            age_years                  = item.age_years,
            agegroup                   = zp.age_group,
            zwift_zftp                 = item.zftp,
            zwift_zrs                  = item.competitionMetrics.racingScore,
            zwift_cat                  = item.competitionMetrics.category,
            velo_score                 = velo.raceitem.max90.rating,
            velo_cat_num               = velo.raceitem.max90.mixed.number,
            velo_cat_name              = velo.raceitem.max90.mixed.category,
            velo_cp                    = velo.poweritem.CP,
            velo_awc                   = velo.poweritem.AWC,
            jgh_pull_adjustment_watts  = 0.0,
            jgh_cp                     = 0.0,
            jgh_w_prime                = 0.0,
            jgh_ftp_curve_coefficient  = 0.0,
            jgh_ftp_curve_exponent     = 0.0,
            jgh_pull_curve_coefficient = 0.0,
            jgh_pull_curve_exponent    = 0.0,
            jgh_when_curves_fitted     = ""
        )

        answer_dict[key] = item


    zsunriders = answer_dict.values()

    logger.info(f"Created a minimally valid subset of zsun zsunriders:  {len(answer_dict)}")

    df = pd.DataFrame([asdict(rider) for rider in zsunriders])

    # Step 8: Save the DataFrame to an Excel file
    OUTPUT_DIR_PATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"

    file_name = "minimally_valid_zsun_riders.xlsx"
    df.to_excel(OUTPUT_DIR_PATH + file_name, index=True)
    logger.info(f"Minimally valid subset of zsun zsunriders: {len(answer_dict)}\nSaved to:  {OUTPUT_DIR_PATH + file_name}")

    # Remove items where zwift_zrs is 0 or vvelo_cat_name is an empty string
    answer_dict = {
        key: value
        for key, value in answer_dict.items()
        if value.zwift_zrs != 0 and value.velo_cat_name != ''
    }

    zsunriders = answer_dict.values()
    df = pd.DataFrame([asdict(rider) for rider in zsunriders])

    file_name = "zsun_riders_recently_active.xlsx"
    df.to_excel(OUTPUT_DIR_PATH + file_name, index=True)
    logger.info(f"Active subset of zsun racers: {len(answer_dict)}\nSaved to:  {OUTPUT_DIR_PATH + file_name}")


if __name__ == "__main__":
    main()
