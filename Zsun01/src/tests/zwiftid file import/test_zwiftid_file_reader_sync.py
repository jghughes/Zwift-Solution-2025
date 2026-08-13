from pathlib import Path

from storage_config import DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES
from zwiftid_named_file_reader import (
    read_zwiftdto_files_to_item_dict_sync, read_zwiftracingappdto_files_to_item_dict_sync,
    read_zwiftpower90daywattsdto_files_to_item_dict_sync
)
import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


# Tests

def test03():
    my_dict = read_zwiftdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFT_FILES), None)
    for zwift_id, item in my_dict.items():
        if not item:
            log_event(
                logger,
                message=f"Profile for zwiftid = {zwift_id} is missing.",
                level=logging.ERROR
            )
            print(f"Profile for zwiftid = {zwift_id} is missing.")
        else:
            print(f"{zwift_id} {item.last_name} zFTP = {round(item.ftp_on_zwift)} Watts, Height = {round(item.height_mm/10.0)} cm Level = {item.achievement_level}")
    log_event(
        logger,
        message=f"Imported {len(my_dict)} zwift_files",
        level=logging.INFO
    )
    print(f"\nHard drive has {len(my_dict)} zwift_files")

def test04():
    my_dict = read_zwiftracingappdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTRACINGAPP_FILES), None)
    for zwift_id, item in my_dict.items():
        if not item:
            log_event(
                logger,
                message=f"Item for zwiftid = {zwift_id} is missing.",
                level=logging.INFO,
                exception=AlertMessageError(message=f"Item for zwiftid = {zwift_id} is missing.")
            )
            print(f"Item for zwiftid = {zwift_id} is missing.")
        else:
            print(f"{zwift_id} {item.full_name} country = {item.country_code2}")
    log_event(
        logger,
        message=f"Imported {len(my_dict)} zwiftracingapp_files",
        level=logging.INFO
    )
    print(f"\nHard drive has {len(my_dict)} zwiftracingapp_files")


def test06():
    my_dict = read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), None)
    for zwift_id, item in my_dict.items():
        if not item:
            log_event(
                logger,
                message=f"Item for zwiftid = {zwift_id} is missing.",
                level=logging.INFO,
                exception=AlertMessageError(message=f"Item for zwiftid = {zwift_id} is missing.")
            )
            print(f"Item for zwiftid = {zwift_id} is missing.")
        else:
            print(f"{zwift_id} cp60 = {item.bp_60}")
    log_event(
        logger,
        message=f"Imported {len(my_dict)} zwiftpower_graph_watts_files",
        level=logging.INFO
    )
    print(f"\nHard drive has {len(my_dict)} zwiftpower_graph_watts_files")

#main runner
if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        start_time = time.time()
        print("Starting tests...\n")
        test03()
        # test04()
        # test06()
        print("\nfinished tests")
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



