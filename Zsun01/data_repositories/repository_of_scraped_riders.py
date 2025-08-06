
import os
from typing import cast, Optional, Type, TypeVar, DefaultDict
from datetime import datetime
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from jgh_sanitise_string import cleanup_name_string
from jgh_read_write import write_pandas_dataframe_as_xlsx, read_filepath_as_text, help_select_filepaths_in_folder
from zwift_rider_particulars_item import ZwiftItem
from zwiftracingapp_rider_particulars_item import ZwiftRacingAppItem
from zwiftpower_rider_particulars_item import ZwiftPowerItem
from zsun_rider_item import ZsunItem
from zsun_watts_properties_item import ZsunWattsItem
import pandas as pd
from computation_classes import CurveFittingResultItem
from critical_power import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model 

from jgh_serialization import JghSerialization
from zwift_rider_particulars_dto import ZwiftDTO
from zwift_rider_particulars_item import ZwiftItem
from zwiftpower_watts_ordinates_dto import ZwiftPowerWattsDTO
from zwiftpower_rider_particulars_dto import ZwiftPowerDTO
from zwiftpower_rider_particulars_item import ZwiftPowerItem
from zwiftracingapp_rider_particulars_dto import ZwiftRacingAppDTO
from zwiftracingapp_rider_particulars_item import ZwiftRacingAppItem
from zsun_watts_properties_item import ZsunWattsItem
from zsun_rider_item import ZsunItem

import logging
logger = logging.getLogger(__name__)


#functions used to read many files in a folder and return a dictionary of items. used to read the thousands of raw zwift profiles, zwiftracingapp profiles, zwiftpower profiles, and zwiftpower best power files obtained by DaveK for Brute. 

def read_zwift_files(
    file_names: Optional[list[str]],
    dir_path: str,
) -> DefaultDict[str, ZwiftItem]:
    answer: defaultdict[str, ZwiftItem] = defaultdict(ZwiftItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing...")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")

        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftDTO)
            dto = cast(ZwiftDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        item = ZwiftItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_zwiftracingapp_files(
    file_names: Optional[list[str]],
    dir_path: str,
) -> DefaultDict[str, ZwiftRacingAppItem]:
    answer: defaultdict[str, ZwiftRacingAppItem] = defaultdict(ZwiftRacingAppItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing..")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppDTO)
            dto = cast(ZwiftRacingAppDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        item = ZwiftRacingAppItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_zwiftpower_files(
    file_names: Optional[list[str]],
    dir_path: str,
) -> DefaultDict[str, ZwiftPowerItem]:
    answer: defaultdict[str, ZwiftPowerItem] = defaultdict(ZwiftPowerItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing..")

    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerDTO)
            dto = cast(ZwiftPowerDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        item = ZwiftPowerItem.from_dataTransferObject(dto)
        answer[zwift_id] = item

    return answer

def read_zwiftpower_graph_watts_files(
    file_names: Optional[list[str]],
    dir_path: str,
) -> DefaultDict[str, ZsunWattsItem]:
    answer: defaultdict[str, ZsunWattsItem] = defaultdict(ZsunWattsItem)

    file_paths = help_select_filepaths_in_folder(file_names, ".json", dir_path)
    logger.info(f"Found {len(file_paths)} files in {dir_path}. Please wait. Processing..")
    file_count = 0
    error_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.debug(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerWattsDTO)
            dto = cast(ZwiftPowerWattsDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
        zwift_id, _ = os.path.splitext(file_name)
        temp = ZsunWattsItem.from_ZwiftPowerBestPowerDTO(dto)
        temp.zwift_id = zwift_id
        answer[zwift_id] = temp

    return answer


# repository for scraped data from DaveK's work for Zsun

T = TypeVar("T")  # Generic type variable for the item type in the defaultdict

@dataclass
class RepositoryForScrapedDataFromDaveK:
    """
    Repository for managing and querying scraped Zwift rider data from multiple sources.

    This class aggregates rider data from Zwift, ZwiftPower, ZwiftRacingApp, and
    ZwiftPower best power graphs, providing unified access and filtering utilities.
    It supports loading data from JSON files, intersection and superset analysis,
    and conversion to pandas DataFrames for further analysis.

    Attributes:
        _dict_of_ZwiftItem (DefaultDict[str, ZwiftItem]):
            Zwift profile data indexed by Zwift ID.
        _dict_of_ZwiftPowerItem (DefaultDict[str, ZwiftPowerItem]):
            ZwiftPower profile data indexed by Zwift ID.
        _dict_of_ZwiftRacingAppItem (DefaultDict[str, ZwiftRacingAppItem]):
            ZwiftRacingApp profile data indexed by Zwift ID.
        _dict_of_ZsunWattsItem (DefaultDict[str, ZsunWattsItem]):
            ZwiftPower best power graph data indexed by Zwift ID.

    Methods:
        populate_repository(...):
            Loads rider data from specified directories into the repository.
        get_table_of_superset_of_sets_by_id(sample1, sample2):
            Returns a DataFrame showing the presence of Zwift IDs across all sources.
        get_table_of_intersections_of_sets(sample1, sample2):
            Returns a DataFrame of Zwift IDs common to all datasets and samples.
        get_table_of_filtered_intersections_of_sets(zwift, racingapp, zwiftpower, zwiftpower_90day_cp):
            Returns a DataFrame filtered by specified source presence criteria.
        get_list_of_intersections_of_sets(sample1, sample2):
            Returns a list of Zwift IDs present in all datasets and samples.
        get_list_of_filtered_intersections_of_sets(zwift, racingapp, zwiftpower, zwiftpower_90day_cp):
            Returns a filtered list of Zwift IDs based on source presence criteria.
        get_dict_of_ZwiftItem(zwift_ids):
            Returns a filtered dictionary of ZwiftItem objects.
        get_dict_of_ZwiftPowerItem(zwift_ids):
            Returns a filtered dictionary of ZwiftPowerItem objects.
        get_dict_of_ZwiftRacingAppItem(zwift_ids):
            Returns a filtered dictionary of ZwiftRacingAppItem objects.
        get_dict_of_ZsunWattsItem(zwift_ids):
            Returns a filtered dictionary of ZsunWattsItem objects.
        get_dict_of_CurveFittingResultItem(zwift_ids):
            Returns curve fitting results for eligible Zwift IDs.
        get_dict_of_ZsunItem(zwift_ids):
            Returns a dictionary of ZsunItem objects, combining all sources and curve fits.

    Notes:
        - All data is indexed by Zwift ID.
        - Filtering and intersection methods support flexible analysis across sources.
        - Designed for use in data analysis, reporting, and team management workflows.
    """

    _dict_of_ZwiftItem:          DefaultDict[str, ZwiftItem]          = field(default_factory=lambda: defaultdict(ZwiftItem))
    _dict_of_ZwiftPowerItem:     DefaultDict[str, ZwiftPowerItem]     = field(default_factory=lambda: defaultdict(ZwiftPowerItem))
    _dict_of_ZwiftRacingAppItem: DefaultDict[str, ZwiftRacingAppItem] = field(default_factory=lambda: defaultdict(ZwiftRacingAppItem))
    _dict_of_ZsunWattsItem:      DefaultDict[str, ZsunWattsItem]      = field(default_factory=lambda: defaultdict(ZsunWattsItem))

    # Repository constants for DataFrame column names
    COL_ZWIFT_ID                  = "zwiftID"
    COL_IN_SAMPLE1                = "in_sample1"
    COL_IN_SAMPLE2                = "in_sample2"
    COL_IN_ZWIFT                  = "zwift"
    COL_IN_ZWIFTPOWER             = "zwiftpower"
    COL_IN_ZWIFTPOWER_WATTS_GRAPHS= "zwiftpower_watts"
    COL_IN_ZWIFTRACINGAPP         = "zwiftracingapp"


    def populate_repository(
        self,
        file_names: Optional[list[str]],
        zwift_dir_path: str,
        zwiftracingapp_dir_path: str,
        zwiftpower_dir_path: str,
        zwiftpower_90day_graph_watts_dir_path: str,
    ):
        self._dict_of_ZwiftItem          = read_zwift_files(file_names, zwift_dir_path)
        self._dict_of_ZwiftRacingAppItem = read_zwiftracingapp_files(file_names, zwiftracingapp_dir_path)
        self._dict_of_ZwiftPowerItem     = read_zwiftpower_files(file_names, zwiftpower_dir_path)
        self._dict_of_ZsunWattsItem      = read_zwiftpower_graph_watts_files(file_names, zwiftpower_90day_graph_watts_dir_path)

    def get_table_of_superset_of_sets_by_id(self, sample1: list[str], sample2: list[str]) -> pd.DataFrame:
        """
        Creates a table showing the commonality of Zwift IDs across various sources.

        Args:
            sample1 (list[str]): A list of Zwift IDs in the first sample.
            sample2 (list[str]): A list of Zwift IDs in the second sample.

        Returns:
            pd.DataFrame: A DataFrame with columns indicating the presence of Zwift IDs in various sources.
        """
        # Step 1: Instantiate the answer list
        answer: list[tuple[str, str, str, str, str, str, str]] = []

        # Step 2: Create a superset of all Zwift IDs - the zwift dataset is over a thousand, the others are half that. zwiftracing contains only 200 odd
        superset_of_zwiftID = set(sample1) | set(sample2) | \
                              set(self._dict_of_ZwiftItem.keys()) | \
                              set(self._dict_of_ZwiftRacingAppItem.keys()) | \
                              set(self._dict_of_ZwiftPowerItem.keys()) | \
                              set(self._dict_of_ZsunWattsItem.keys())

        # Optional: Log the size of the superset for debugging
        logger.info(f"Total unique Zwift IDs in superset: {len(superset_of_zwiftID)}")

        # Step 3: Populate the answer list
        for key in superset_of_zwiftID:
            row = (
                key,  # col 0: zwiftID
                "y" if key in sample1 else "n",  # col 1: in_sample1
                "y" if key in sample2 else "n",  # col 2: in_sample2
                "y" if key in self._dict_of_ZwiftItem.keys() else "n",  # col 3: in_zwift_profiles
                "y" if key in self._dict_of_ZwiftRacingAppItem.keys() else "n",  # col 4: in_zwiftracingapp_profiles
                "y" if key in self._dict_of_ZwiftPowerItem.keys() else "n",  # col 5: in_zwiftpower_profiles
                "y" if key in self._dict_of_ZsunWattsItem.keys() else "n",  # col 6: in_zwiftpower_90daybest_graphs
            )
            answer.append(row)

        answer.sort(key=lambda x: x[0])  # Sort by the first element (zwiftID)

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

    def get_table_of_intersections_of_sets(self, sample1: list[str], sample2: list[str]) -> pd.DataFrame:
        """
        Creates a table showing Zwift IDs that are common to all datasets.
        If sample1 and sample2 are empty, they are excluded from the criterion.

        Args:
            sample1 (list[str]): A list of Zwift IDs in the first sample.
            sample2 (list[str]): A list of Zwift IDs in the second sample.

        Returns:
            pd.DataFrame: A DataFrame with columns indicating the presence of Zwift IDs in all datasets.
        """
        # Step 1: Create sets for all datasets
        #create four separate list [str] of keys of each dataset
        zwift_profiles = list(self._dict_of_ZwiftItem.keys())
        zwiftracingapp_profiles = list(self._dict_of_ZwiftRacingAppItem.keys())
        zwiftpower_profiles = list(self._dict_of_ZwiftPowerItem.keys())
        zwiftpower_90daybest_graphs = list(self._dict_of_ZsunWattsItem.keys())
        
        intersection = set(zwift_profiles) & set(zwiftracingapp_profiles) & set(zwiftpower_profiles) & set(zwiftpower_90daybest_graphs)

        # Include sample1 and sample2 in the criterion only if they are not empty
        if sample1:
            intersection = intersection & set(sample1)

        if sample2:
            intersection = intersection & set(sample2)



        # Step 2: Find Zwift IDs common to all datasets

        # Step 3: Populate the answer list
        answer: list[tuple[str, str, str, str, str, str, str]] = []
        for key in intersection:
            row = (
                key,  # col 0: zwiftID
                "y" if key in sample1 else "n",  # col 1: in_sample1
                "y" if key in sample2 else "n",  # col 2: in_sample2
                "y" if key in self._dict_of_ZwiftItem.keys() else "n",  # col 3: in_zwift_profiles
                "y" if key in self._dict_of_ZwiftRacingAppItem.keys() else "n",  # col 4: in_zwiftracingapp_profiles
                "y" if key in self._dict_of_ZwiftPowerItem.keys() else "n",  # col 5: in_zwiftpower_profiles
                "y" if key in self._dict_of_ZsunWattsItem.keys() else "n",  # col 6: in_zwiftpower_90daybest_graphs
            )
            answer.append(row)

        answer.sort(key=lambda x: x[0])  # Sort by the first element (zwiftID)

        df = pd.DataFrame(answer, columns=[
                "zwiftID",
                "in_sample1",
                "in_sample2",
                "in_zwift_profiles",
                "in_zwiftracingapp_profiles",
                "in_zwiftpower_profiles",
                "in_zwiftpower_90daybest_graphs",
            ],)

        return df

    def get_table_of_filtered_intersections_of_sets(self, zwift: str, racingapp: str, zwiftpower: str, zwiftpower_90day_cp: str
    ) -> pd.DataFrame:
        """
        Filters the superset DataFrame based on the provided template.

        Args:
            zwift (str): Filter for the "in_zwift_profiles" column. Allowed values: "y_or_n", "y", "n".
            racingapp (str): Filter for the "in_zwiftracingapp_profiles" column. Allowed values: "y_or_n", "y", "n".
            zwiftpower (str): Filter for the "in_zwiftpower_profiles" column. Allowed values: "y_or_n", "y", "n".
            zwiftpower_90day_cp (str): Filter for the "in_zwiftpower_90daybest_graphs" column. Allowed values: "y_or_n", "y", "n".

        Returns:
            pd.DataFrame: A filtered DataFrame based on the provided template.
        """
        # validate the parameters
        valid_values : set[str] = {"y_or_n", "y", "n"}
        invalid_params : list[str] = []

        for param_name, param_value in {
            "zwift": zwift,
            "racingapp": racingapp,
            "zwiftpower": zwiftpower,
            "zwiftpower_90day_cp": zwiftpower_90day_cp,
        }.items():
            if param_value not in valid_values:
                invalid_params.append(f"{param_name}='{param_value}' (must be one of {valid_values})")

        if invalid_params:
            raise ValueError(f"Invalid parameters: {', '.join(invalid_params)}")

        # get_table_of_superset_of_sets_by_id
        df_superset = self.get_table_of_superset_of_sets_by_id([], [])

        # write elper method to Filter the DataFrame
        def matches_template(row: pd.Series, template: dict[str, str]) -> bool:
            """
            Checks if a row matches the filtering template.

            Args:
                row (pd.Series): A row from the DataFrame.
                template (dict[str, str]): A dictionary where keys are column names and values are the expected values 
                                           ("y", "n", or "y_or_n").

            Returns:
                bool: True if the row matches the template, False otherwise.
            """
            for col, value in template.items():
                if value == "y_or_n":
                    continue  # Match any value
                if row[col] != value:
                    return False
            return True

        # define the template for filtering
        template = {
            self.COL_IN_ZWIFT: zwift,
            self.COL_IN_ZWIFTRACINGAPP: racingapp,
            self.COL_IN_ZWIFTPOWER: zwiftpower,
            self.COL_IN_ZWIFTPOWER_WATTS_GRAPHS: zwiftpower_90day_cp,
        }

  
        # apply the filter
        filtered_df = df_superset[
            df_superset.apply(lambda row: matches_template(row, template), axis=1)
        ]

        # return the filtered DataFrame
        return filtered_df

    def get_list_of_intersections_of_sets(self, sample1: list[str], sample2: list[str]) -> list[str]:
        """
        Creates a list of Zwift IDs that are common to all datasets.
        If sample1 and sample2 are empty, they are excluded from the criterion.
        Args:
            sample1 (list[str]): A list of Zwift IDs in the first sample.
            sample2 (list[str]): A list of Zwift IDs in the second sample.
        Returns:
            list[str]: A list of Zwift IDs common to all datasets.
        """
        df = self.get_table_of_intersections_of_sets(sample1, sample2)
        return df[self.COL_ZWIFT_ID].tolist()

    def get_list_of_filtered_intersections_of_sets(self, zwift: str, racingapp: str, zwiftpower: str, zwiftpower_90day_cp: str
    ) -> list[str]:
        """
        Filters the superset DataFrame based on the provided template and returns a list of Zwift IDs.
        Args:
            zwift (str): Filter for the "in_zwift_profiles" column. Allowed values: "y_or_n", "y", "n".
            racingapp (str): Filter for the "in_zwiftracingapp_profiles" column. Allowed values: "y_or_n", "y", "n".
            zwiftpower (str): Filter for the "in_zwiftpower_profiles" column. Allowed values: "y_or_n", "y", "n".
            zwiftpower_90day_cp (str): Filter for the "in_zwiftpower_90daybest_graphs" column. Allowed values: "y_or_n", "y", "n".
        Returns:
            list[str]: A filtered list of Zwift IDs based on the provided template.
        """
        df = self.get_table_of_filtered_intersections_of_sets(zwift, racingapp, zwiftpower, zwiftpower_90day_cp)
        return df[self.COL_ZWIFT_ID].tolist()
 
    def _get_dict_of_generic_items(self, source_dict: DefaultDict[str, T], zwift_ids: Optional[list[str]], default_factory: Type[T]) -> DefaultDict[str, T]:
        """
        Generic method to retrieve a filtered defaultdict of items based on provided Zwift IDs.

        Args:
            source_dict (defaultdict[str, T]): The source dictionary to filter.
            zwift_ids (Optional[list[str]]): List of Zwift IDs to filter. If None, return all items.
            default_factory (Type[T]): The default factory for the defaultdict.

        Returns:
            defaultdict[str, T]: A filtered defaultdict of items.
        """
        answer: DefaultDict[str, T] = defaultdict(default_factory)

        # all of them
        if not zwift_ids:
            for key, value in source_dict.items():
                answer[key] = value
            return answer

        # filter them
        for zwift_id in zwift_ids:
            if zwift_id in source_dict:
                answer[zwift_id] = source_dict[zwift_id]

        return answer

    def get_dict_of_ZwiftItem(self, zwift_ids: Optional[list[str]]) -> DefaultDict[str, ZwiftItem]:
        return self._get_dict_of_generic_items(self._dict_of_ZwiftItem, zwift_ids, ZwiftItem)

    def get_dict_of_ZwiftPowerItem(self, zwift_ids: Optional[list[str]]) -> DefaultDict[str, ZwiftPowerItem]:
        return self._get_dict_of_generic_items(self._dict_of_ZwiftPowerItem, zwift_ids, ZwiftPowerItem)

    def get_dict_of_ZwiftRacingAppItem(self, zwift_ids: Optional[list[str]]) -> DefaultDict[str, ZwiftRacingAppItem]:
        return self._get_dict_of_generic_items(self._dict_of_ZwiftRacingAppItem, zwift_ids, ZwiftRacingAppItem)

    def get_dict_of_ZsunWattsItem(self, zwift_ids: Optional[list[str]]) -> DefaultDict[str, ZsunWattsItem]:
        return self._get_dict_of_generic_items(self._dict_of_ZsunWattsItem, zwift_ids, ZsunWattsItem)

    def get_dict_of_CurveFittingResultItem(self, zwift_ids: Optional[list[str]]) -> DefaultDict[str, CurveFittingResultItem]:

        min_coordinates = 5 # minimum I desire for reliable curve fitting
        skipped_count = 0
        answer : defaultdict[str, CurveFittingResultItem] = defaultdict(CurveFittingResultItem)

        if zwift_ids is None:
            zwift_ids = []

        dict_of_JghBestPowerItem = self.get_dict_of_ZsunWattsItem(zwift_ids)

        for zwiftID, item in dict_of_JghBestPowerItem.items():

            item.zwift_id = zwiftID

            ordinates = item.export_all_x_y_ordinates()

            if not ordinates:
                logger.warning(f"Repository message: ZwiftID {item.zwift_id} has no ordinates")
                skipped_count += 1
                continue

            if all(value == 0 for value in ordinates.values()):
                logger.warning(f"Repository message: ZwiftID {item.zwift_id} has empty data")
                skipped_count += 1
                continue
        
            raw_xy_data_one_hour = item.export_x_y_ordinates_for_one_hour_zone_modelling()
            raw_xy_data_pull = item.export_x_y_ordinates_for_pull_zone_modelling()
            raw_xy_data_cp = item.export_x_y_ordinates_for_cp_w_prime_modelling()

            if len(raw_xy_data_cp) < 5 or len(raw_xy_data_pull) < min_coordinates or len(raw_xy_data_one_hour) < min_coordinates:
                logger.warning(f"Repository message: {item.zwift_id} too sparse for reliable modelling.")
                skipped_count += 1
                continue

            coefficient_one_hour, exponent_one_hour, r_squared_one_hour, _, _ = do_curve_fit_with_decay_model(raw_xy_data_one_hour)
            coefficient_pull, exponent_pull, r_squared_pull, _, _ = do_curve_fit_with_decay_model(raw_xy_data_pull)
            critical_power, anaerobic_work_capacity, _, _, _  = do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)

            curvefit = CurveFittingResultItem(
                zwift_id=zwiftID,
                one_hour_curve_coefficient = coefficient_one_hour,
                one_hour_curve_exponent= exponent_one_hour,
                one_hour_curve_r_squared= r_squared_one_hour,
                TTT_pull_curve_coefficient = coefficient_pull,
                TTT_pull_curve_exponent= exponent_pull,
                TTT_pull_curve_r_squared= r_squared_pull,
                CP=round(critical_power),
                AWC=round((anaerobic_work_capacity/1_000.0),1),
                when_curves_fitted = datetime.now().isoformat(),
            )

            answer[zwiftID] = curvefit

        logger.info(f"Repository message: successfuly completed {len(answer)} curve fittings.")
        logger.info(f"Repository message: skipped {skipped_count} riders due to insufficient data for modelling. Size requirement is {min_coordinates} ordinates minimum.")

        return answer

    def get_dict_of_ZsunItem(self, zwift_ids: Optional[list[str]]) -> DefaultDict[str, ZsunItem]:

        answer : defaultdict[str, ZsunItem] = defaultdict(ZsunItem)

        if zwift_ids is None:
            zwift_ids = []

        eligible_IDs = set(self.get_list_of_filtered_intersections_of_sets("y","y_or_n","y_or_n","y"))

        eligible_IDs = list(set(eligible_IDs) & set(zwift_ids))

        jgh_curve_dict = self.get_dict_of_CurveFittingResultItem(eligible_IDs)
    
        for key in self.get_dict_of_ZwiftItem(eligible_IDs):

            zwiftItem = self._dict_of_ZwiftItem[key]
            zwiftpowerItem = self._dict_of_ZwiftPowerItem[key]
            zwiftracingappItem = self._dict_of_ZwiftRacingAppItem[key]
            jghcurveItem = jgh_curve_dict[key]

            if key in self._dict_of_ZwiftRacingAppItem:
                name = self._dict_of_ZwiftRacingAppItem[key].fullname or f"{zwiftItem.first_name} {zwiftItem.last_name}"
            else:
                name = f"{zwiftItem.first_name} {zwiftItem.last_name}"

            zwiftItem = ZsunItem(
                zwift_id                          = zwiftItem.zwift_id,
                name                              = cleanup_name_string(name),
                weight_kg                         = round((zwiftItem.weight_grams or 0.0) / 1_000.0, 1),
                height_cm                         = round((zwiftItem.height_mm or 0.0) / 10.0),
                gender                            = "m" if zwiftItem.male else "f",
                age_years                         = zwiftItem.age_years,
                age_group                          = zwiftracingappItem.age_group,
                zwift_ftp                         = round(zwiftItem.ftp),
                zwiftpower_zFTP                   = round(zwiftpowerItem.zftp),
                zwiftracingapp_zpFTP              = round(zwiftracingappItem.zp_FTP),
                zsun_one_hour_watts               = round(jghcurveItem.one_hour_curve_coefficient),
                zsun_CP                           = jghcurveItem.CP,
                zsun_AWC                          = jghcurveItem.AWC,
                zwift_zrs                         = round(zwiftItem.competitionMetrics.racingScore),
                zwift_cat                         = zwiftItem.competitionMetrics.category,
                zwiftracingapp_score              = round(zwiftracingappItem.raceitem.max90.rating),
                zwiftracingapp_cat_num            = zwiftracingappItem.raceitem.max90.mixed.number,
                zwiftracingapp_cat_name           = zwiftracingappItem.raceitem.max90.mixed.category,
                zwiftracingapp_CP                 = round(zwiftracingappItem.poweritem.CP),
                zwiftracingapp_AWC                = round(zwiftracingappItem.poweritem.AWC / 1_000.0),
                zsun_one_hour_curve_coefficient   = jghcurveItem.one_hour_curve_coefficient,
                zsun_one_hour_curve_exponent      = jghcurveItem.one_hour_curve_exponent,
                zsun_TTT_pull_curve_coefficient   = jghcurveItem.TTT_pull_curve_coefficient,
                zsun_TTT_pull_curve_exponent      = jghcurveItem.TTT_pull_curve_exponent,
                zsun_TTT_pull_curve_fit_r_squared = jghcurveItem.one_hour_curve_r_squared,
                zsun_when_curves_fitted           = jghcurveItem.when_curves_fitted,
            )

            answer[key] = zwiftItem

        return answer


# Testing


def main03():


    my_dict = read_zwift_files(None, ZWIFT_DIRPATH)

    logger.info (f"Imported {len(my_dict)} zwift profile items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Profile for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.last_name} zFTP = {round(item.ftp)} Watts, Height = {round(item.height_mm/10.0)} cm")

    logger.info(f"Imported {len(my_dict)} items")

def main04():

    my_dict = read_zwiftracingapp_files(None, ZWIFTRACINGAPP_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.fullname} country = {item.country}")

    logger.info(f"Imported {len(my_dict)} items")

def main05():

    my_dict = read_zwiftpower_files(None, ZWIFTPOWER_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} {item.zwift_name}")

    logger.info(f"Imported {len(my_dict)} items")

def main06():

    my_dict = read_zwiftpower_graph_watts_files(None, ZWIFTPOWER_GRAPHS_DIRPATH)

    logger.info (f"Imported {len(my_dict)} items")
    for zwift_id, item in my_dict.items():
        if not item:
            logger.warning(f"Item for zwiftid = {zwift_id} is missing.")
        logger.info(f"{zwift_id} cp60 = {item.bp_60}")

    logger.info(f"Imported {len(my_dict)} items")

def main11():

    # Initialize the repository
    rep = RepositoryForScrapedDataFromDaveK()

    # Populate the repository with data
    rep.populate_repository(
        file_names=None,
        zwift_dir_path=ZWIFT_DIRPATH,
        zwiftracingapp_dir_path=ZWIFTRACINGAPP_DIRPATH,
        zwiftpower_dir_path=ZWIFTPOWER_DIRPATH,
        zwiftpower_90day_graph_watts_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
    )

    # ... rest of the function remains unchanged ...
    # Define sample Zwift IDs for testing
    betel = [
  "1024413",
  "11526",
  "11741",
  "1193",
  "1657744",
  "1707548",
  "183277",
  "1884456",
  "2398312",
  "2508033",
  "2682791",
  "3147366",
  "383480",
  "384442",
  "480698",
  "5134",
  "5421258",
  "5490373",
  "5530045",
  "5569057",
  "6142432",
  "9011",
  "991817"
] # betel, only two of whom are in all the datasets - dave and scott

    # Example: get the superset - should be more than 1500
    df = rep.get_table_of_superset_of_sets_by_id([], [])
    logger.debug("DataFrame of superset of Zwift IDs in all datasets including samples:")
    logger.debug(df)
    OUTPUT_FILENAME = "beautiful_superset_of_everything.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)

    # Example: get the intersection - should be about 80
    df = rep.get_table_of_intersections_of_sets([], [])
    logger.debug("DataFrame of intesection of Zwift IDs in main datasets:")
    logger.debug(df)
    OUTPUT_FILENAME2 = "beautiful_intersection_of_main_datasets.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME2, OUTPUT_DIRPATH)


    # Example: get an intersection of all main sets and betel - should be tiny - 4
    df = rep.get_table_of_intersections_of_sets(betel, [])
    logger.debug("DataFrame of intesection of Zwift IDs in all datasets and Betel:")
    logger.debug(df)
    OUTPUT_FILENAME3 = "beautiful_intersection_of_main_datasets_and_betel.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME3, OUTPUT_DIRPATH)

def main12():

    # Initialize the repository
    rep = RepositoryForScrapedDataFromDaveK()

    # Populate the repository with data
    rep.populate_repository(
        file_names=None,
        zwift_dir_path=ZWIFT_DIRPATH,
        zwiftracingapp_dir_path=ZWIFTRACINGAPP_DIRPATH,
        zwiftpower_dir_path=ZWIFTPOWER_DIRPATH,
        zwiftpower_90day_graph_watts_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
    )

    # Define any test parameters for get_table_of_filtered_intersections_of_sets
    zwift_filter = "y" 
    racingapp_filter = "y"
    zwiftpower_filter = "y"
    zwiftpower_90day_cp_filter = "y"

    # Call the get_table_of_filtered_intersections_of_sets method
    filtered_df = rep.get_table_of_filtered_intersections_of_sets(
        zwift=zwift_filter,
        racingapp=racingapp_filter,
        zwiftpower=zwiftpower_filter,
        zwiftpower_90day_cp=zwiftpower_90day_cp_filter
    )

    # Display the filtered DataFrame
    logger.debug("Filtered DataFrame:")
    logger.debug(filtered_df)

    # Validate the test results
    # Check if the DataFrame is not empty
    assert not filtered_df.empty, "Filtered DataFrame is empty, but it probably shouldn't be (although not definitely)."

    # Optionally, save the filtered DataFrame to an Excel file for verification
    OUTPUT_FILENAME = "beautiful_matching_specified_boolean_filter_criteria.xlsx"
    write_pandas_dataframe_as_xlsx(filtered_df, OUTPUT_FILENAME, OUTPUT_DIRPATH)
    logger.info(f"Test passed. Filtered DataFrame saved to {OUTPUT_DIRPATH}{OUTPUT_FILENAME}")

def main13():

    # Initialize the repository
    rep = RepositoryForScrapedDataFromDaveK()

    # Populate the repository with data
    rep.populate_repository(
        [],
        zwift_dir_path=ZWIFT_DIRPATH,
        zwiftracingapp_dir_path=ZWIFTRACINGAPP_DIRPATH,
        zwiftpower_dir_path=ZWIFTPOWER_DIRPATH,
        zwiftpower_90day_graph_watts_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
        logger=logger,
        log_level=log_level
    )

    # Example: get the superset - should be more than 1500
    dict_of_items = rep.get_dict_of_ZwiftItem([])
    logger.debug(f"Zwift profiles:\n{dict_of_items.values()}\n")
    logger.info(f"Zwift profiles: {len(dict_of_items.items())}\n")

    logger.debug(f"{dict_of_items}")

    #convert to dict to list of values
    items = list(dict_of_items.values())

    # Create a DataFrame from the list of velo files
    data = []
    for item in items:
        # Assuming each velo object has a method to convert it to a dictionary
        data.append(asdict(item))  # Replace with the actual method to get a dictionary representation

    df = pd.DataFrame(data)

    logger.debug("DataFrame of all Zwift profiles:")
    logger.debug(df)
    OUTPUT_FILENAME = "sexy_spreadsheet_of_all_Zwift_profiles.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)
    logger.info(f"Test passed. Filtered DataFrame saved to {OUTPUT_DIRPATH}{OUTPUT_FILENAME}")

def main14():

    # Initialize the repository
    rep = RepositoryForScrapedDataFromDaveK()

    # Populate the repository with data
    rep.populate_repository(
        None,
        zwift_dir_path=ZWIFT_DIRPATH,
        zwiftracingapp_dir_path=ZWIFTRACINGAPP_DIRPATH,
        zwiftpower_dir_path=ZWIFTPOWER_DIRPATH,
        zwiftpower_90day_graph_watts_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
        logger=logger,
        log_level=log_level
    )

    # Example: get the superset - should be more than 1500
    dict_of_items = rep.get_dict_of_ZwiftRacingAppItem([])
    logger.debug(f"ZwiftRacingApp profiles:\n{dict_of_items.values()}\n")
    logger.info(f"ZwiftRacingApp profiles: {len(dict_of_items.items())}\n")

    logger.debug(f"{dict_of_items}")

    #convert to dict to list of values
    items = list(dict_of_items.values())

    # Create a DataFrame from the list of velo files
    data = []
    for item in items:
        # Assuming each velo object has a method to convert it to a dictionary
        data.append(asdict(item))  # Replace with the actual method to get a dictionary representation

    df = pd.DataFrame(data)

    logger.debug("DataFrame of all ZwiftRacingApp profiles:")
    logger.debug(df)
    OUTPUT_FILENAME = "sexy_spreadsheet_of_all_ZwiftRacingApp_profiles.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)
    logger.info(f"Test passed. Filtered DataFrame saved to {OUTPUT_DIRPATH}{OUTPUT_FILENAME}")

def main15():

    # Initialize the repository
    rep = RepositoryForScrapedDataFromDaveK()

    # Populate the repository with data
    rep.populate_repository(
        None,
        zwift_dir_path=ZWIFT_DIRPATH,
        zwiftracingapp_dir_path=ZWIFTRACINGAPP_DIRPATH,
        zwiftpower_dir_path=ZWIFTPOWER_DIRPATH,
        zwiftpower_90day_graph_watts_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
    )

    # Example: get the superset - should be more than 1500
    dict_of_items = rep.get_dict_of_ZwiftPowerItem([])
    logger.debug(f"ZwiftPower profiles:\n{dict_of_items.values()}\n")
    logger.info(f"ZwiftPower profiles: {len(dict_of_items.items())}\n")

    logger.debug(f"{dict_of_items}")

    #convert to dict to list of values
    items = list(dict_of_items.values())

    # Create a DataFrame from the list of velo files
    data = []
    for item in items:
        # Assuming each velo object has a method to convert it to a dictionary
        data.append(asdict(item))  # Replace with the actual method to get a dictionary representation

    df = pd.DataFrame(data)

    logger.debug("DataFrame of all ZwiftPower profiles:")
    logger.debug(df)
    OUTPUT_FILENAME = "sexy_spreadsheet_of_all_ZwiftPower_profiles.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)
    logger.info(f"Test passed. Filtered DataFrame saved to {OUTPUT_DIRPATH}{OUTPUT_FILENAME}")

def main16():

    # Initialize the repository
    rep = RepositoryForScrapedDataFromDaveK()

    # Populate the repository with data
    rep.populate_repository(
        None,
        zwift_dir_path=ZWIFT_DIRPATH,
        zwiftracingapp_dir_path=ZWIFTRACINGAPP_DIRPATH,
        zwiftpower_dir_path=ZWIFTPOWER_DIRPATH,
        zwiftpower_90day_graph_watts_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
    )

    # Example: get the superset - should be more than 1500
    dict_of_items = rep.get_dict_of_ZsunWattsItem([])
    logger.debug(f"Jgh best power curves:\n{dict_of_items.values()}\n")
    logger.info(f"Jgh best power curves: {len(dict_of_items.items())}\n")

    logger.debug(f"{dict_of_items}")

    #convert to dict to list of values
    items = list(dict_of_items.values())

    # Create a DataFrame from the list of velo files
    data = []
    for item in items:
        # Assuming each velo object has a method to convert it to a dictionary
        data.append(asdict(item))  # Replace with the actual method to get a dictionary representation

    df = pd.DataFrame(data)

    logger.debug("DataFrame of all Jgh best power curves:")
    logger.debug(df)
    OUTPUT_FILENAME = "sexy_spreadsheet_of_all_Jgh_best_power_curves.xlsx"
    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)
    logger.info(f"Test passed. Filtered DataFrame saved to {OUTPUT_DIRPATH}{OUTPUT_FILENAME}")


if __name__ == "__main__":
    # configure root logging since this is the entry point
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")

    ZWIFT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwift/"
    ZWIFTRACINGAPP_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftracing-app-post/"
    ZWIFTPOWER_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/power-graph-watts/"
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"

    # Comment/uncomment the lines below to run the tests you want. for more verbose output, set log_level to logging.DEBUG

    # main03()
    # main04()
    # main05()
    # main06()

    # main11()
    # main12()
    # main13()
    # main14()
    main15()
    # main16()
