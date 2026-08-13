# from jgh_cyclic_matrix import generate_cyclic_matrix
from rider_compute_item import RiderComputeItem
from pathlib import Path
from typing import List
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_COMPUTE_DTO_JSON_DICT
from custom_file_read_write import read_rider_compute_dict_from_json

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

#   this is a method to test the cyclic formula used 
#   for determining the order of riders in a rotating paceline.
#   see populate_rider_work_assignments() in jgh_formulae04.py

def generate_cyclic_matrix(riders: List[RiderComputeItem]) -> List[List[RiderComputeItem]]:
    """
    Generates a cyclic matrix where each column is a cyclic permutation of the first_name column.

    Args:
        riders (List[RiderComputeItem]): A list of RiderComputeItem objects.

    Returns:
        List[List[RiderComputeItem]]: A 2D list representing the cyclic matrix.

    The function uses the provided list of RiderComputeItem objects to create the initial column.
    It then generates each subsequent column by cyclically shifting the elements of the initial column.
    For example, if the list of riders contains RiderComputeItem objects (with names) 
    ['Barry B', 'John H', 'Lynsey S'], the resulting matrix will be:

    [
        ['Barry B', 'John H', 'Lynsey S']
        ['John H', 'Lynsey S', 'Barry B']
        ['Lynsey S', 'Barry B', 'John H']
    ]
    """
    n = len(riders)
    
    # Generate the cyclic matrix using simple iteration
    matrix: List[List[RiderComputeItem]] = []
    for i in range(n):
        row = [riders[(i + j) % n] for j in range(n)]
        matrix.append(row)
    
    return matrix


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

#main runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        start_time = time.time()
        test00()
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
