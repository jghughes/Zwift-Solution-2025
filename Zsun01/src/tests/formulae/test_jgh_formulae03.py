import time
from pathlib import Path
from typing import List

from constants import PULL_DURATION_OPTIONS_SEC, DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC
from jgh_formulae03 import (
    order_paceline_by_desired_order_of_riders,
    solve_for_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph,
    generate_all_suitable_paceline_rotation_sequences_in_the_solution_space,
)
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_COMPUTE_DTO_JSON_DICT
from rider_compute_item import RiderComputeItem
from repository_of_team_rosters import RepositoryOfTeamRosters
from working_file_read_write import read_rider_compute_dict_from_json
from paceline_modelling_items import PacelineIngredientsItem
from zwift_id_base import lookup_Items_by_ZwiftID


def test01():
    dict_of_all_riders = read_rider_compute_dict_from_json(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),FILENAME_RIDER_COMPUTE_DTO_JSON_DICT)
    riderIDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)
    riders: List[RiderComputeItem] = lookup_Items_by_ZwiftID(riderIDs, dict_of_all_riders, RiderComputeItem)

    riders = order_paceline_by_desired_order_of_riders(riders)
    pull_periods_sec_as_list = PULL_DURATION_OPTIONS_SEC
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [solve_for_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders, DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC)] * len(riders),
        sequence_of_pull_periods_sec = pull_periods_sec_as_list,
        max_exertion_intensity_factor= RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(team_name),
    )

    start_time = time.perf_counter()
    pruned_sequences = generate_all_suitable_paceline_rotation_sequences_in_the_solution_space(ingredients)
    elapsed_time2 = time.perf_counter() - start_time

    # uncomment for the gory details
    # for sequence in pruned_sequences:
    #     print(sequence)

    print(f"Generated {len(pruned_sequences)} pruned_sequences for {len(riders)} riders on team={team_name} in {elapsed_time2} seconds.")

# runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        team_name = "scratchpad"

        start_time = time.time()
        test01()
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

