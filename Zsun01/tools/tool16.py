import concurrent.futures
import os
from zsun_rider_item import ZsunRiderItem
from computation_classes import PullPlanComputationParams, OptimalPullPlansResult
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae03 import generate_rider_permutations
from jgh_formulae07 import populate_pullplan_displayobjects, log_concise_pullplan_displayobjects
from jgh_formulae08 import (
        calculate_upper_bound_pull_speed,
        calculate_upper_bound_speed_at_one_hour_watts,
        search_for_optimal_pull_plans_using_most_performant_algorithm,)
from jgh_formatting import truncate
from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging




def evaluate_permutation(params: PullPlanComputationParams) -> OptimalPullPlansResult:
    # GET READY  FIGURE OUT params.pull_speeds_kph

    perm_riders = params.riders_list

    _, _, r01_speed = calculate_upper_bound_pull_speed(perm_riders)
    _, _, r02_speed = calculate_upper_bound_speed_at_one_hour_watts(perm_riders)
    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed, 0)), 1)

    params.pull_speeds_kph = [lowest_bound_speed] * len(perm_riders)

    # GO!

    result = search_for_optimal_pull_plans_using_most_performant_algorithm(params)

    return result

def main():
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders: list[ZsunRiderItem] = []
    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    rider_permutations = generate_rider_permutations(riders)

    # --- Evaluate all permutations for optimal pull plans in parallel ---
    params_list = [
        PullPlanComputationParams(
            riders_list=perm_riders,
            standard_pull_periods_sec=STANDARD_PULL_PERIODS_SEC,
            pull_speeds_kph=None,  # Will be set in evaluate_permutation
            max_exertion_intensity_factor=MAX_INTENSITY_FACTOR
        )
        for perm_idx, perm_riders in rider_permutations.items()
    ]

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(evaluate_permutation, params_list)
        all_permutation_results = list(results)

    # 4. Sort by speed of halted_rider in lowest_dispersion_plan
    def get_halted_rider_speed(optimal_result: OptimalPullPlansResult):
        if not optimal_result.solutions:
            return 0
        # Assume the first solution is the "lowest_dispersion_plan"
        solution = optimal_result.solutions[0]
        # Each solution has rider_pull_plans: DefaultDict[ZsunRiderItem, RiderPullPlanItem]
        # and limiting_rider: Optional[ZsunRiderItem]
        if solution.limiting_rider is None:
            return 0
        limiting_rider = solution.limiting_rider
        plan_line_items = solution.rider_pull_plans
        if limiting_rider not in plan_line_items:
            return 0
        return getattr(plan_line_items[limiting_rider], "speed_kph", 0)

    all_permutation_results.sort(key=get_halted_rider_speed, reverse=True)

    # 5. Log a pretty table for each lowest_dispersion_plan
    for idx, optimal_result in enumerate(all_permutation_results):
        if not optimal_result.solutions:
            continue
        solution = optimal_result.solutions[0]
        plan_line_items = solution.rider_pull_plans
        limiting_rider = solution.limiting_rider
        if limiting_rider is None or limiting_rider not in plan_line_items:
            continue
        plan_line_items_displayobjects = populate_pullplan_displayobjects(plan_line_items)
        speed = round(getattr(plan_line_items[limiting_rider], "speed_kph", 0), 1)
        rider_names = [getattr(rider, "name", str(rider)) for rider in plan_line_items.keys()]
        logger.info(f"\nPermutation {idx+1}: lowest_dispersion_plan Speed: {speed} kph | Riders: {', '.join(rider_names)}")
        log_concise_pullplan_displayobjects(
            f"Permutation {idx+1} - lowest_dispersion_plan: {speed} kph", plan_line_items_displayobjects, logger
        )

if __name__ == "__main__":
        main()