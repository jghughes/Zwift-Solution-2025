from pathlib import Path
from typing import List

from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import log_rider_contributions, populate_rider_contributions
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_COMPUTE_DTO_JSON_DICT
from rider_compute_item import RiderComputeItem
from repository_of_team_rosters import RepositoryOfTeamRosters
from working_file_read_write import read_rider_compute_dict_from_json
from zwift_id_base import lookup_Items_by_ZwiftID

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


def test01() -> None:

    dict_of_all_riders = read_rider_compute_dict_from_json(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),FILENAME_RIDER_COMPUTE_DTO_JSON_DICT)
    
    riderIDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)
    riders: List[RiderComputeItem] = lookup_Items_by_ZwiftID(riderIDs, dict_of_all_riders, RiderComputeItem)

    pull_durations = [120.0, 0.0, 30.0] # duration array MUST be same len as riders (or longer), and the sequence MUST match the rider order in the paceline
    pull_speeds_kph = [40.0] * len(riders)
    pull_speed = 40.0  # Example speed in kph
    pull_speeds_kph = [pull_speed] * len(riders)

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    rider_contributions = populate_rider_contributions(dict_of_rider_exertions, 0.95)

    log_rider_contributions(f"{len(riders)} riders @ {pull_speed}kph\n", rider_contributions)


#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        team_name = "scratchpad"
        test01()

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


