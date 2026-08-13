from dataclasses import asdict
from pathlib import Path

import pandas as pd

from jgh_read_write import write_dataframe_as_xlsx_file
from repository_of_riders import RepositoryOfRiders

from storage_config import (
    DIRPATH_ZWIFT_FILES,
    DIRPATH_ZWIFTRACINGAPP_FILES,
    DIRPATH_ZWIFTPOWER,
    DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    DIRPATH_RUBBISH_SCRATCHPAD
)
import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING 

# Tests
def test09():
    # repository = RepositoryOfRiders()
    # repository.populate_repository(
    #     [],
    #     zwift_dir_path=DIRPATH_ZWIFT_FILES,
    #     zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
    #     zwiftpower_dir_path=DIRPATH_ZWIFTPOWER,
    #     zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    #     filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched=""
    # )
    print(f"Test09: There are {len(repository.get_dict_of_RiderComputeItem_by_ids(None))} active racers.")

def test11():
    # repository = RepositoryOfRiders()
    # repository.populate_repository(
    #     file_names=None,
    #     zwift_dir_path=DIRPATH_ZWIFT_FILES,
    #     zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
    #     zwiftpower_dir_path=DIRPATH_ZWIFTPOWER,
    #     zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    #     filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched=""
    # )

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

    # Example: get the union - should be more than 1500
    df = repository._create_union_of_sets_as_dataframe([], [])
    # print("DataFrame of union of Zwift IDs in all datasets including samples:")
    # print(df)
    output_filename = "beautiful_union_of_everything.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename, df)

    # Example: get the intersection - should be about 80
    df = repository._create_intersection_of_sets_as_dataframe([], [])
    # print("DataFrame of intersection of Zwift IDs in main datasets:")
    # print(df)
    OUTPUT_FILENAME2 = "beautiful_intersection_of_main_datasets.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), OUTPUT_FILENAME2, df)


    # Example: get an intersection of all main sets and betel - should be tiny - 4
    df = repository._create_intersection_of_sets_as_dataframe(betel, [])
    # print("DataFrame of intersection of Zwift IDs in all datasets and Betel:")
    # print(df)
    OUTPUT_FILENAME3 = "beautiful_intersection_of_main_datasets_and_betel.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), OUTPUT_FILENAME3, df)

def test12():
    # repository = RepositoryOfRiders()

    # # Populate the repository with data
    # repository.populate_repository(
    #     file_names=None,
    #     zwift_dir_path=DIRPATH_ZWIFT_FILES,
    #     zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
    #     zwiftpower_dir_path=DIRPATH_ZWIFTPOWER,
    #     zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    #     filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched=""
    # )

    # Define any test parameters for _create_union_of_sets_filtered_by_membership_as_dataframe
    zwift_filter = "y" 
    racingapp_filter = "y"
    zwiftpower_filter = "y_or_n"
    zwiftpower_90day_cp_filter = "y"

    # Call the _create_union_of_sets_filtered_by_membership_as_dataframe method
    filtered_df = repository._create_union_of_sets_filtered_by_membership_as_dataframe(
        zwift=zwift_filter,
        racingapp=racingapp_filter,
        zwiftpower=zwiftpower_filter,
        zwiftpower_90day_cp=zwiftpower_90day_cp_filter
    )

    # Display the filtered DataFrame
    # print("Filtered DataFrame:")
    # print(filtered_df)

    # Validate the test results
    # Check if the DataFrame is not empty
    assert not filtered_df.empty, "Filtered DataFrame is empty, but it probably shouldn't be (although not definitely)."

    # Optionally, save the filtered DataFrame to an Excel file for verification
    output_filename = "beautiful_matching_specified_boolean_filter_criteria.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename, filtered_df)
    print(f"Test passed. Filtered DataFrame saved to {Path(DIRPATH_RUBBISH_SCRATCHPAD)}{output_filename}")

def test13():
    """
    Test function that loads all Zwift profile data, converts it to a
    pandas DataFrame, and saves the result to an Excel file.

    Unlike other test functions, this one focuses only on Zwift profile
    data, not ZwiftRacingApp, ZwiftPower, or best power curve data.

    No arguments. No return value. Results are written to an Excel file.
    """

    # # Initialize the repository
    # repository = RepositoryOfRiders()

    # # Populate the repository with data
    # repository.populate_repository(
    #     [],
    #     zwift_dir_path=DIRPATH_ZWIFT_FILES,
    #     zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
    #     zwiftpower_dir_path=DIRPATH_ZWIFTPOWER,
    #     zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    #     filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched=""
    # )

    dict_of_items = repository.get_dict_of_ZwiftItem_by_ids([])
    print(f"Zwift profiles: {len(dict_of_items.items())}\n")
    items = list(dict_of_items.values())
    data = []
    for item in items:
        data.append(asdict(item))

    df = pd.DataFrame(data)
    output_filename = "sexy_spreadsheet_of_all_Zwift_profiles.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename, df)
    print(f"Test passed. Filtered DataFrame saved to {Path(DIRPATH_RUBBISH_SCRATCHPAD)}{output_filename}")

def test14():
    """
    Test function that loads all ZwiftRacingApp profile data, converts it
    to a pandas DataFrame, and saves the result to an Excel file.

    Unlike other test functions, this one focuses only on ZwiftRacingApp
    data, not Zwift, ZwiftPower, or best power curve data.

    No arguments. No return value. Results are written to an Excel file.
    """
    # repository = RepositoryOfRiders()
    # repository.populate_repository(
    #     None,
    #     zwift_dir_path=DIRPATH_ZWIFT_FILES,
    #     zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
    #     zwiftpower_dir_path=DIRPATH_ZWIFTPOWER,
    #     zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    #     filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched=""
    # )

    dict_of_items = repository.get_dict_of_ZwiftRacingAppItem_by_ids([])
    print(f"ZwiftRacingApp profiles: {len(dict_of_items.items())}\n")
    items = list(dict_of_items.values())
    data = []
    for item in items:
        data.append(asdict(item))
    df = pd.DataFrame(data)
    output_filename = "sexy_spreadsheet_of_all_ZwiftRacingApp_profiles.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename, df)
    print(f"Test passed. Filtered DataFrame saved to {Path(DIRPATH_RUBBISH_SCRATCHPAD)}{output_filename}")

def test16():
    """
    Test function that loads all ZwiftPower best power curve data, converts
    it to a pandas DataFrame, and saves the result to an Excel file.

    Unlike other test functions, this one focuses only on best power curve
    data, not Zwift, ZwiftPower, or ZwiftRacingApp profiles.

    No arguments. No return value. Results are written to an Excel file.
    """
    # repository = RepositoryOfRiders()
    # repository.populate_repository(
    #     None,
    #     zwift_dir_path=DIRPATH_ZWIFT_FILES,
    #     zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
    #     zwiftpower_dir_path=DIRPATH_ZWIFTPOWER,
    #     zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    #     filepath_snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched=""
    # )

    dict_of_items = repository.get_dict_of_ZwiftPower90dayWattsItem_by_ids([])
    print(f"Jgh best power curves: {len(dict_of_items.items())}\n")

    #convert to dict to list of values
    items = list(dict_of_items.values())

    # Create a DataFrame from the list of velo files
    data = []
    for item in items:
        
        data.append(asdict(item))

    df = pd.DataFrame(data)

    print("DataFrame of all Jgh best power curves:")
    # print(df)
    output_filename = "sexy_spreadsheet_of_all_Jgh_best_power_curves.xlsx"
    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename, df)
    print(f"Test passed. Filtered DataFrame saved to {Path(DIRPATH_RUBBISH_SCRATCHPAD)}{output_filename}")


#main runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        repository = RepositoryOfRiders()
        repository.populate_repository(
            [],
            zwift_dir_path=DIRPATH_ZWIFT_FILES,
            zwiftracingapp_dir_path=DIRPATH_ZWIFTRACINGAPP_FILES,
            zwiftpower_90day_graph_watts_dir_path=DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
            snapshot_of__RiderStatsItems_when_accelerated_levelling_up_launched_filepath=""
        )

        start_time = time.time()  
        print("Starting tests...\n")
        # test09()
        # test11()
        # test12()
        # test13()
        # test14() 
        test16()
        print("\nTests complete.")
        end_time = time.time()

        success_msg = f"Success: Main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(logger, message=alert_err.message, level=logging.INFO, exception=alert_err)
        print(f"{alert_err.message}\n")
    except Exception as ex:
        log_event(logger, message=f"Unhandled Exception: {ex}", level=logging.ERROR, exception=ex)  # Pass the original exception object
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")
