from cyclic_matrix import generate_cyclic_matrix
from rider_compute_item import RiderComputeItem
from pathlib import Path
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_COMPUTE_DTO_JSON_DICT
from working_file_read_write import read_rider_compute_dict_from_json

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

# Example usage:
def test00():

    dict_of_zwiftrideritem = read_rider_compute_dict_from_json(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), FILENAME_RIDER_COMPUTE_DTO_JSON_DICT)

    barryb : RiderComputeItem = dict_of_zwiftrideritem['5490373'] # barryb
    johnh : RiderComputeItem = dict_of_zwiftrideritem['1884456'] # johnh
    lynseys : RiderComputeItem = dict_of_zwiftrideritem['383480'] # lynseys

    riders = [barryb, johnh, lynseys]

    matrix = generate_cyclic_matrix(riders)

    for row in matrix:
        print([rider.name for rider in row])


#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        test00()

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


