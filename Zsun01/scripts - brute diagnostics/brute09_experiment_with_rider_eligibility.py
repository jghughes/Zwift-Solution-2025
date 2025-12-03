"""
This tool is not used directly in the Brute production pipeline. I wrote
this tool to develop a dictionary of minimally-valid RiderBruteItem and
save it to Excel for eyeballing. In brute08 my focus was on exploring a
suitable value to cut-off poor curve fits. In this brute09, I couldn't
care less about the quality of curve fits; instead I am concerned about
filtering and selecting riders who are deemed to be recently active
racers regardless of their curve fits.

I went to a lot of trouble to write methods in the
RepositoryOfRiders that return unions/intersections as subsets
of power data from Zwift, ZwiftPower, and ZwiftRacingApp profiles
respectively in order to discover and fine tune how many riders are or
are not common to any two or three of them and to get to the bottom of
choosing only currently active racers with a valid zwift racing score
and velo racing score who deserve to be in the JSON database for Brute
riders. One of the metrics I eyeball as a matter of curiosity in the
output is jgh_TTT_pull_curve_fit_r_squared to monitor the fidelity of
curve fits in the pull zone. Some are much better than others, but I
don't filter out any of them, as I want to see the full range of curve
fits in Excel and their r-squared values. In the April 2025 dataset,
pull r-squared values for active racers range from 0.997 at best to
0.673 at worst. In the July 2025 dataset, the comparable values are
0.994 at best and 0.528 at worst.

In the April 2025 dataset, there were 1,514 riders in the club, and 304
actively racing riders. The comparable figures for July 2025 are 1,552
riders in the club and 264 actively racing riders.

This tool loads myriad files from Zwift, ZwiftPower, and ZwiftRacingApp
obtained by DaveK. It aggregates, models, and exports comprehensive
rider data for all club members using the multiple data sources and
power curve models.

The script performs the following steps:
- Configures logging for the application.
- Loads Zwift, ZwiftPower, and ZwiftRacingApp profiles, as well as best
  power data, using a unified data repository.
- Identifies the set of riders with complete and valid data across all
  sources.
- Retrieves and applies precomputed power curve fitting results for
  each rider.
- Constructs a unified rider data object (RiderBruteItem) for each
  member, combining demographic, performance, and modeled metrics.
- Exports the full set of rider profiles to Excel for further analysis.
- Filters the dataset to include only recently active riders (based on
  racing score and velo category), and exports this subset to a
  separate Excel file.

This tool demonstrates large-scale data integration, model application,
and dataset preparation for club-level cycling analytics and reporting.
Note the use of Pandas for data manipulation and export to Excel, as
well as NumPy for numerical operations related to power curve modeling.
"""
import os
from dataclasses import asdict
from pathlib import Path
# from typing import Any

import numpy as np, pandas as pd

from jgh_number import safe_divide
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_power_curve_fit_models import decay_model_numpy
from jgh_read_write import write_excel_file
from jgh_string import cleanup_name_string
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_BRUTE_DTO_JSON_DICT, DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_RUBBISH_SCRATCHPAD 
from repository_of_riders import RepositoryOfRiders
from rider_brute_item import RiderBruteItem
# from zwiftpower_profile_item import ZwiftPowerProfileItem

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING
# from paceline_computation_types import CurveFittingResultItem


def run_experiments_on_determinants_of_rider_eligibility():

    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_ZWIFT_FILES), Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), Path(DIRPATH_ZWIFTRACINGAPP_FILES),   Path(DIRPATH_RUBBISH_SCRATCHPAD)])
    except Exception as err:
        print(err)
        return
    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_BRUTE_DTO_JSON_DICT, output_filename01, output_filename02, output_filename03,])
    except Exception as err:
        print(err)
        return


    repository : RepositoryOfRiders = RepositoryOfRiders()
    repository.populate_repository(None, DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES) 

    eligible_IDs = repository._create_union_of_sets_filtered_by_membership_as_list("y","y_or_n","y")

    print(f"Using all {len(eligible_IDs)} eligible IDs from repository.")

    dict_of_zwiftItem = repository.get_dict_of_ZwiftItem_by_ids(eligible_IDs)
    dict_of_ZwiftRacingAppItem = repository.get_dict_of_ZwiftRacingAppItem_by_ids(eligible_IDs)
    # dict_of_ZwiftPowerProfileItem = repository.get_dict_of_ZwiftPowerProfileItem_by_ids(eligible_IDs)
    dict_of_flattenedZwiftPower90dayWatts = repository.get_dict_of_ZwiftPower90dayWattsItem_by_ids(eligible_IDs)
    dict_of_curve_fits = repository._compute_dict_of_selected_CurveFittingResultItem(eligible_IDs)

    print(f"Imported {len(dict_of_zwiftItem)} zwift profiles from : - \nDir : {DIRPATH_ZWIFT_FILES}\n")
    print(f"Imported {len(dict_of_ZwiftRacingAppItem)} racingapp profiles from : - \nDir :{DIRPATH_ZWIFTRACINGAPP_FILES}\n")
    # print(f"Imported {len(dict_of_ZwiftPowerProfileItem)} zwiftpower profiles from : - \nDir : {DIRPATH_ZWIFTPOWER_PROFILE_PAGE}\n")
    print(f"Imported {len(dict_of_flattenedZwiftPower90dayWatts)} zwiftpower 90-day best graphs from : - \nDir : {DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES}\n")

    #step 1: print a spreadsheet of all riders in dict_of_zwiftItem
    zwift_items_list = [asdict(item) for item in dict_of_zwiftItem.values()]
    zwift_items_df = pd.DataFrame(zwift_items_list)
    zwift_items_output_path = os.path.join(DIRPATH_RUBBISH_SCRATCHPAD, "all_zwift_items.xlsx")
    zwift_items_df.to_excel(zwift_items_output_path, index=False, engine="openpyxl")
    print(f"Saved spreadsheet of {len(dict_of_zwiftItem)} records in dict_of_zwiftItem to:\n{zwift_items_output_path}\n")

    # step 2: print a spreadsheet of all riders in the intersection of dict_of_zwiftItem and dict_of_flattenedZwiftPower90dayWatts
    intersection_ids = set(dict_of_zwiftItem.keys()) & set(dict_of_flattenedZwiftPower90dayWatts.keys())
    intersected_zwift_items = [asdict(dict_of_zwiftItem[zwift_id]) for zwift_id in intersection_ids]
    intersected_zwift_items_df = pd.DataFrame(intersected_zwift_items)
    intersected_output_path = os.path.join(DIRPATH_RUBBISH_SCRATCHPAD, "zwift_items_intersection_90daywatts.xlsx")
    intersected_zwift_items_df.to_excel(intersected_output_path, index=False, engine="openpyxl")
    print(f"Saved spreadsheet of {len(intersected_zwift_items)} records in intersection (dict_of_zwiftItem/dict_of_flattenedZwiftPower90dayWatts) to:\n{intersected_output_path}\n")

    # step 3: print a spreadsheet of all riders in the intersection of dict_of_zwiftItem, dict_of_flattenedZwiftPower90dayWatts, and dict_of_ZwiftRacingAppItem
    intersection_ids_3way = (
        set(dict_of_zwiftItem.keys())
        & set(dict_of_flattenedZwiftPower90dayWatts.keys())
        & set(dict_of_ZwiftRacingAppItem.keys())
    )
    intersected_zwift_items_3way = [asdict(dict_of_zwiftItem[zwift_id]) for zwift_id in intersection_ids_3way]
    intersected_zwift_items_3way_df = pd.DataFrame(intersected_zwift_items_3way)
    intersected_output_path_3way = os.path.join(DIRPATH_RUBBISH_SCRATCHPAD, "zwift_items_intersection_90daywatts_racingapp.xlsx")
    intersected_zwift_items_3way_df.to_excel(intersected_output_path_3way, index=False, engine="openpyxl")
    print(f"Saved spreadsheet of {len(intersected_zwift_items_3way)} records in intersection (dict_of_zwiftItem/dict_of_flattenedZwiftPower90dayWatts/dict_of_ZwiftRacingAppItem) to:\n{intersected_output_path_3way}\n")

    # step 4: print a spreadsheet of all riders in the intersection of dict_of_zwiftItem, dict_of_flattenedZwiftPower90dayWatts, dict_of_ZwiftRacingAppItem, and dict_of_curve_fits
    intersection_ids_4way = (
        set(dict_of_zwiftItem.keys())
        & set(dict_of_flattenedZwiftPower90dayWatts.keys())
        & set(dict_of_ZwiftRacingAppItem.keys())
        & set(dict_of_curve_fits.keys())
    )
    intersected_zwift_items_4way = [asdict(dict_of_zwiftItem[zwift_id]) for zwift_id in intersection_ids_4way]
    intersected_zwift_items_4way_df = pd.DataFrame(intersected_zwift_items_4way)
    intersected_output_path_4way = os.path.join(DIRPATH_RUBBISH_SCRATCHPAD, "zwift_items_intersection_90daywatts_racingapp_curvefits.xlsx")
    intersected_zwift_items_4way_df.to_excel(intersected_output_path_4way, index=False, engine="openpyxl")
    print(f"Saved spreadsheet of {len(intersected_zwift_items_4way)} records in intersection (dict_of_zwiftItem ? dict_of_flattenedZwiftPower90dayWatts ? dict_of_ZwiftRacingAppItem ? dict_of_curve_fits) to:\n{intersected_output_path_4way}\n")


    # step 5: make a list of the zwift_id of all riders in the intersection of dict_of_zwiftItem, dict_of_flattenedZwiftPower90dayWatts, dict_of_ZwiftRacingAppItem, and dict_of_curve_fits
    zwift_id_intersection_list = list(
        set(dict_of_zwiftItem.keys())
        & set(dict_of_flattenedZwiftPower90dayWatts.keys())
        & set(dict_of_ZwiftRacingAppItem.keys())
        & set(dict_of_curve_fits.keys())
    )

    #step 6: make a list from Step 5 - but only those with successful curve fits. save to Excel
    answer_dict : dict[str, RiderBruteItem] = dict[str, RiderBruteItem]()

    for key in zwift_id_intersection_list:
        zwiftItem = dict_of_zwiftItem[key]
        racingapp = dict_of_ZwiftRacingAppItem[key]
        jgh_curve_fit = dict_of_curve_fits[key]

        # we have only about 80 zwiftpowwerprofile files, DaveK doesn't fetch them all.
        # in any case, we don't need them for this experiment. we only use it for populating
        # zwiftpowerprofileItem.zftp_from_somewhere
        # if key not in dict_of_ZwiftPowerProfileItem:
        #     zwiftpowerprofileItem = ZwiftPowerProfileItem()
        # else:
        #     zwiftpowerprofileItem = dict_of_ZwiftPowerProfileItem[key]

        name = dict_of_ZwiftRacingAppItem[key].full_name or f"{zwiftItem.first_name} {zwiftItem.last_name}"

        jgh_curve_fit = dict_of_curve_fits[key]
        p60min = decay_model_numpy(np.array([3_600]), jgh_curve_fit.sixty_min_curve_coefficient, jgh_curve_fit.sixty_min_curve_exponent)
        one_hour_watts =  p60min[0]

        answer = RiderBruteItem(
        	zwift_id                         = zwiftItem.zwift_id,
        	name                             = cleanup_name_string(name),
            zwift_country_code3              = zwiftItem.country_code3,
        	weight_kg                        = round((safe_divide(zwiftItem.weight_grams, 1_000.0)), 1),
        	height_cm                        = round(safe_divide(zwiftItem.height_mm, 10.0 )),
        	gender                           = "m" if zwiftItem.is_male else "f",
        	age_years                        = zwiftItem.age_years,
        	age_group                        = racingapp.age_group,
        	zwift_FTP_watts                  = round(zwiftItem.ftp_on_zwift),
        	# zwiftpower_zFTP_watts            = round(zwiftpowerprofileItem.zftp_from_somewhere),
        	velo_zwiftpower_zFTP_watts      = round(racingapp.zp_FTP),
        	jgh_60_min_watts                 = round(one_hour_watts),
        	zwift_racing_score               = round(zwiftItem.competition_metrics.zwift_racing_score),
        	zwift_cat_open                   = zwiftItem.competition_metrics.zwift_category_open,
            zwift_cat_women                 = zwiftItem.competition_metrics.zwift_category_women,
        	velo_rating_30_days              = round(racingapp.raceitem.racing_score_max30_obj.velo_rating),
        	velo_cat_num_30_days             = racingapp.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_num,
        	velo_cat_name_30_days            = racingapp.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_name,
        	jgh_60_min_curve_coefficient     = jgh_curve_fit.sixty_min_curve_coefficient,
        	jgh_60_min_curve_exponent       = jgh_curve_fit.sixty_min_curve_exponent,
        	jgh_TTT_pull_curve_coefficient   = jgh_curve_fit.TTT_pull_curve_coefficient,
        	jgh_TTT_pull_curve_exponent      = jgh_curve_fit.TTT_pull_curve_exponent,
        	jgh_TTT_pull_curve_fit_r_squared = jgh_curve_fit.TTT_pull_curve_r_squared,
        	jgh_when_curves_fitted           = jgh_curve_fit.when_curves_fitted,
        )
        answer_dict[key] = answer

    riders = answer_dict.values()

    print(f"Trimmed the list to exclude failed curve fits: {len(riders)} riders.")

    df = pd.DataFrame([asdict(rider) for rider in riders])
    write_excel_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename02, df)
    print(f"\nSubset saved to:  {DIRPATH_RUBBISH_SCRATCHPAD + output_filename02}")

    # Step 7: Remove items where both zwift_racing_score and velo rating is zero (last 30_days)

    filtered_riders: list[RiderBruteItem] = [
        rider for rider in riders
        if rider.zwift_racing_score != 0 or rider.velo_rating_30_days != 0
    ]

    df = pd.DataFrame([asdict(rider) for rider in filtered_riders])
    write_excel_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename03, df)
    print(f"Trimmed the final list to exclude those who don't yet have a zwift_racing_score and/or velo rating score: {len(filtered_riders)} riders\nSaved to:  {DIRPATH_RUBBISH_SCRATCHPAD + output_filename03}")

    #Step 9: write to excel the riders who got excluded in step 7
    excluded_riders: list[RiderBruteItem] = [
        rider for rider in riders
        if rider not in filtered_riders
    ]

    excluded_output_filename = "riders_excluded_due_to_missing_racing_or_velo_scores.xlsx"
    df_excluded = pd.DataFrame([asdict(rider) for rider in excluded_riders])
    write_excel_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), excluded_output_filename, df_excluded)
    print(f"Saved excluded riders to: {DIRPATH_RUBBISH_SCRATCHPAD + excluded_output_filename} ({len(excluded_riders)} riders)")


if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        output_filename01 = "candidate_zwift_profiles.xlsx"
        output_filename02 = "riders_with_successful_curvefits.xlsx"
        output_filename03 = "riders_with_successful_curvefits_and_racing_scores_on_the_board.xlsx"
        run_experiments_on_determinants_of_rider_eligibility()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

    except AlertMessageError as alert_err:
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )
        print(f"{alert_err.message}\n")

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")