import time
from pathlib import Path
from typing import List

from constants import PULL_DURATION_OPTIONS_SEC
from jgh_formulae03 import (
    arrange_riders_interleaved_by_1_minute_strength,
    calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph,
    generate_all_suitable_paceline_rotation_sequences_in_the_solution_space,
)
from storage_config import DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_COMPUTE_DTO_JSON_DICT
from rider_compute_item import RiderComputeItem
from repository_of_team_rosters import RepositoryOfTeamRosters
from working_file_read_write import read_rider_brute_dict_from_json
from paceline_modelling_items import PacelineIngredientsItem
from zwift_id_base import lookup_Items_by_ZwiftID


def test01():
    dict_of_all_riders = read_rider_brute_dict_from_json(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),FILENAME_RIDER_COMPUTE_DTO_JSON_DICT)
    riderIDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)
    riders: List[RiderComputeItem] = lookup_Items_by_ZwiftID(riderIDs, dict_of_all_riders, RiderComputeItem)

    riders = arrange_riders_interleaved_by_1_minute_strength(riders) # an arbitrary choice of ordering as a test
    pull_periods_sec_as_list = PULL_DURATION_OPTIONS_SEC
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
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
    from jgh_logging import setup_structlog 
    from jgh_exceptions import AppErrorBase, AlertMessageError, describe_exception, log_event, log_exception
    setup_structlog()
    try:
        team_name = "scratchpad"
        test01()
    except AlertMessageError as alertError:
        print(alertError.message)  
    except AppErrorBase as app_err:
        print("Error was caught. See log files for details.")
        print(app_err.short_description())  
        log_event(app_err)              
    except Exception as unhandledEx:
        print("Fatal exception occurred. See log files for details.")
        print(describe_exception(unhandledEx)) 
        # Note: Log files saved in folder called 'logs' in the root folder of your VS2022 project. 
        # Folder not visible in VS2022 Solution Explorer. Use File Explorer. 
        log_exception(unhandledEx)

