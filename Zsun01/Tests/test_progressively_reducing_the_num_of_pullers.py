import concurrent.futures
import os
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem, PacelineSolutionsComputationReport, RiderContributionDisplayObject
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae03 import generate_rider_permutations
from jgh_formulae08 import (
        calculate_upper_bound_paceline_speed,
        calculate_upper_bound_paceline_speed_at_one_hour_watts,
        generate_paceline_solutions_using_serial_and_parallel_algorithms,
        generate_a_single_paceline_solution_complying_with_exertion_constraints)
from jgh_formatting import truncate
from constants import EXERTION_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH


def evaluate_permutation(params: PacelineIngredientsItem) -> PacelineSolutionsComputationReport:
    # GET READY  FIGURE OUT params.pull_speeds_kph

    perm_riders = params.riders_list

    _, _, r01_speed = calculate_upper_bound_paceline_speed(perm_riders)
    _, _, r02_speed = calculate_upper_bound_paceline_speed_at_one_hour_watts(perm_riders)
    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed, 0)), 1)

    params.pull_speeds_kph = [lowest_bound_speed] * len(perm_riders)

    # GO!

    result = generate_paceline_solutions_using_serial_and_parallel_algorithms(params)

    return result

def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders: list[ZsunRiderItem] = []
    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    rider_permutations = generate_rider_permutations(riders)
    logger.info(f"Ranking the speed of {len(rider_permutations)} variations in the circulation order of {len(riders)} riders...\n")


    # --- Evaluate all permutations for optimal pull plans in parallel ---

    ARRAY_OF_STANDARD_PULL_PERIODS_SEC = [30.0,60.0, 240.0]

    list_of_instructions = [
        PacelineIngredientsItem(
            riders_list=perm_riders,
            sequence_of_pull_periods_sec=ARRAY_OF_STANDARD_PULL_PERIODS_SEC,
            pull_speeds_kph=[],  # Will be set in evaluate_permutation
            max_exertion_intensity_factor=EXERTION_INTENSITY_FACTOR
        )
        for _, perm_riders in rider_permutations.items()
    ]

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(evaluate_permutation, list_of_instructions)
        all_permutation_results = list(results)

    # 4. Sort by speed of halted_rider in lowest_dispersion_plan
    def get_halted_rider_speed(optimal_result: PacelineSolutionsComputationReport):
        if not optimal_result.solutions:
            return 0
        # # Assume the first solution is the "lowest_dispersion_plan"
        # solution = optimal_result.solutions[0]

        # Assume the 2nd solution is the "fastest_plan"
        solution = optimal_result.solutions[1]

        return solution.calculated_average_speed_of_paceline_kph

    all_permutation_results.sort(key=get_halted_rider_speed, reverse=True)

    # 5. Log a pretty table for each lowest_dispersion_plan
    for idx, optimal_result in enumerate(all_permutation_results):
        if not optimal_result.solutions:
            continue
        solution = optimal_result.solutions[0]
        plan_line_items = solution.rider_contributions
        if solution.algorithm_ran_to_completion == False:
            continue
        plan_line_items_displayobjects = RiderContributionDisplayObject.from_RiderContributionItems(plan_line_items)
        speed = round(solution., 1)
        rider_names = [getattr(rider, "name", str(rider)) for rider in plan_line_items.keys()]
        logger.info(f"Permutation {idx+1}: fastest plan Speed: {speed} kph | Riders: {', '.join(rider_names)}")
        # log_pretty_paceline_solution_report(
        #     f"Permutation {idx+1} - lowest_dispersion_plan: {speed} kph", plan_line_items_displayobjects, logger
        # )

if __name__ == "__main__":
        main()