
from dataclasses import dataclass, field 
from collections import defaultdict
from handy_utilities import *
from zwift_profile_dto import ZwiftProfileDTO
from zwiftracingapp_profile_dto import ZwiftRacingAppProfileDTO
from zwiftpower_profile_dto import ZwiftPowerProfileDTO
from zsun_rider_item import ZwiftPower90DayBestGraphItem
import pandas as pd
from jgh_read_write import raise_exception_if_invalid


@dataclass
class ScrapedZwiftDataRepository:
    
    def __init__(self):
        self.dict_of_zwift_profileDTO: defaultdict[str, ZwiftProfileDTO] = field(default_factory=lambda: defaultdict(ZwiftProfileDTO))
        self.dict_of_zwiftracingapp_profileDTO: defaultdict[str, ZwiftRacingAppProfileDTO] = field(default_factory=lambda: defaultdict(ZwiftRacingAppProfileDTO))
        self.dict_of_zwiftpower_profileDTO: defaultdict[str, ZwiftPowerProfileDTO] = field(default_factory=lambda: defaultdict(ZwiftPowerProfileDTO))
        self.dict_of_zwiftpower_90daybest_graph_item: defaultdict[str, ZwiftPower90DayBestGraphItem] = field(default_factory=lambda: defaultdict(ZwiftPower90DayBestGraphItem))

    def populate_repository(
        self,
        riderIDs: Optional[list[str]],
        zwift_profile_dir_path: str,
        zwiftracingapp_profile_dir_path: str,
        zwiftpower_profile_dir_path: str,
        zwiftpower_90daybest_dir_path: str
    ):
        self.dict_of_zwift_profileDTO               = read_many_zwift_profile_files_in_folder(riderIDs, zwift_profile_dir_path)
        self.dict_of_zwiftracingapp_profileDTO      = read_many_zwiftracingapp_profile_files_in_folder(riderIDs, zwiftracingapp_profile_dir_path)
        self.dict_of_zwiftpower_profileDTO          = read_many_zwiftpower_profile_files_in_folder(riderIDs, zwiftpower_profile_dir_path)
        self.dict_of_zwiftpower_90daybest_graph_item = read_many_zwiftpower_critical_power_graph_files_in_folder(riderIDs, zwiftpower_90daybest_dir_path)

    def get_dataframe_of_zwiftid_commonality(self, sample1: list[str], sample2: list[str]) -> pd.DataFrame:
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

        # Step 2: Create a superset of all Zwift IDs
        superset_of_zwiftID = set(sample1) | set(sample2) | \
                              set(self.dict_of_zwift_profileDTO.keys()) | \
                              set(self.dict_of_zwiftracingapp_profileDTO.keys()) | \
                              set(self.dict_of_zwiftpower_profileDTO.keys()) | \
                              set(self.dict_of_zwiftpower_90daybest_graph_item.keys())

        # Optional: Log the size of the superset for debugging
        logger.info(f"Total unique Zwift IDs in superset: {len(superset_of_zwiftID)}")

        # Step 3: Populate the answer list
        for key in superset_of_zwiftID:
            row = (
                key,  # col 0: zwiftID
                "y" if key in sample1 else "n",  # col 1: in_sample1
                "y" if key in sample2 else "n",  # col 2: in_sample2
                "y" if key in self.dict_of_zwift_profileDTO.keys() else "n",  # col 3: in_zwift_profiles
                "y" if key in self.dict_of_zwiftracingapp_profileDTO.keys() else "n",  # col 4: in_zwiftracingapp_profiles
                "y" if key in self.dict_of_zwiftpower_profileDTO.keys() else "n",  # col 5: in_zwiftpower_profiles
                "y" if key in self.dict_of_zwiftpower_90daybest_graph_item.keys() else "n",  # col 6: in_zwiftpower_90daybest_graphs
            )
            answer.append(row)

        # Step 4: Create a pandas DataFrame
        df = pd.DataFrame(
            answer,
            columns=[
                "zwiftID",
                "in_sample1",
                "in_sample2",
                "in_zwift_profiles",
                "in_zwiftracingapp_profiles",
                "in_zwiftpower_profiles",
                "in_zwiftpower_90daybest_graphs",
            ],
        )

        # Return the DataFrame
        return df

    def get_dataframe_of_zwiftid_common_to_all(self, sample1: list[str], sample2: list[str]) -> pd.DataFrame:
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
        sets_to_check = [
            set(self.dict_of_zwift_profileDTO.keys()),
            set(self.dict_of_zwiftracingapp_profileDTO.keys()),
            set(self.dict_of_zwiftpower_profileDTO.keys()),
            set(self.dict_of_zwiftpower_90daybest_graph_item.keys())
        ]

        # Include sample1 and sample2 in the criterion only if they are not empty
        if sample1:
            sets_to_check.append(set(sample1))
        if sample2:
            sets_to_check.append(set(sample2))

        # Step 2: Find Zwift IDs common to all datasets
        common_zwiftIDs = set.intersection(*sets_to_check)

        # Step 3: Populate the answer list
        answer: list[tuple[str, str, str, str, str, str, str]] = []
        for key in common_zwiftIDs:
            row = (
                key,  # col 0: zwiftID
                "y" if key in sample1 else "n",  # col 1: in_sample1
                "y" if key in sample2 else "n",  # col 2: in_sample2
                "y" if key in self.dict_of_zwift_profileDTO.keys() else "n",  # col 3: in_zwift_profiles
                "y" if key in self.dict_of_zwiftracingapp_profileDTO.keys() else "n",  # col 4: in_zwiftracingapp_profiles
                "y" if key in self.dict_of_zwiftpower_profileDTO.keys() else "n",  # col 5: in_zwiftpower_profiles
                "y" if key in self.dict_of_zwiftpower_90daybest_graph_item.keys() else "n",  # col 6: in_zwiftpower_90daybest_graphs
            )
            answer.append(row)

        # Step 4: Create a pandas DataFrame
        df = pd.DataFrame(
            answer,
            columns=[
                "zwiftID",
                "in_sample1",
                "in_sample2",
                "in_zwift_profiles",
                "in_zwiftracingapp_profiles",
                "in_zwiftpower_profiles",
                "in_zwiftpower_90daybest_graphs",
            ],
        )

        # Return the DataFrame
        return df

    def save_pretty_dataframe_of_zwiftid_commonality_to_excel(self, df: pd.DataFrame, file_name: str, dir_path : str):
           # Validate the file name
            if not file_name or not file_name.endswith(".xlsx"):
                raise ValueError(f"Invalid file name: '{file_name}'. Ensure it ends with '.xlsx'.")

            # # Validate the directory path
            raise_exception_if_invalid(dir_path, file_name, ".xlsx", must_read_not_write=False)

            # Process the "in_sample1" and "in_sample2" columns
            df["in_sample1"] = df["in_sample1"].replace("n", "")
            df["in_sample2"] = df["in_sample2"].replace("n", "")

            # Process all remaining columns
            remaining_columns = [col for col in df.columns if col not in ["in_sample1", "in_sample2"]]
            for col in remaining_columns:
                df[col] = df[col].replace("y", "")

            # Save the processed DataFrame to an Excel file
            output_path = os.path.join(dir_path, file_name)
            df.to_excel(output_path, index=False, engine="openpyxl")
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
    sample1 = ["12345", "67890", "11223"]
    sample2 = ["67890", "44556", "77889"]

    # Call the method to get the DataFrame of Zwift IDs common to all datasets
    df_common_to_all = rep.get_dataframe_of_zwiftid_common_to_all(sample1, sample2)

    # Display the resulting DataFrame
    print("DataFrame of Zwift IDs common to all datasets:")
    print(df_common_to_all)

    # Optionally, save the DataFrame to an Excel file for verification
    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    OUTPUT_FILENAME = "zwiftid_common_to_all.xlsx"
    rep.save_pretty_dataframe_of_zwiftid_commonality_to_excel(df_common_to_all, OUTPUT_FILENAME, OUTPUT_DIRPATH)


if __name__ == "__main__":
    main()
