import concurrent.futures
import os
from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae03 import generate_rider_permutations
from jgh_formulae07 import populate_pullplan_displayobjects, log_concise_pullplan_displayobjects
from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging

def evaluate_permutation(args):
    perm_riders, STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR = args
    from jgh_formulae08 import (
        calculate_upper_bound_pull_speed,
        calculate_upper_bound_speed_at_one_hour_watts,
        search_for_optimal_pull_plans_using_most_efficient_algorithm,
    )
    from jgh_formatting import truncate

    r01, _, r01_speed = calculate_upper_bound_pull_speed(perm_riders)
    r02, _, r02_speed = calculate_upper_bound_speed_at_one_hour_watts(perm_riders)
    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed, 0)), 1)

    pull_plans, total_num_of_all_conceivable_plans, total_compute_iterations, compute_time = \
        search_for_optimal_pull_plans_using_most_efficient_algorithm(
            perm_riders, STANDARD_PULL_PERIODS_SEC, lowest_bound_speed, MAX_INTENSITY_FACTOR
        )

    return (pull_plans, total_num_of_all_conceivable_plans, total_compute_iterations, compute_time)

def main():
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders : list[ZsunRiderItem] = []
    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    rider_permutations = generate_rider_permutations(riders)

    # --- Evaluate all permutations for optimal pull plans in parallel ---
    all_permutation_results = []
    args_list = [
        (perm_riders, STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR)
        for perm_idx, perm_riders in rider_permutations.items()
    ]

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(evaluate_permutation, args_list)
        all_permutation_results = list(results)

    # # 4. Sort by speed of halted_rider in lowest_dispersion_plan
    # def get_halted_rider_speed(result):
    #     lowest_dispersion_plan, _ = result[0][:]
    #     _, plan_line_items01, halted_rider01 = lowest_dispersion_plan
    #     return plan_line_items01[halted_rider01].speed_kph

    # all_permutation_results.sort(key=get_halted_rider_speed, reverse=True)

    # # 5. Log a pretty table for each lowest_dispersion_plan
    # for idx, result in enumerate(all_permutation_results):
    #     pull_plans, _, _, _ = result
    #     lowest_dispersion_plan, _ = pull_plans[:2]
    #     _, plan_line_items01, halted_rider01 = lowest_dispersion_plan
    #     plan_line_items_displayobjects01 = populate_pullplan_displayobjects(plan_line_items01)
    #     speed = round(plan_line_items01[halted_rider01].speed_kph, 1)
    #     rider_names = [rider.name for rider in plan_line_items01.keys()]
    #     logger.info(f"\nPermutation {idx+1}: lowest_dispersion_plan Speed: {speed} kph | Riders: {', '.join(rider_names)}")
    #     log_concise_pullplan_displayobjects(
    #         f"Permutation {idx+1} - lowest_dispersion_plan: {speed} kph", plan_line_items_displayobjects01, logger
    #     )

    # --- Repeat for highest_speed_plan ---
    # 4b. Sort by speed of halted_rider in highest_speed_plan
    def get_halted_rider_speed_highest_speed_plan(result):
        _, highest_speed_plan = result[0][:2]
        _, plan_line_items02, halted_rider02 = highest_speed_plan
        return plan_line_items02[halted_rider02].speed_kph

    all_permutation_results.sort(key=get_halted_rider_speed_highest_speed_plan, reverse=True)

    # 5b. Log a pretty table for each highest_speed_plan
    for idx, result in enumerate(all_permutation_results):
        pull_plans, _, _, _ = result
        _, highest_speed_plan = pull_plans[:2]
        _, plan_line_items02, halted_rider02 = highest_speed_plan
        plan_line_items_displayobjects02 = populate_pullplan_displayobjects(plan_line_items02)
        speed = round(plan_line_items02[halted_rider02].speed_kph, 1)
        rider_names = [rider.name for rider in plan_line_items02.keys()]
        logger.info(f"\nPermutation {idx+1}: highest_speed_plan Speed: {speed} kph | Riders: {', '.join(rider_names)}")
        log_concise_pullplan_displayobjects(
            f"Permutation {idx+1} - highest_speed_plan: {speed} kph", plan_line_items_displayobjects02, logger
        )




if __name__ == "__main__":
    main()


