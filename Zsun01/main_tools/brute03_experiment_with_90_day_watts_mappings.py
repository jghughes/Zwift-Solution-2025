"""
Debugging and Testing Tool for ZwiftPower 90-Day Power Graph Extraction

This script is intended for development use with a small dataset. Its purpose is to extract and process the best power data from the nested structure of ZwiftPowerItems, converting them into a format compatible with the Brute pipeline. The output is manually inspected via the generated JSON file to ensure correctness and compatibility.

Key Features:
- Extracts and processes ZwiftPowerItems from input data, mapping them to ZwiftPowerFlattened90dayWattsItem objects.
- Flattens each rider's power graph (critical power values for 99 durations, 1-7200 seconds) into named properties for easier downstream processing.
- Validates and loads rider profiles and best-power-graph data using pydantic DTOs.
- Processes a subset of rider IDs (e.g., BetelIDs or any test group) and generates display names for logging.
- Writes the cleaned, processed data to a new JSON file keyed by ZwiftID.

Workflow:
1. Configure logging for the application.
2. Load all rider profiles from a JSON file into a dictionary.
3. Retrieve a subset of rider IDs to process.
4. For each rider:
   - Validate and map their best-power-graph data file to ZwiftPowerFlattened90dayWattsItem.
   - Insert the ZwiftID and generate a display name for logging.
5. Write the processed data for all riders to a new JSON file in the output directory.

This script demonstrates:
- Reading and writing JSON data using pydantic DTOs.
- Mapping between dataclasses and DTOs.
- Use of file and string utility functions for validation and display.
"""
from pathlib import Path
from zwiftid_file_reader_sync import read_zwiftpower90daywattsdto_files_to_item_dict_sync
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_string import make_short_displayname
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES
from storage_config import FILENAME_RIDER_COMPUTE_DTO_JSON_DICT

from storage_config import DIRPATH_RUBBISH_SCRATCHPAD
from working_file_read_write import (
    read_rider_compute_dict_from_json,
    write_zwiftpower_90day_watts_dict_to_json,
)
from repository_of_team_rosters import RepositoryOfTeamRosters


import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def experiment_with_90_day_watts_mappings():

    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), Path(DIRPATH_RUBBISH_SCRATCHPAD)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_COMPUTE_DTO_JSON_DICT,_output_filename])
    except Exception as err:
        print(err)
        return

    all_rider_items_as_dict = read_rider_compute_dict_from_json(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),FILENAME_RIDER_COMPUTE_DTO_JSON_DICT)
    print(f"loaded RiderItems for {len(all_rider_items_as_dict)} riders")
    test_IDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)
    print(f"loaded {len(test_IDs)} IDs for our little test")
    dict_of_zwiftpower_90day_watts_items = read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES),test_IDs)
    print(f"loaded zwiftpower_graph_watts files for {len(dict_of_zwiftpower_90day_watts_items)} testIDs")

    # function to make nick-names for display purposes for each rider
    for rider_id, rider_watts_graph in dict_of_zwiftpower_90day_watts_items.items():
        rider_watts_graph.zwift_id = rider_id # write filename into zwiftId field
        display_name = make_short_displayname(all_rider_items_as_dict[rider_id].name) # add short name
        print(f"{rider_id} {display_name}")

    write_zwiftpower_90day_watts_dict_to_json(Path(DIRPATH_RUBBISH_SCRATCHPAD), _output_filename, dict_of_zwiftpower_90day_watts_items)

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:
        team_name = "scratchpad"
        _output_filename = "extracted_input_power_graphs_for_testIDs.json"
        experiment_with_90_day_watts_mappings()

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





