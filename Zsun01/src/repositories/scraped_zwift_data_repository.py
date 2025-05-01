
from dataclasses import dataclass, field 
from collections import defaultdict
from handy_utilities import *
from zwift_profile_item import ZwiftProfileItem
from zwiftracingapp_profile_item import ZwiftRacingAppProfileItem
from zwiftpower_profile_item import ZwiftPowerProfileItem
from zwiftpower_90day_bestpower_item import ZwiftPower90DayBestPowerItem
import pandas as pd
import numpy as np
from jgh_read_write import raise_exception_if_invalid


@dataclass
class ScrapedZwiftDataRepository:
    # Class constants for DataFrame column names
    COL_ZWIFT_ID = "zwiftID"
    COL_IN_SAMPLE1 = "in_sample1"
    COL_IN_SAMPLE2 = "in_sample2"
    COL_IN_ZWIFT_PROFILES = "in_zwift_profiles"
    COL_IN_ZWIFTRACINGAPP_PROFILES = "in_zwiftracingapp_profiles"
    COL_IN_ZWIFTPOWER_PROFILES = "in_zwiftpower_profiles"
    COL_IN_ZWIFTPOWER_90DAYBEST_GRAPHS = "in_zwiftpower_90daybest_graphs"
 
    def __init__(self):
        self.dict_of_zwift_profileitem: defaultdict[str, ZwiftProfileItem] = field(default_factory=lambda: defaultdict(ZwiftProfileItem))
        self.dict_of_zwiftracingapp_profileitem: defaultdict[str, ZwiftRacingAppProfileItem] = field(default_factory=lambda: defaultdict(ZwiftRacingAppProfileItem))
        self.dict_of_zwiftpower_profileitem: defaultdict[str, ZwiftPowerProfileItem] = field(default_factory=lambda: defaultdict(ZwiftPowerProfileItem))
        self.dict_of_zwiftpower_90daybest_graph_item: defaultdict[str, ZwiftPower90DayBestPowerItem] = field(default_factory=lambda: defaultdict(ZwiftPower90DayBestPowerItem))

    def populate_repository(
        self,
        riderIDs: Optional[list[str]],
        zwift_profile_dir_path: str,
        zwiftracingapp_profile_dir_path: str,
        zwiftpower_profile_dir_path: str,
        zwiftpower_90daybest_dir_path: str
    ):
        self.dict_of_zwift_profileitem               = read_many_zwift_profile_files_in_folder(riderIDs, zwift_profile_dir_path)
        self.dict_of_zwiftracingapp_profileitem      = read_many_zwiftracingapp_profile_files_in_folder(riderIDs, zwiftracingapp_profile_dir_path)
        self.dict_of_zwiftpower_profileitem          = read_many_zwiftpower_profile_files_in_folder(riderIDs, zwiftpower_profile_dir_path)
        self.dict_of_zwiftpower_90daybest_graph_item = read_many_zwiftpower_bestpower_files_in_folder(riderIDs, zwiftpower_90daybest_dir_path)

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
                              set(self.dict_of_zwift_profileitem.keys()) | \
                              set(self.dict_of_zwiftracingapp_profileitem.keys()) | \
                              set(self.dict_of_zwiftpower_profileitem.keys()) | \
                              set(self.dict_of_zwiftpower_90daybest_graph_item.keys())

        # Optional: Log the size of the superset for debugging
        logger.info(f"Total unique Zwift IDs in superset: {len(superset_of_zwiftID)}")

        # Step 3: Populate the answer list
        for key in superset_of_zwiftID:
            row = (
                key,  # col 0: zwiftID
                "y" if key in sample1 else "n",  # col 1: in_sample1
                "y" if key in sample2 else "n",  # col 2: in_sample2
                "y" if key in self.dict_of_zwift_profileitem.keys() else "n",  # col 3: in_zwift_profiles
                "y" if key in self.dict_of_zwiftracingapp_profileitem.keys() else "n",  # col 4: in_zwiftracingapp_profiles
                "y" if key in self.dict_of_zwiftpower_profileitem.keys() else "n",  # col 5: in_zwiftpower_profiles
                "y" if key in self.dict_of_zwiftpower_90daybest_graph_item.keys() else "n",  # col 6: in_zwiftpower_90daybest_graphs
            )
            answer.append(row)

        answer.sort(key=lambda x: x[0])  # Sort by the first element (zwiftID)

        df = pd.DataFrame(answer, columns=[
                self.COL_ZWIFT_ID,
                self.COL_IN_SAMPLE1,
                self.COL_IN_SAMPLE2,
                self.COL_IN_ZWIFT_PROFILES,
                self.COL_IN_ZWIFTRACINGAPP_PROFILES,
                self.COL_IN_ZWIFTPOWER_PROFILES,
                self.COL_IN_ZWIFTPOWER_90DAYBEST_GRAPHS,
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
        zwift_profiles = list(self.dict_of_zwift_profileitem.keys())
        zwiftracingapp_profiles = list(self.dict_of_zwiftracingapp_profileitem.keys())
        zwiftpower_profiles = list(self.dict_of_zwiftpower_profileitem.keys())
        zwiftpower_90daybest_graphs = list(self.dict_of_zwiftpower_90daybest_graph_item.keys())
        
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
                "y" if key in self.dict_of_zwift_profileitem.keys() else "n",  # col 3: in_zwift_profiles
                "y" if key in self.dict_of_zwiftracingapp_profileitem.keys() else "n",  # col 4: in_zwiftracingapp_profiles
                "y" if key in self.dict_of_zwiftpower_profileitem.keys() else "n",  # col 5: in_zwiftpower_profiles
                "y" if key in self.dict_of_zwiftpower_90daybest_graph_item.keys() else "n",  # col 6: in_zwiftpower_90daybest_graphs
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

    def get_filtered_table_of_intersections_of_sets(
        self, 
        zwift: str, 
        racingapp: str, 
        zwiftpower: str, 
        zwiftpower_90day_cp: str
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
            self.COL_IN_ZWIFT_PROFILES: zwift,
            self.COL_IN_ZWIFTRACINGAPP_PROFILES: racingapp,
            self.COL_IN_ZWIFTPOWER_PROFILES: zwiftpower,
            self.COL_IN_ZWIFTPOWER_90DAYBEST_GRAPHS: zwiftpower_90day_cp,
        }

  
        # apply the filter
        filtered_df = df_superset[
            df_superset.apply(lambda row: matches_template(row, template), axis=1)
        ]

        # return the filtered DataFrame
        return filtered_df

    def save_dataframe_to_excel(self, df: pd.DataFrame, file_name: str, dir_path : str):
           # Validate the file name
            if not file_name or not file_name.endswith(".xlsx"):
                raise ValueError(f"Invalid file name: '{file_name}'. Ensure it ends with '.xlsx'.")

            # # Validate the directory path
            raise_exception_if_invalid(dir_path, file_name, ".xlsx", must_read_not_write=False)

            # # Process the "in_sample1" and "in_sample2" columns
            # df["in_sample1"] = df["in_sample1"].replace("n", "")
            # df["in_sample2"] = df["in_sample2"].replace("n", "")

            # # Process all remaining columns
            # remaining_columns = [col for col in df.columns if col not in ["in_sample1", "in_sample2"]]
            # for col in remaining_columns:
            #     df[col] = df[col].replace("y", "")

            # Save the processed DataFrame to an Excel file
            output_path = os.path.join(dir_path, file_name)
            df.to_excel(output_path)
            # df.to_excel(output_path, index=False, engine="openpyxl")
            # df.to_excel(output_path, index=False, engine="openpyxl")
            logger.info(f"DataFrame saved to: {os.path.join(dir_path, file_name)}")


def main():
    # Define paths for testing
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    # Initialize the repository
    rep = ScrapedZwiftDataRepository()

    # Populate the repository with data
    rep.populate_repository(
        riderIDs=None,
        zwift_profile_dir_path=ZWIFT_PROFILES_DIRPATH,
        zwiftracingapp_profile_dir_path=ZWIFTRACINGAPP_PROFILES_DIRPATH,
        zwiftpower_profile_dir_path=ZWIFTPOWER_PROFILES_DIRPATH,
        zwiftpower_90daybest_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
    )

    # Define sample Zwift IDs for testing
    sample1 = ["3147366", "11526"] # daveK and scottM
    sample2 = [
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

    # get the superset - should be more than 1500
    df = rep.get_table_of_superset_of_sets_by_id(sample1, sample2)

    # Display the resulting DataFrame
    print("DataFrame of superset of Zwift IDs in all datasets including samples:")
    print(df)

    # Optionally, save the DataFrame to an Excel file for verification
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    OUTPUT_FILENAME = "beautiful_superset_of_zwiftids_in__all_datasets_including_samples.xlsx"
    rep.save_dataframe_to_excel(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)

    # Call the method to get the DataFrame of the intersection of datasets - should be tiny
    df = rep.get_table_of_intersections_of_sets(sample1, sample2)

    # Display the resulting DataFrame
    print("DataFrame of intesection of Zwift IDs in all datasets including samples:")
    print(df)

    # Optionally, save the DataFrame to an Excel file for verification
    OUTPUT_FILENAME2 = "beautiful_intersection_of_zwiftids_in__all_datasets_including_samples.xlsx"
    rep.save_dataframe_to_excel(df, OUTPUT_FILENAME2, OUTPUT_DIRPATH)









def main2():
    # Initialize the repository
    rep = ScrapedZwiftDataRepository()

    # Populate the repository with mock data (adjust paths as needed for your environment)
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    rep.populate_repository(
        riderIDs=None,
        zwift_profile_dir_path=ZWIFT_PROFILES_DIRPATH,
        zwiftracingapp_profile_dir_path=ZWIFTRACINGAPP_PROFILES_DIRPATH,
        zwiftpower_profile_dir_path=ZWIFTPOWER_PROFILES_DIRPATH,
        zwiftpower_90daybest_dir_path=ZWIFTPOWER_GRAPHS_DIRPATH,
    )

    # Define any test parameters for get_filtered_table_of_intersections_of_sets
    zwift_filter = "y" 
    racingapp_filter = "y"
    zwiftpower_filter = "y"
    zwiftpower_90day_cp_filter = "y"

    # Call the get_filtered_table_of_intersections_of_sets method
    filtered_df = rep.get_filtered_table_of_intersections_of_sets(
        zwift=zwift_filter,
        racingapp=racingapp_filter,
        zwiftpower=zwiftpower_filter,
        zwiftpower_90day_cp=zwiftpower_90day_cp_filter
    )

    # Display the filtered DataFrame
    print("Filtered DataFrame:")
    print(filtered_df)

    # Validate the test results
    # Check if the DataFrame is not empty
    assert not filtered_df.empty, "Filtered DataFrame is empty, but it probably shouldn't be (although not definitely)."

    # Optionally, save the filtered DataFrame to an Excel file for verification
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    OUTPUT_FILENAME = "zwiftid_matching_specified_boolean_filter_criteria.xlsx"
    rep.save_dataframe_to_excel(filtered_df, OUTPUT_FILENAME, OUTPUT_DIRPATH)

    print(f"Test passed. Filtered DataFrame saved to {OUTPUT_DIRPATH}{OUTPUT_FILENAME}")


if __name__ == "__main__":
    main()

    # main2()
