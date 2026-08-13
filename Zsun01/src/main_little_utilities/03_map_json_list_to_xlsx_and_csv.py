from pathlib import Path

from rider_stats_dto import RiderStatsDtoListModel

from custom_file_read_write import read_json_list_and_export_tabular

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


#tests
def main01():

    dirpath_input : Path = Path(r"C:\Users\johng\holding_pen\StuffForZsun\!StuffFromDaveK_byJgh\special")
    filename : str = r"2026-05-03_rider_stats_dto_as_list_four_days_after_accelerated_levelling_up_introduced.json"

    dirpath_output = dirpath_input

    dataframe_outcome = read_json_list_and_export_tabular(dirpath_input, filename, RiderStatsDtoListModel, dirpath_output)

    print(f"Imported: {len(dataframe_outcome)} zsun riders")
    print(f"Imported: JSON file {filename}.")
    print(f"Exported: Excel and CSV in the same directory as the source JSON file: {dirpath_output}\n\n")


#main runner
if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        print("Starting script...be patient, this may or may not take a while...\n")

        start_time = time.time()
        main01()
        end_time = time.time()

        success_msg = f"Success: main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(logger, message=alert_err.message, level=logging.INFO, exception=alert_err)
        print(f"\n{alert_err.message}\n")
    except Exception as ex:
        log_event(logger, message=f"Unhandled Exception: {ex}", level=logging.ERROR, exception=ex) # Pass the original exception object
        print(f"\nUnhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n\n")

