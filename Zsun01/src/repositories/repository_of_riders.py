from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional
from paceline_modelling_items import CurveFittingResultItem
from critical_power import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model
from zwiftid_file_reader_sync import (
    read_zwiftdto_files_to_item_dict_sync,
    read_zwiftracingappdto_files_to_item_dict_sync,
    read_zwiftpower90daywattsdto_files_to_item_dict_sync,
)
from jgh_dictionary_helpers import filter_generic_dict_by_key
from jgh_formulae10 import calculate_projected_accelerated_level_up
from working_file_read_write import read_rider_stats_list_from_json_as_dict
from zwift_item import ZwiftItem
from zwiftracingapp_item import ZwiftRacingAppItem
from repository_of_routes import RepositoryOfRoutes
from rider_compute_item import RiderComputeItem
from rider_stats_item import RiderStatsItem
from slope_bucket_item import SlopeBucketItem
from route_item import RouteItem

from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem
from model_constructors import construct_RiderComputeItem, construct_RiderStatsItem, construct_CurveFittingResultItem

@dataclass
class RepositoryOfRiders:

    _dict_of_ZwiftItem                  :   Dict[str, ZwiftItem] = field(default_factory=dict)
    _dict_of_ZwiftRacingAppItem         :   Dict[str, ZwiftRacingAppItem] = field(default_factory=dict)
    _dict_of_ZwiftPower90dayWattsItem   :   Dict[str, ZwiftPowerFlattened90dayWattsItem] = field(default_factory=dict)
    _snapshot_of_dict_of_RiderStatsItem_when_accelerated_levelling_up_launched  :  Dict[str, RiderStatsItem] = field(default_factory=dict)

    _eligible_IDs                       :  list[str] = field(default_factory=list)
    _computed_dict_of_curveFitItem      :  Dict[str, CurveFittingResultItem] = field(default_factory=dict)
    _computed_dict_of_riderComputeItem  :  Dict[str, RiderComputeItem] = field(default_factory=dict)
    _computed_dict_of_riderStatsItem    :  Dict[str, RiderStatsItem] = field(default_factory=dict)

    _singleSegment           : SlopeBucketItem = field(default_factory = SlopeBucketItem)

    _routeItem                : RouteItem = field(default_factory = RouteItem) 

    # The main method to populate the repository. This is where the heavy lifting happens: reading files, doing curve fitting, and computing rider statistics. This method is synchronous/blocking and can take up to a minute to complete. It presumes that all files are present on local hard-drive and that their names match file_names and that the filenames match the zwiftIDs of the riders. In practice some or many files might be missing....

    def populate_repository(
        self,
        file_names: Optional[list[str]], # filenames are zwiftIDs. some of the files might or might not exist
        zwift_dir_path: str,
        zwiftracingapp_dir_path: str,
        zwiftpower_90day_graph_watts_dir_path: str,
        snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched_filepath : str,
        single_segment: SlopeBucketItem,
        routeItem: RouteItem
    )->bool:

        """
        Loads rider data from all three data sources, performs curve fitting, and computes rider
        statistics. This is the single entry point for populating the repository and must be called
        before any getter methods are used.

        This method is synchronous/blocking and can typically take up to a minute to complete.
        It executes the following steps in strict order:
            1. Reads Zwift profile files from disk.
            2. Reads ZwiftPower 90-day power watts files from disk.
            3. Reads ZwiftRacingApp profile files from disk.
            4. Reads the launch-date snapshot file for the accelerated levelling-up scheme.
            5. Fits decay and CP/W-prime curves to the 90-day power watts data.
            6. Computes RiderComputeItems for riders who have curve fit data.
            7. Computes RiderStatsItems for all riders with a Zwift profile.

        File presence is best-effort: file_names defines the candidate set of Zwift IDs to attempt.
        Individual files may be missing on disk without causing a failure -- missing data sources
        result in default empty values being used for the affected rider.

        Args:
            file_names (Optional[list[str]]):
                Candidate list of Zwift IDs to process. Each entry is expected to match both a
                filename on disk and a Zwift ID. If None, all files found in the directories are read.
            zwift_dir_path (str):
                Directory path containing Zwift profile files.
            zwiftracingapp_dir_path (str):
                Directory path containing ZwiftRacingApp profile files.
            zwiftpower_90day_graph_watts_dir_path (str):
                Directory path containing ZwiftPower 90-day best-power graph files.
            filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched (Optional[str]):
                Full file path to the JSON snapshot of RiderStatsItems captured at the launch date
                of the accelerated levelling-up scheme. Used to compute projected_accelerated_level
                for eligible riders.

        Returns:
            bool: True if the repository was populated successfully.
        """

        self._singleSegment = single_segment
        self._routeItem = routeItem

        print(f"Repository to read raw data is populating itself. This will take up to a minute.")
        print(f"1-3. Reading Zwift, ZwiftPower 90-day, and ZwiftRacingApp files in parallel.")

        def _read_zwift():
            return read_zwiftdto_files_to_item_dict_sync(Path(zwift_dir_path), file_names)

        def _read_zwiftpower():
            return read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(zwiftpower_90day_graph_watts_dir_path), file_names)

        def _read_zwiftracingapp():
            return read_zwiftracingappdto_files_to_item_dict_sync(Path(zwiftracingapp_dir_path), file_names)

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_zwift        = executor.submit(_read_zwift)
            future_zwiftpower   = executor.submit(_read_zwiftpower)
            future_racingapp    = executor.submit(_read_zwiftracingapp)
            self._dict_of_ZwiftItem                 = future_zwift.result()
            self._dict_of_ZwiftPower90dayWattsItem  = future_zwiftpower.result()
            self._dict_of_ZwiftRacingAppItem        = future_racingapp.result()

        print(f"4. Reading file with list of riders eligible for accelerated levelling up based on their achievement level and total experience points.")
        if snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched_filepath != "":
            self._snapshot_of_dict_of_RiderStatsItem_when_accelerated_levelling_up_launched = read_rider_stats_list_from_json_as_dict(Path(snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched_filepath))
        
        print(f"5. Fitting curves to 90-day power watts datapoints.")

        # now that we have read all the files that we could find, we need to determine the unique set of the union of zwiftIDs (dict keys) across all three datasets
        all_zwift_ids_as_set = set(self._dict_of_ZwiftItem.keys()).union(
            self._dict_of_ZwiftPower90dayWattsItem.keys(),
            self._dict_of_ZwiftRacingAppItem.keys()
        )
        all_zwift_ids = list(all_zwift_ids_as_set)

        self._computed_dict_of_curveFitItem = self._do_power_graph_curve_fitting(all_zwift_ids) #do first
        print(f"6. Building RiderComputeItems.")
        self._computed_dict_of_riderComputeItem = self._make_dict_of_RiderComputeItem(all_zwift_ids) # do second
        print(f"7. Building RiderStatsItems.")
        self._computed_dict_of_riderStatsItem = self._make_dict_of_RiderStatsItem(all_zwift_ids) # do third
        print(f"Repository successfully populated.")
   
        return True

    # Getters for the repository    


    def get_dict_of_ZwiftItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftItem]:
        return filter_generic_dict_by_key(self._dict_of_ZwiftItem, zwift_ids)

    def get_dict_of_ZwiftRacingAppItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftRacingAppItem]:
        return filter_generic_dict_by_key(self._dict_of_ZwiftRacingAppItem, zwift_ids)

    def get_dict_of_ZwiftPower90dayWattsItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, ZwiftPowerFlattened90dayWattsItem]:
        return filter_generic_dict_by_key(self._dict_of_ZwiftPower90dayWattsItem, zwift_ids)

    def get_dict_of_RiderComputeItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderComputeItem]:
        return filter_generic_dict_by_key(self._computed_dict_of_riderComputeItem, zwift_ids)

    def get_dict_of_RiderStatsItem_by_ids(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderStatsItem]:
        return filter_generic_dict_by_key(self._computed_dict_of_riderStatsItem, zwift_ids)

    # ...the heavy lifting: building the repository

    def _do_power_graph_curve_fitting(self, zwift_ids: Optional[list[str]]) -> Dict[str, CurveFittingResultItem]:

        min_coordinates = 5
        skipped_count = 0
        answer: Dict[str, CurveFittingResultItem] = {}

        if zwift_ids is None:
            zwift_ids = []

        print(f"Repository message: attempting curvefits for {len(zwift_ids)} candidates.")

        # by definition we only do curve fitting on those zwift_ids that have ZwiftPower90dayWattsItem data

        dict_of_90dayWattsItem = self.get_dict_of_ZwiftPower90dayWattsItem_by_ids(zwift_ids)

        for zwift_id, item in dict_of_90dayWattsItem.items():

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
            coefficient_pull, exponent_pull, r_squared_pull, _, _             = do_curve_fit_with_decay_model(raw_xy_data_pull)
            critical_power, anaerobic_work_capacity, _, _, _                  = do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)

            answer[zwift_id] = construct_CurveFittingResultItem(
                zwift_id,
                coefficient_one_hour,
                exponent_one_hour,
                r_squared_one_hour,
                coefficient_pull,
                exponent_pull,
                r_squared_pull,
                critical_power,
                anaerobic_work_capacity,
            )
        print(f"Repository message: curve fitting completed. Total riders processed: {len(dict_of_90dayWattsItem)}. Riders skipped due to insufficient data: {skipped_count}. Riders with curve fits: {len(answer)}.")
        return answer

    def _make_dict_of_RiderComputeItem(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderComputeItem]:
        """
        Iterates over the candidate Zwift IDs and builds a RiderBruteItem for each rider
        that has both a Zwift profile and curve fit data. Riders missing either data source
        are skipped -- by definition a RiderBruteItem only exists for curve-fitted riders.

        Construction of each item is delegated to build_RiderBruteItem in model_constructors.py.
        ZwiftRacingApp data is passed through as Optional; riders without it receive default
        empty values inside the builder.

        Args:
            zwift_ids (Optional[list[str]]):
                Candidate list of Zwift IDs to process. If None, an empty list is used
                and no items are produced.

        Returns:
            Dict[str, RiderBruteItem]: Dictionary of RiderComputeItems keyed by zwift_id.
            Only riders with both a ZwiftItem and a CurveFittingResultItem are included.
        """


        answer: Dict[str, RiderComputeItem] = {}

        if zwift_ids is None:
            zwift_ids = []

        print(f"Repository message: computing rider brute items for {len(zwift_ids)} candidates.")

        for key in zwift_ids:

            zwiftItem = self._dict_of_ZwiftItem.get(key)
            if zwiftItem is None:
                continue  # skip this rider if no Zwift data

            jghcurveItem = self._computed_dict_of_curveFitItem.get(key)
            if jghcurveItem is None:
                continue  # skip this rider if no curve fit data. by definition a Compute rider is someone with curve fit data

            answer[key] = construct_RiderComputeItem(
                zwiftItem,
                self._dict_of_ZwiftRacingAppItem.get(key),
                jghcurveItem,
            )

        print(f"Repository message: completed computing brute items for {len(answer)} riders.")

        return answer

    def _make_dict_of_RiderStatsItem(self, zwift_ids: Optional[list[str]]) -> Dict[str, RiderStatsItem]:
        """
        Iterates over the candidate Zwift IDs and builds a RiderStatsItem for each rider
        that has a Zwift profile. Riders without a Zwift profile are skipped -- it is the
        minimum required data source for a RiderStatsItem.

        ZwiftRacingApp data, RiderBruteItem data, and ZwiftPower 90-day watts data are all
        passed through as Optional; riders missing any of these receive default empty values
        inside the builder. Construction of each item is delegated to construct_RiderStatsItem
        in model_constructors.py.

        The projected_accelerated_level for each rider is resolved here before the builder
        is called, as it requires access to the launch-date snapshot dictionary which is
        repository state and not available inside the builder.

        Args:
            zwift_ids (Optional[list[str]]):
                Candidate list of Zwift IDs to process. If None, an empty list is used
                and no items are produced.

        Returns:
            Dict[str, RiderStatsItem]: Dictionary of RiderStatsItems keyed by zwift_id.
            Only riders with a ZwiftItem are included.
        """

        answer: Dict[str, RiderStatsItem] = {}

        if zwift_ids is None:
            zwift_ids = []

        print(f"Repository message: computing rider stats items for {len(zwift_ids)} riders.")

        for key in zwift_ids:

            zwiftItem = self._dict_of_ZwiftItem.get(key)
            if zwiftItem is None:
                continue  # skip this key/rider if no Zwift data

            this_rider_on_launch_date = self._snapshot_of_dict_of_RiderStatsItem_when_accelerated_levelling_up_launched.get(key)
            if this_rider_on_launch_date is not None and this_rider_on_launch_date.zwift_id == key:
                projected_accelerated_level = calculate_projected_accelerated_level_up(this_rider_on_launch_date.achievement_level, this_rider_on_launch_date.rider_score)
            else:
                projected_accelerated_level = 0  # if rider not in the file with list of riders eligible for accelerated levelling up, we set projected_accelerated_level to 0

            answer[key] = construct_RiderStatsItem(
                zwiftItem,
                self._dict_of_ZwiftRacingAppItem.get(key),
                self._computed_dict_of_riderComputeItem.get(key),
                self._dict_of_ZwiftPower90dayWattsItem.get(key),
                projected_accelerated_level,
                self._singleSegment,
                self._routeItem
            )

        print(f"Repository message: completed computing rider stats items for {len(answer)} riders.")

        return answer

