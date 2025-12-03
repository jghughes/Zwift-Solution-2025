from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, TypeVar

import pandas as pd

from paceline_computation_types import CurveFittingResultItem
from critical_power import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model
from zwiftid_file_reader_sync import (
    read_zwiftdto_files_to_item_dict_sync,
    read_zwftracingappdto_files_to_item_dict_sync,
    # read_zwiftpowerprofiledto_files_to_item_dict_sync,
    read_zwiftpower90daywattsdto_files_to_item_dict_sync,
)
from jgh_formatting import get_current_utc_iso8601_timestamp
from jgh_number import safe_divide
from jgh_string import cleanup_name_string
from zwift_item import ZwiftItem
# from zwiftpower_profile_item import ZwiftPowerProfileItem
from zwiftracingapp_item import ZwiftRacingAppItem
from rider_brute_item import RiderBruteItem
from rider_stats_item import RiderStatsItem
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem


T = TypeVar("T")  # Generic type variable for the item type in the dict
@dataclass
class RepositoryOfRiders:

    _dict_of_ZwiftItem                  :   Dict[str, ZwiftItem] = field(default_factory=dict)
    # _dict_of_ZwiftPowerProfileItem      :   Dict[str, ZwiftPowerProfileItem] = field(default_factory=dict)
    _dict_of_ZwiftRacingAppItem         :   Dict[str, ZwiftRacingAppItem] = field(default_factory=dict)
    _dict_of_ZwiftPower90dayWattsItem   :   Dict[str, ZwiftPowerFlattened90dayWattsItem] = field(default_factory=dict)

    _eligible_IDs                       :  list[str] = field(default_factory=list)
    _computed_dict_of_curveFitItem      :  Dict[str, CurveFittingResultItem] = field(default_factory=dict)
    _computed_dict_of_riderBruteItem    :  Dict[str, RiderBruteItem] = field(default_factory=dict)
    _computed_dict_of_riderStatsItem    :  Dict[str, RiderStatsItem] = field(default_factory=dict)

    # Repository constants for DataFrame column names
    COL_ZWIFT_ID                  = "zwift_id"
    COL_IN_SAMPLE1                = "in_sample1"
    COL_IN_SAMPLE2                = "in_sample2"
    COL_IN_ZWIFT                  = "zwift"
    COL_IN_ZWIFTPOWER             = "zwiftpower"
    COL_IN_ZWIFTPOWER_WATTS_GRAPHS= "zwiftpower_90_day_watts"
    COL_IN_ZWIFTRACINGAPP         = "zwiftracingapp"

    def populate_repository(
        self,
        file_names: Optional[list[str]],
        zwift_dir_path: str,
        zwiftracingapp_dir_path: str,
        zwiftpower_90day_graph_watts_dir_path: str,
    )->bool:
        print(f"Repository to read raw data (sync) is populating itself. This will take more than a minute.")
        print(f"1. Reading hundreds of Zwift files on hard-drive.")
        self._dict_of_ZwiftItem = read_zwiftdto_files_to_item_dict_sync(Path(zwift_dir_path), file_names)
        print(f"2. Reading hundreds of ZwiftPower 90-day power watts files on hard-drive.")
        self._dict_of_ZwiftPower90dayWattsItem = read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(zwiftpower_90day_graph_watts_dir_path),file_names)
        print(f"3. Reading hundreds of ZwiftRacingApp files on hard-drive.")
        self._dict_of_ZwiftRacingAppItem = read_zwftracingappdto_files_to_item_dict_sync(Path(zwiftracingapp_dir_path),file_names)
        print(f"4. Doing curve fits for 90-day power watts files.")
        eligible_IDs = self._compute_intersection_of_mandatory_sets_as_list() 
        self._computed_dict_of_curveFitItem = self._compute_dict_of_selected_CurveFittingResultItem(eligible_IDs) #do first
        print(f"5. Doing rider brute items.")
        self._computed_dict_of_riderBruteItem = self._compute_dict_of_RiderBruteItem(eligible_IDs) # do second
        print(f"6. Doing rider stats items.")
        self._computed_dict_of_riderStatsItem = self._compute_dict_of_RiderStatsItem(eligible_IDs)# do third
        print(f"Repository successfully populated.")
   
        return True

    def get_zwiftIDs_of_all_RiderBruteItem(self) -> list[str]:
        """
        Returns a list of all Zwift IDs (keys) present in the _computed_dict_of_riderBruteItem,
        sorted by the RiderBruteItem.name property.

        Returns:
            list[str]: List of Zwift IDs for all riders in the computed dictionary, sorted by name.
        """
        sorted_items: list[tuple[str, RiderBruteItem]] = sorted(
            self._computed_dict_of_riderBruteItem.items(),
            key=lambda item: item[1].name
        )
        return [zwift_id for zwift_id, _ in sorted_items]

    def get_dict_of_RiderBruteItem(self) -> Dict[str, RiderBruteItem]:
        return self._computed_dict_of_riderBruteItem

    def get_dict_of_RiderStatsItem(self) -> Dict[str, RiderStatsItem]:
        return self._computed_dict_of_riderStatsItem

    def get_dict_of_RiderBruteItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderBruteItem]:
        return self._get_dict_by_ids(self._computed_dict_of_riderBruteItem, zwift_ids)

    def get_dict_of_ZwiftItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftItem]:
        return self._get_dict_by_ids(self._dict_of_ZwiftItem, zwift_ids)

    # def get_dict_of_ZwiftPowerProfileItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftPowerProfileItem]:
    #     return self._get_dict_by_ids(self._dict_of_ZwiftPowerProfileItem, zwift_ids)

    def get_dict_of_ZwiftRacingAppItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftRacingAppItem]:
        return self._get_dict_by_ids(self._dict_of_ZwiftRacingAppItem, zwift_ids)

    def get_dict_of_ZwiftPower90dayWattsItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftPowerFlattened90dayWattsItem]:
        return self._get_dict_by_ids(self._dict_of_ZwiftPower90dayWattsItem, zwift_ids)

    def _get_dict_by_ids(self, source_dict: Dict[str, T], zwift_ids: Optional[list[str]]) -> Dict[str, T]:
        """
        Returns a dictionary containing only the items from `source_dict` whose keys are present in `zwift_ids`.

        If `zwift_ids` is None or empty, all items from `source_dict` are included.
        If a key in `zwift_ids` does not exist in `source_dict`, it is skipped.

        Args:
            source_dict (Dict[str, T]): The source dictionary to filter.
            zwift_ids (Optional[list[str]]): List of keys to include in the result. If None or empty, include all.

        Returns:
            Dict[str, T]: A dictionary containing only the requested items.
        """

        # If zwift_ids is None or empty, return a shallow copy of the entire source_dict.
        if not zwift_ids:
            return dict(source_dict)

        # Convert zwift_ids to a set for fast O(1) membership checks.
        zwift_id_set = set(zwift_ids)

        # Use dictionary comprehension for efficient filtering.
        # Only include keys that exist in source_dict.
        return {key: source_dict[key] for key in zwift_id_set if key in source_dict}

    def _compute_intersection_of_mandatory_sets_as_list(self) -> list[str]:
        """
        Returns a list of Zwift IDs present in all three main dictionaries:
        _dict_of_ZwiftItem, _dict_of_ZwiftRacingAppItem, and _dict_of_ZwiftPower90dayWattsItem.
        """
        intersection = list(
            set(self._dict_of_ZwiftItem.keys())
            & set(self._dict_of_ZwiftRacingAppItem.keys())
            & set(self._dict_of_ZwiftPower90dayWattsItem.keys())
        )
        print(f"Number of Zwift IDs in intersection of mandatory sets: {len(intersection)}")
        return intersection

        #HEAP IMPORTANT. THE MEAT AND POTATOES FUNCTION THAT PRODUCES THE FINAL OUTPUT DICTIONARY

    def _compute_dict_of_RiderBruteItem(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderBruteItem]:

        answer: Dict[str, RiderBruteItem] = {}

        if zwift_ids is None:
            zwift_ids = []

        # NB: by computing jgh_curve_dict first, we ensure that only riders with curve fits are included, this strips out many riders without sufficient/any data on zwiftpower (approx 150 of them)
        # jgh_curve_dict = self._computed_dict_of_curveFitItem

        print(f"Repository message: computing rider brute items for {len(zwift_ids)} candidates.")
 
        for key in self._computed_dict_of_curveFitItem:

            zwiftItem = self._dict_of_ZwiftItem.get(key)
            if zwiftItem is None:
                zwiftItem = ZwiftItem()

            zwiftracingappItem = self._dict_of_ZwiftRacingAppItem.get(key)
            if zwiftracingappItem is None:
                zwiftracingappItem = ZwiftRacingAppItem()

            jghcurveItem = self._computed_dict_of_curveFitItem.get(key)
            if jghcurveItem is None:
                jghcurveItem = CurveFittingResultItem()

            if key in self._dict_of_ZwiftRacingAppItem:
                name = self._dict_of_ZwiftRacingAppItem[key].full_name or f"{zwiftItem.first_name} {zwiftItem.last_name}"
            else:
                name = f"{zwiftItem.first_name} {zwiftItem.last_name}"

            zwiftItem = RiderBruteItem(
                zwift_id                          = zwiftItem.zwift_id,
                name                              = cleanup_name_string(name),
                weight_kg                         = round((zwiftItem.weight_grams or 0.0) / 1_000.0, 1),
                zwift_country_code3               = zwiftItem.country_code3,
                height_cm                         = round((zwiftItem.height_mm  or 0.0) / 10.0),
                gender                            = "m" if zwiftItem.is_male else "f",
                age_years                         = zwiftItem.age_years,
                age_group                         = zwiftracingappItem.age_group,
                zwift_FTP_watts                   = round(zwiftItem.ftp_on_zwift),
                velo_zwiftpower_zFTP_watts          = round(zwiftracingappItem.zp_FTP),
                jgh_60_min_watts                  = round(jghcurveItem.sixty_min_curve_coefficient),
                zwift_racing_score                 = round(zwiftItem.competition_metrics.zwift_racing_score),
                zwift_cat_open                     = zwiftItem.competition_metrics.zwift_category_open,
                zwift_cat_women                     = zwiftItem.competition_metrics.zwift_category_women,
                velo_rating_30_days                = round(zwiftracingappItem.raceitem.racing_score_max30_obj.velo_rating),
                velo_cat_num_30_days               = zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_num,
                velo_cat_name_30_days              = zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_name,
                jgh_60_min_curve_coefficient      = jghcurveItem.sixty_min_curve_coefficient,
                jgh_60_min_curve_exponent         = jghcurveItem.sixty_min_curve_exponent,
                jgh_TTT_pull_curve_coefficient    = jghcurveItem.TTT_pull_curve_coefficient,
                jgh_TTT_pull_curve_exponent       = jghcurveItem.TTT_pull_curve_exponent,
                jgh_TTT_pull_curve_fit_r_squared  = jghcurveItem.sixty_min_curve_r_squared,
                jgh_when_curves_fitted            = jghcurveItem.when_curves_fitted,
    )

            answer[key] = zwiftItem

        print (f"Repository message: completed computing brute items for {len(answer)} riders.")

        return answer

    def _compute_dict_of_RiderStatsItem(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderStatsItem]:

        preliminary_answer: Dict[str, RiderStatsItem] = {}
        answer: Dict[str, RiderStatsItem] = {}

        if zwift_ids is None:
            zwift_ids = []

        print(f"Repository message: computing rider stats items for {len(zwift_ids)} riders.")

 
        for key in zwift_ids:

            zwiftItem = self._dict_of_ZwiftItem.get(key)
            if zwiftItem is None:
                zwiftItem = ZwiftItem()

            zwiftracingappItem = self._dict_of_ZwiftRacingAppItem.get(key)
            if zwiftracingappItem is None:
                zwiftracingappItem = ZwiftRacingAppItem()

            jghcurveItem = self._computed_dict_of_curveFitItem.get(key)
            if jghcurveItem is None:
                jghcurveItem = CurveFittingResultItem()

            if key in self._dict_of_ZwiftRacingAppItem:
                name = self._dict_of_ZwiftRacingAppItem[key].full_name or f"{zwiftItem.first_name} {zwiftItem.last_name}"
            else:
                name = f"{zwiftItem.first_name} {zwiftItem.last_name}"

            riderStatsItem = RiderStatsItem(
                zwift_id=zwiftItem.zwift_id,
                name=cleanup_name_string(name),
                zwift_country_code3=zwiftItem.country_code3,
                age=zwiftItem.age_years,
                height_cm=round((zwiftItem.height_mm or 0.0) / 10.0),
                weight_kg=round((zwiftItem.weight_grams or 0.0) / 1_000.0, 1),
                gender_code="m" if zwiftItem.is_male else "f",
                cat_open=zwiftItem.competition_metrics.zwift_category_open,
                cat_women=zwiftItem.competition_metrics.zwift_category_women,
                zwift_racing_score=round(zwiftItem.competition_metrics.zwift_racing_score),
                zwift_ftp_w=round(zwiftItem.ftp_on_zwift),
                zwift_zftp_w=round(zwiftracingappItem.zp_FTP),
                zwift_zftp_wkg=0.0,  # No direct mapping, set to 0.0 or compute if possible
                zwift_cat_label="",  # se below
                velo_age_group=zwiftracingappItem.age_group,
                velo_cat_num_30_days=zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_num,
                velo_cat_name_30_days=zwiftracingappItem.raceitem.racing_score_max30_obj.mixed_things_obj.velo_cat_name,
                velo_rating_30_days=round(zwiftracingappItem.raceitem.racing_score_max30_obj.velo_rating),
                velo_cat_label="",  # see below
                wkg_05sec=0.0, # all the power data points below are set from _dict_of_ZwiftPower90dayWattsItem
                wkg_15sec=0.0,
                wkg_30sec=0.0,
                wkg_01min=0.0,
                wkg_02min=0.0,
                wkg_03min=0.0,
                wkg_05min=0.0,
                wkg_10min=0.0,
                wkg_12min=0.0,
                wkg_15min=0.0,
                wkg_20min=0.0,
                wkg_30min=0.0,
                wkg_40min=0.0,
                wkg_60min_curvefit=round(jghcurveItem.sixty_min_curve_coefficient, 2),
                w_05sec=0.0,
                w_15sec=0.0,
                w_30sec=0.0,
                w_01min=0.0,
                w_02min=0.0,
                w_03min=0.0,
                w_05min=0.0,
                w_10min=0.0,
                w_12min=0.0,
                w_15min=0.0,
                w_20min=0.0,
                w_30min=0.0,
                w_40min=0.0,
                w_60min_curvefit=round(jghcurveItem.sixty_min_curve_coefficient, 2),
                timestamp=get_current_utc_iso8601_timestamp(),
            )

            riderStatsItem.zwift_zftp_wkg = safe_divide(zwiftracingappItem.zp_FTP, riderStatsItem.weight_kg)

            if riderStatsItem.cat_open == "":
                riderStatsItem.cat_open = "?"  
            if riderStatsItem.cat_women == "":
                if riderStatsItem.gender_code == "m":
                    riderStatsItem.cat_women = ""
                else:
                    riderStatsItem.cat_women = "?"
            if riderStatsItem.gender_code == "m":
                cat_combo = riderStatsItem.cat_open
            else:
                cat_combo = riderStatsItem.cat_open + "/" + riderStatsItem.cat_women

            if riderStatsItem.zwift_racing_score== 0:
                riderStatsItem.zwift_cat_label = f"{round(riderStatsItem.zwift_zftp_wkg,1)}wkg"
            else:
                riderStatsItem.zwift_cat_label = f"{round(riderStatsItem.zwift_zftp_wkg,1)}wkg  {riderStatsItem.zwift_racing_score}  {cat_combo}"

            if riderStatsItem.velo_rating_30_days ==0:
                riderStatsItem.velo_cat_label= ""
            else:
                riderStatsItem.velo_cat_label = f"{riderStatsItem.velo_rating_30_days}  {riderStatsItem.velo_cat_num_30_days}  {riderStatsItem.velo_cat_name_30_days}"

            preliminary_answer[key] = riderStatsItem

        for zwift_id, rider_stats_item in preliminary_answer.items():
            watts_90_day_item = self._dict_of_ZwiftPower90dayWattsItem.get(zwift_id)
            weight_kg = rider_stats_item.weight_kg
            if watts_90_day_item is not None:
                rider_stats_item = ZwiftPowerFlattened90dayWattsItem.populate_riderStatsItem_with_90dayWattsItem(
                    rider_stats_item, watts_90_day_item, weight_kg
                )
            answer[zwift_id] = rider_stats_item

        print (f"Repository message: completed computing rider stats items for {len(answer)} riders.")

        return answer

    def _compute_dict_of_selected_CurveFittingResultItem(self, zwift_ids: Optional[list[str]]) -> Dict[str, CurveFittingResultItem]:

        min_coordinates = 5
        skipped_count = 0
        answer: Dict[str, CurveFittingResultItem] = {}

        if zwift_ids is None:
            zwift_ids = []

        print(f"Repository message: attempting curvefits for {len(zwift_ids)} candidates.")

        dict_of_JghBestPowerItem = self.get_dict_of_ZwiftPower90dayWattsItem_by_ids(zwift_ids)

        for zwift_id, item in dict_of_JghBestPowerItem.items():

            item.zwift_id = zwift_id

            ordinates = item.export_all_x_y_ordinates()

            if not ordinates:
                print(f"Repository message: ZwiftID={item.zwift_id} has no x_y ordinates from zwiftpower data. Skipped.")
                skipped_count += 1
                continue

            if all(value == 0 for value in ordinates.values()):
                print(f"Repository message: ZwiftID={item.zwift_id} has empty data. Skipped.")
                skipped_count += 1
                continue
        
            raw_xy_data_one_hour = item.export_x_y_ordinates_for_one_hour_zone_modelling()
            raw_xy_data_pull = item.export_x_y_ordinates_for_pull_zone_modelling()
            raw_xy_data_cp = item.export_x_y_ordinates_for_cp_w_prime_modelling()

            if len(raw_xy_data_cp) < 5 or len(raw_xy_data_pull) < min_coordinates or len(raw_xy_data_one_hour) < min_coordinates:
                print(f"Repository message: ZwiftID={item.zwift_id} is too sparse for reliable modelling. Skipped")
                skipped_count += 1
                continue

            coefficient_one_hour, exponent_one_hour, r_squared_one_hour, _, _ = do_curve_fit_with_decay_model(raw_xy_data_one_hour)
            coefficient_pull, exponent_pull, r_squared_pull, _, _ = do_curve_fit_with_decay_model(raw_xy_data_pull)
            critical_power, anaerobic_work_capacity, _, _, _  = do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)

            curvefit = CurveFittingResultItem(
                zwift_id=zwift_id,
                sixty_min_curve_coefficient = coefficient_one_hour,
                sixty_min_curve_exponent= exponent_one_hour,
                sixty_min_curve_r_squared= r_squared_one_hour,
                TTT_pull_curve_coefficient = coefficient_pull,
                TTT_pull_curve_exponent= exponent_pull,
                TTT_pull_curve_r_squared= r_squared_pull,
                CP=round(critical_power),
                AWC=round((anaerobic_work_capacity/1_000.0),1),
                when_curves_fitted = get_current_utc_iso8601_timestamp(),
            )

            answer[zwift_id] = curvefit
        print(f"Repository message: curve fitting completed. Total riders processed: {len(dict_of_JghBestPowerItem)}. Riders skipped due to insufficient data: {skipped_count}. Riders with curve fits: {len(answer)}.")
        return answer

    def _create_union_of_sets_as_dataframe(self, sample1: list[str], sample2: list[str]) -> pd.DataFrame:
        """
        Returns a pandas DataFrame representing the union of Zwift IDs found across all main datasets
        (Zwift, ZwiftRacingApp, ZwiftPower, ZwiftPower 90-day power graphs) and the provided sample lists.

        Each row corresponds to a unique Zwift ID and indicates its presence ("y" or "n") in each dataset
        and in the sample lists.

        Args:
            sample1 (list[str]): Optional list of Zwift IDs to include in the union and mark membership.
            sample2 (list[str]): Optional second list of Zwift IDs to include in the union and mark membership.

        Returns:
            pd.DataFrame: DataFrame with columns for Zwift ID, sample membership, and dataset membership.

        Columns:
            - zwift_id
            - in_sample1
            - in_sample2
            - zwift
            - zwiftracingapp
            - zwiftpower
            - zwiftpower_watts

        Notes:
            - The union includes all unique Zwift IDs found in any dataset or sample list.
            - Membership is indicated by "y" (present) or "n" (absent) for each column.
        """
        answer: list[tuple[str, str, str, str, str, str]] = []

        superset_of_zwiftID = set(sample1) | set(sample2) | \
                              set(self._dict_of_ZwiftItem.keys()) | \
                              set(self._dict_of_ZwiftRacingAppItem.keys()) | \
                              set(self._dict_of_ZwiftPower90dayWattsItem.keys())

        print(f"Total unique Zwift IDs in union: {len(superset_of_zwiftID)}")

        for key in superset_of_zwiftID:
            row = (
                key,
                "y" if key in sample1 else "n",
                "y" if key in sample2 else "n",
                "y" if key in self._dict_of_ZwiftItem.keys() else "n",
                "y" if key in self._dict_of_ZwiftRacingAppItem.keys() else "n",
                "y" if key in self._dict_of_ZwiftPower90dayWattsItem.keys() else "n",
            )
            answer.append(row)

        answer.sort(key=lambda x: x[0])

        df = pd.DataFrame(answer, columns=[
                self.COL_ZWIFT_ID,
                self.COL_IN_SAMPLE1,
                self.COL_IN_SAMPLE2,
                self.COL_IN_ZWIFT,
                self.COL_IN_ZWIFTRACINGAPP,
                self.COL_IN_ZWIFTPOWER,
                self.COL_IN_ZWIFTPOWER_WATTS_GRAPHS,
            ],)

        return df

    def _create_intersection_of_sets_as_dataframe(self, sample1: list[str], sample2: list[str]) -> pd.DataFrame:
        zwift_profiles = list(self._dict_of_ZwiftItem.keys())
        zwiftracingapp_profiles = list(self._dict_of_ZwiftRacingAppItem.keys())
        zwiftpower_90daybest_graphs = list(self._dict_of_ZwiftPower90dayWattsItem.keys())
        
        intersection = set(zwift_profiles) & set(zwiftracingapp_profiles) & set(zwiftpower_90daybest_graphs)

        if sample1:
            intersection = intersection & set(sample1)

        if sample2:
            intersection = intersection & set(sample2)

        answer: list[tuple[str, str, str, str, str, str]] = []
        for key in intersection:
            row = (
                key,
                "y" if key in sample1 else "n",
                "y" if key in sample2 else "n",
                "y" if key in self._dict_of_ZwiftItem.keys() else "n",
                "y" if key in self._dict_of_ZwiftRacingAppItem.keys() else "n",
                "y" if key in self._dict_of_ZwiftPower90dayWattsItem.keys() else "n",
            )
            answer.append(row)

        answer.sort(key=lambda x: x[0])

        df = pd.DataFrame(answer, columns=[
                "zwift_id",
                "in_sample1",
                "in_sample2",
                "in_zwift_profiles",
                "in_zwiftracingapp_profiles",
                "in_zwiftpower_profiles",
                "in_zwiftpower_90daybest_graphs",
            ],)

        return df

    def _create_union_of_sets_filtered_by_membership_as_dataframe(self, zwift: str, racingapp: str, zwiftpower_90day_cp: str
    ) -> pd.DataFrame:
        valid_values : set[str] = {"y_or_n", "y", "n"}
        invalid_params : list[str] = []

        for param_name, param_value in {
            "zwift": zwift,
            "racingapp": racingapp,
            "zwiftpower_90day_cp": zwiftpower_90day_cp,
        }.items():
            if param_value not in valid_values:
                invalid_params.append(f"{param_name}='{param_value}' (must be one of {valid_values})")

        if invalid_params:
            raise ValueError(f"Invalid parameters: {', '.join(invalid_params)}")

        df_superset = self._create_union_of_sets_as_dataframe([], [])

        def matches_template(row: pd.Series, template: dict[str, str]) -> bool:
            for col, value in template.items():
                if value == "y_or_n":
                    continue
                if row[col] != value:
                    return False
            return True

        template = {
            self.COL_IN_ZWIFT: zwift,
            self.COL_IN_ZWIFTRACINGAPP: racingapp,
            self.COL_IN_ZWIFTPOWER_WATTS_GRAPHS: zwiftpower_90day_cp,
        }

        filtered_df = df_superset[
            df_superset.apply(lambda row: matches_template(row, template), axis=1)
        ]

        return filtered_df

    def _create_intersection_of_sets_as_list(self, sample1: list[str], sample2: list[str]) -> list[str]:
        df = self._create_intersection_of_sets_as_dataframe(sample1, sample2)
        return df[self.COL_ZWIFT_ID].tolist()

    def _create_union_of_sets_filtered_by_membership_as_list(self, zwift: str, racingapp: str, zwiftpower_90day_cp: str
    ) -> list[str]:
        df = self._create_union_of_sets_filtered_by_membership_as_dataframe(zwift, racingapp, zwiftpower_90day_cp)
        return df[self.COL_ZWIFT_ID].tolist()

