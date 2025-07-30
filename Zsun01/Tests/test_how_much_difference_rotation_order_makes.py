import concurrent.futures
import os
from jgh_number import safe_divide
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem, PacelineSolutionsComputationReportItem
from handy_utilities import read_dict_of_zsunriderDTO
from teams import get_team_riderIDs
from jgh_formulae03 import generate_rider_permutations
from jgh_formulae08 import generate_paceline_solutions_using_serial_and_parallel_algorithms
from jgh_formatting import truncate
from constants import RIDERS_FILE_NAME, DATA_DIRPATH

sequence_of_pull_periods_sec = [30.0, 60.0, 240.0]
desired_solution_index = 1  # 0 means lowest dispersion plan, 1 means fastest plan, etc.
max_intensity_factor = 100 #arbitrarily big number, so that we can get the fastest plan without worrying about the intensity factor.

def first_rider_is_strongest(strongest_rider : ZsunRiderItem, result : PacelineSolutionsComputationReportItem, desired_solution_index : int ) -> bool:
    if not result.solutions or not result.solutions[desired_solution_index].rider_contributions:
        return False
    first_rider = next(iter(result.solutions[desired_solution_index].rider_contributions.keys()))
    return first_rider == strongest_rider

def evaluate_permutation(params: PacelineIngredientsItem) -> PacelineSolutionsComputationReportItem:
    # GET READY  FIGURE OUT params.pull_speeds_kph

    perm_riders = params.riders_list

    _, _, r01_speed = calculate_upper_bound_paceline_speed(perm_riders)
    _, _, r02_speed = calculate_upper_bound_paceline_speed_at_one_hour_watts(perm_riders)
    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed, 0)), 1)

    params.pull_speeds_kph = [lowest_bound_speed] * len(perm_riders)

    # GO!

    result = generate_paceline_solutions_using_serial_and_parallel_algorithms(params)

    return result

def get_solution_speed(optimal_result: PacelineSolutionsComputationReportItem, desired_solution_index : int) -> float:
    if not optimal_result.solutions:
        return 0
    solution = optimal_result.solutions[desired_solution_index]
    pull_plans_for_all_riders = solution.rider_contributions.values()
    a_pull_plan = next(iter(pull_plans_for_all_riders), None) # arbitrarily take the first pull plan. the speed should be the same for all riders in a solution.
    solution_speed_kph = a_pull_plan.speed_kph if a_pull_plan else 0
    return solution_speed_kph

def get_hardest_intensity(optimal_result: PacelineSolutionsComputationReportItem, desired_solution_index : int) -> float:
    if not optimal_result.solutions:
        return 0
    solution = optimal_result.solutions[desired_solution_index]
    pull_plans_for_all_riders = solution.rider_contributions.items()

    #find the hardest intensity factor across all riders in the solution
    hardest_intensity = max(safe_divide(pull_plan.normalized_watts, rider.get_one_hour_watts())
        for rider, pull_plan in pull_plans_for_all_riders
    )
    return round(hardest_intensity, 2)

def get_intensity_suffered_by_weakest_rider(optimal_result: PacelineSolutionsComputationReportItem, desired_solution_index : int) -> float:
    if not optimal_result.solutions:
        return 0
    solution = optimal_result.solutions[desired_solution_index]

    # identify the weakest rider
    weakest_rider = min(
        (rider for rider, _ in solution.rider_contributions.items()),
        key=lambda r: r.get_strength_wkg()
    )

    # obtain pull plan of weakest rider
    pull_plan_of_weakest_rider = solution.rider_contributions[weakest_rider]

    # calculate intensity factor of the weakest rider
    intensity_factor = safe_divide(pull_plan_of_weakest_rider.normalized_watts, weakest_rider.get_one_hour_watts())

    return round(intensity_factor, 2)


def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    dict_of_zsunrideritems = read_dict_of_zsunriderDTO(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders: list[ZsunRiderItem] = [dict_of_zsunrideritems[ID] for ID in riderIDs]

    rider_permutations = generate_rider_permutations(riders)

    logger.info(f"Ranking the implications on speed and intensity of {len(rider_permutations)} variations in the circulation order of {len(riders)} riders...\n")

    #Note to self: don't try this for more iterations/riders/alternatives than the threshold where generate_paceline_solutions_using_serial_and_parallel_algorithms() transitions from serial to parallel processing. it unleashes a flood of parallel workers that will saturate the memory of the machine and cause it to grind to a halt. This is empirically determined to be around 512 permutations for 4 standard pull periods and 5 riders.

    title = "lowest dispersion plan" if desired_solution_index == 0 else "fastest plan"

    # --- Evaluate all permutations for optimal pull plans in parallel ---
    list_of_instructions = [
        PacelineIngredientsItem(
            riders_list=perm_riders,
            sequence_of_pull_periods_sec=sequence_of_pull_periods_sec,
            pull_speeds_kph=[],  # Will be set in evaluate_permutation
            max_exertion_intensity_factor=max_intensity_factor
        )
        for _, perm_riders in rider_permutations.items()
    ]

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(evaluate_permutation, list_of_instructions)
        all_permutation_results = list(results)

    # 4. exclude all the results in all_permutation_results which do not have the strongest rider first on the list of riders.


    # Filter: only keep results where the first rider in the pull plan is the strongest, and the last rider is the second_strongest rider
    
    # Identify the strongest and second strongest riders (by w/kg)
    sorted_riders = sorted(riders, key=lambda r: r.get_strength_wkg(), reverse=True)
    strongest_rider = sorted_riders[0]
    second_strongest_rider = sorted_riders[1]

    logger.info(f"The strongest rider is {strongest_rider.name} with {strongest_rider.get_strength_wkg()} w/kg.")
    logger.info(f"The second strongest rider is {second_strongest_rider.name} with {second_strongest_rider.get_strength_wkg()} w/kg.\n")

    def first_and_last_rider_filter(result: PacelineSolutionsComputationReportItem, desired_solution_index: int) -> bool:
        if not result.solutions or not result.solutions[desired_solution_index].rider_contributions:
            return False
        rider_order = list(result.solutions[desired_solution_index].rider_contributions.keys())
        return rider_order[0] == strongest_rider and rider_order[-1] == second_strongest_rider

    all_permutation_results = [
        result for result in all_permutation_results
        if first_and_last_rider_filter(result, desired_solution_index)]     
    logger.info(f"Filtered down to {len(all_permutation_results)} permutations with the strongest rider first and 2nd strongest last.\n")

    # 5. Log a pretty table of the speeds for the desired solution - - sorted by speed, fastest first

    # all_permutation_results.sort(key=lambda result: get_solution_speed(result, desired_solution_index), reverse=True)
    # for index, optimal_result in enumerate(all_permutation_results):
    #     if not optimal_result.solutions:
    #         continue
    #     speed_kph = get_solution_speed(optimal_result, desired_solution_index)
    #     solution = optimal_result.solutions[desired_solution_index]
    #     plan_line_items = solution.rider_contributions
    #     rider_names = [rider.name for rider in plan_line_items.keys()]        
    #     logger.info(f"Permutation {index+1}: {title} {speed_kph}kph | Riders: {', '.join(rider_names)}")

    # 6. Log a pretty table of the hardest intensity of anybody for the desired solution - - sorted by intensity, lowest first

    # all_permutation_results.sort(key=lambda result: get_hardest_intensity(result, desired_solution_index), reverse=False)
    # for index, optimal_result in enumerate(all_permutation_results):
    #     if not optimal_result.solutions:
    #         continue
    #     hardest_intensity = get_hardest_intensity(optimal_result, desired_solution_index)
    #     solution = optimal_result.solutions[desired_solution_index]
    #     plan_line_items = solution.rider_contributions
    #     rider_names = [rider.name for rider in plan_line_items.keys()]        
    #     logger.info(f"Permutation {index+1}: {title}: IF={hardest_intensity} | Riders: {', '.join(rider_names)}")

    # 6. Log a pretty table of the hardest intensity of the weakest rider for the desired solution - - sorted by intensity, lowest first

    all_permutation_results.sort(key=lambda result: get_intensity_suffered_by_weakest_rider(result, desired_solution_index), reverse=False)
    for index, optimal_result in enumerate(all_permutation_results):
        if not optimal_result.solutions:
            continue
        hardest_intensity = get_intensity_suffered_by_weakest_rider(optimal_result, desired_solution_index)
        solution = optimal_result.solutions[desired_solution_index]
        plan_line_items = solution.rider_contributions
        rider_names = [rider.name for rider in plan_line_items.keys()]        
        logger.info(f"Permutation {index+1}: {title}: IF={hardest_intensity} | Riders: {', '.join(rider_names)}")




if __name__ == "__main__":
        main()