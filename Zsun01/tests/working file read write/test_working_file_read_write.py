from pathlib import Path

from storage_config import (
    FILENAME_RIDER_COMPUTE_DTO_JSON_DICT,
    DIRPATH_ZWIFT_FILES,
    # DIRPATH_ZWIFTPOWER_PROFILE_PAGE,
    DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
    DIRPATH_ZWIFTRACINGAPP_FILES,
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
)
from test_zwiftid_file_reader_sync import test04
from working_file_read_write import read_rider_compute_dict_from_json
from zwiftid_file_reader_sync import (
    read_zwiftdto_files_to_item_dict_sync,
    read_zwiftracingappdto_files_to_item_dict_sync,
    read_zwiftpower90daywattsdto_files_to_item_dict_sync,
)

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


#tests
def test01():

    all_riders = read_rider_compute_dict_from_json(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),FILENAME_RIDER_COMPUTE_DTO_JSON_DICT)

    print(f"Imported {len(all_riders)} zsun riders from VS2022 python project file.")



def test03():

    dict_of_zwiftItem = dict(read_zwiftdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFT_FILES),None))
    dict_of_zwiftracingappItem = dict(read_zwiftracingappdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTRACINGAPP_FILES), None))
    dict_of_zwiftpower90dayItem = dict(read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), None))

    print(f"Imported {len(dict_of_zwiftItem)} zwift profile items")
    print (f"Imported {len(dict_of_zwiftracingappItem)} zwiftracingapp profile items")
    print(f"Imported {len(dict_of_zwiftpower90dayItem)} zwiftpower 90-day best graph items")

def test04():
    dict_of_zwiftItem = dict(read_zwiftdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFT_FILES),None))
    print(f"Imported {len(dict_of_zwiftItem)} zwift profile items")

    for zwift_id, item in dict_of_zwiftItem.items():
        print(f"Key: {zwift_id}, Zwift ID: {item.zwift_id}, Name: {item.last_name}, Achievement Level: {item.achievement_level}")

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        print("Starting tests...be patient, this may take a while, thousands of files to process...\n")
        # test01()
        # test03()
        test04()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error. Check the logs for possible feedback.\n")

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



