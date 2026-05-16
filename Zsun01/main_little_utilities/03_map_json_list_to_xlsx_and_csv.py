from pathlib import Path

from rider_stats_dto import RiderStatsDtoListModel

from working_file_read_write import read_json_list_and_export_tabular

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


#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        print("Starting script...be patient, this may or may not take a while...\n")
        main01()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. Script executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. Script executed without error. Check the logs for possible feedback.\n")

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



