from typing import  List, DefaultDict, Tuple
import os
from collections import defaultdict
import copy
import concurrent.futures
import time
import numpy as np
from jgh_formatting import truncate
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem, RiderContributionItem, PacelineComputationReport, PacelineSolutionsComputationReport
from jgh_formulae02 import (calculate_overall_intensity_factor_of_rider_contribution, calculate_overall_average_speed_of_paceline_kph, generate_a_scaffold_of_the_total_solution_space, radically_shrink_the_solution_space)
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_rider_contributions
from constants import (SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD, SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_CONSTRAINT_VIOLATING_SPEED_KPH, INCREASE_IN_SPEED_PER_ITERATION_KPH, DESIRED_PRECISION_KPH, MAX_PERMITTED_ITERATIONS)

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger("numba").setLevel(logging.ERROR)


def populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(
    riders:                        List[ZsunRiderItem],
    standard_pull_periods_seconds: List[float],
    pull_speeds_kph:               List[float],
    max_exertion_intensity_factor: float
) -> Tuple[float, DefaultDict[ZsunRiderItem, RiderContributionItem]]:
    """
    Computes the contributions of each rider in a single paceline solution.

    This function determines the work assignments, exertions, and final contributions for each rider
    based on the provided pull periods, target speeds, and maximum allowed exertion intensity.
    It returns the overall average speed of the paceline and a mapping of each rider to their computed contribution.

    Args:
        riders: List of ZsunRiderItem objects representing the riders in the paceline.
        standard_pull_periods_seconds: List of pull durations (in seconds) for each rider.
        pull_speeds_kph: List of target pull speeds (in kph) for each rider.
        max_exertion_intensity_factor: Maximum allowed exertion intensity factor for any rider.

    Returns:
        Tuple containing:
            - overall_av_speed_of_paceline (float): The computed average speed of the paceline (kph).
            - dict_of_rider_contributions (DefaultDict[ZsunRiderItem, RiderContributionItem]):
                Mapping of each rider to their computed RiderContributionItem, including effort metrics and constraint violations.
    """

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, standard_pull_periods_seconds, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    overall_av_speed_of_paceline = calculate_overall_average_speed_of_paceline_kph(dict_of_rider_exertions)

    dict_of_rider_contributions = populate_rider_contributions(dict_of_rider_exertions, max_exertion_intensity_factor)

    return overall_av_speed_of_paceline, dict_of_rider_contributions


def generate_a_single_paceline_solution_complying_with_exertion_constraints(
    paceline_ingredients: PacelineIngredientsItem,
) -> PacelineComputationReport:
    """
    Computes a single paceline solution that adheres to rider exertion constraints using a binary search approach.

    This function determines the maximum feasible paceline speed such that no rider exceeds the specified exertion intensity factor.
    It first finds a safe upper bound for speed where at least one rider violates the exertion constraint, then performs a binary search
    between the lower and upper bounds to pinpoint the precise speed at which the constraint is just met. The function returns a detailed
    computation report including whether the algorithm ran to completion, the number of iterations performed, the computed average speed,
    and each rider's contribution and constraint status.

    Args:
        paceline_ingredients: PacelineIngredientsItem
            An object containing all necessary parameters for the paceline computation, including:
                - riders_list: List of ZsunRiderItem objects representing the riders.
                - sequence_of_pull_periods_sec: List of pull durations (in seconds) for each rider.
                - pull_speeds_kph: List of initial pull speeds (in kph).
                - max_exertion_intensity_factor: Maximum allowed exertion intensity factor for any rider.

    Returns:
        PacelineComputationReport: An object containing:
            - algorithm_ran_to_completion (bool): Whether the binary search completed within the permitted iterations.
            - compute_iterations_performed_count (int): Number of iterations performed during the search.
            - calculated_average_speed_of_paceline_kph (float): The computed average speed of the paceline (kph).
            - rider_contributions (DefaultDict[ZsunRiderItem, RiderContributionItem]): Mapping of each rider to their computed contribution,
              including effort metrics and any constraint violations.

    Notes:
        - If a feasible solution cannot be found within the maximum permitted iterations, the function returns the last computed result
          and sets algorithm_ran_to_completion to False.
        - The function assumes all input parameters are valid and finite.
    """

    riders = paceline_ingredients.riders_list
    standard_pull_periods_seconds = list(paceline_ingredients.sequence_of_pull_periods_sec)
    lowest_conceivable_kph = truncate(paceline_ingredients.pull_speeds_kph[0],3)
    max_exertion_intensity_factor = paceline_ingredients.max_exertion_intensity_factor

    num_riders = len(riders)

    compute_iterations_performed: int = 0 # Number of iterations performed in the binary search, part of the answer
    dict_of_rider_contributions: DefaultDict[ZsunRiderItem, RiderContributionItem] = defaultdict(RiderContributionItem)  # <-- part of the answer

    # Initial parameters used to determine a safe upper_bound for the binary search
    lower_bound_for_next_search_iteration_kph = lowest_conceivable_kph
    upper_bound_for_next_search_iteration_kph = lower_bound_for_next_search_iteration_kph

    # Find a speed at which at least one rider's plan has already become in violation.
    # This is done by iteratively increasing the speed until we stumble upon a speed 
    # that violates the contribution of at least one rider. This speed is not the answer 
    # we are looking for. It will most likely be way above the precise speed that 
    # triggered the violation, but it is a safe upper bound. This is required for 
    # the binary search to work correctly to piun down the precise speed.

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_CONSTRAINT_VIOLATING_SPEED_KPH):

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders, max_exertion_intensity_factor)

        if any(contribution.effort_constraint_violation_reason for contribution in dict_of_rider_contributions.values()):
            break # break out of the loop as soon as we successfuly find a speed that violates at least one rider's ability
        
        upper_bound_for_next_search_iteration_kph += INCREASE_IN_SPEED_PER_ITERATION_KPH

        compute_iterations_performed += 1
    else:
        # If we never find an upper_bound_for_next_search_iteration_kph bound, just bale and return the last result
        return PacelineComputationReport(
            algorithm_ran_to_completion         = False,  # We did not run to completion, we hit the max iterations
            exertion_intensity_constraint_used  = paceline_ingredients.max_exertion_intensity_factor,
            compute_iterations_performed_count  = compute_iterations_performed,
            rider_contributions                 = dict_of_rider_contributions,
        )

    # Do the binary search. The concept is to search by bouncing back and forth between speeds bounded by  
    # lower_bound_for_next_search_iteration_kph and upper_bound_for_next_search_iteration_kph, continuing
    # until the difference between the two bounds is less than DESIRED_PRECISION_KPH i.e. until we are within a small enough range
    # of speeds that we can consider the solution precise enough. We have thus found the speed at the point at which it 
    # violates the contribution of at least one rider. The cause of the violation is flagged inside populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(..). 
    # At this moment, we know that the speed of the paceline is somewhere between the lower and upper bounds, the difference 
    # between which is negligible i.e. less than DESIRED_PRECISION_KPH. Use the upper_bound_for_next_search_iteration_kph as our answer


    while (upper_bound_for_next_search_iteration_kph - lower_bound_for_next_search_iteration_kph) > DESIRED_PRECISION_KPH and compute_iterations_performed < MAX_PERMITTED_ITERATIONS:

        mid_point_kph = (lower_bound_for_next_search_iteration_kph + upper_bound_for_next_search_iteration_kph) / 2

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [mid_point_kph] * num_riders, max_exertion_intensity_factor)

        compute_iterations_performed += 1

        if any(rider_contribution.effort_constraint_violation_reason for rider_contribution in dict_of_rider_contributions.values()):
            upper_bound_for_next_search_iteration_kph = mid_point_kph
        else:
            lower_bound_for_next_search_iteration_kph = mid_point_kph

    # Knowing the speed, we can rework the contributions and thus the solution

    speed_of_paceline,dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders , max_exertion_intensity_factor)

    return PacelineComputationReport(
        algorithm_ran_to_completion              = True,  
        compute_iterations_performed_count       = compute_iterations_performed,
        exertion_intensity_constraint_used       = paceline_ingredients.max_exertion_intensity_factor,
        calculated_average_speed_of_paceline_kph = speed_of_paceline,
        rider_contributions                      = dict_of_rider_contributions,
    )


def generate_paceline_solutions_using_serial_processing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: List[List[float]]
) -> List[PacelineComputationReport]:
    """
    Compute paceline solutions for a set of candidate pull period sequences using serial (single-threaded) processing.

    This function evaluates each candidate paceline rotation schedule one at a time, generating a solution for each by
    invoking the exertion-constrained paceline solver. For each alternative, it constructs a PacelineIngredientsItem
    with the specified pull periods, computes the optimal paceline speed and rider contributions, and collects the results.
    Any exceptions encountered during computation are logged and the corresponding alternative is skipped.

    Args:
        paceline_ingredients: PacelineIngredientsItem
            The base input parameters for the computation, including the list of riders, initial pull speeds,
            and exertion constraints. The pull periods are overridden for each alternative.
        paceline_rotation_sequence_alternatives: List[List[float]]
            A list of candidate pull period schedules to evaluate, where each schedule is a list of pull durations (seconds).

    Returns:
        List[PacelineComputationReport]: A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - This function processes alternatives sequentially and is intended for use when the number of alternatives is small.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - For large numbers of alternatives, consider using parallel processing for improved performance.
    """

    paceline_description = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)

    solutions: List[PacelineComputationReport] = []

    for sequence in paceline_rotation_sequence_alternatives:
        try:
            paceline_description.sequence_of_pull_periods_sec = list(sequence)

            result = generate_a_single_paceline_solution_complying_with_exertion_constraints(paceline_description)

            solutions.append(PacelineComputationReport(
                algorithm_ran_to_completion              = result.algorithm_ran_to_completion,
                compute_iterations_performed_count       = result.compute_iterations_performed_count,
                exertion_intensity_constraint_used       = paceline_ingredients.max_exertion_intensity_factor,
                calculated_average_speed_of_paceline_kph = result.calculated_average_speed_of_paceline_kph,
                rider_contributions                      = result.rider_contributions,
            ))
        except Exception as exc:
            logger.error(f"Exception in function generate_a_single_paceline_solution_complying_with_exertion_constraints(): {exc}")

    return solutions


def generate_paceline_solutions_using_parallel_workstealing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: List[List[float]]
) -> List[PacelineComputationReport]:
    """
    Computes paceline solutions for multiple candidate pull period sequences using parallel processing with a work-stealing process pool.

    This function distributes the evaluation of each candidate paceline rotation schedule across available CPU cores using a process pool,
    allowing for efficient computation when the number of alternatives is large. For each alternative, it constructs a PacelineIngredientsItem
    with the specified pull periods, computes the optimal paceline speed and rider contributions, and collects the results. Invalid or incomplete
    results are skipped and logged.

    Args:
        paceline_ingredients: PacelineIngredientsItem
            The base input parameters for the computation, including the list of riders, initial pull speeds,
            and exertion constraints. The pull periods are overridden for each alternative.
        paceline_rotation_sequence_alternatives: List[List[float]]
            A list of candidate pull period schedules to evaluate, where each schedule is a list of pull durations (seconds).

    Returns:
        List[PacelineComputationReport]: A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - This function is intended for use when the number of alternatives is large enough to benefit from parallel processing.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - Invalid or incomplete results are logged as warnings and not included in the output list.
    """

    paceline_description = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)

    list_of_instructions: List[PacelineIngredientsItem] = []    
    
    for sequence in paceline_rotation_sequence_alternatives:
        paceline_description.sequence_of_pull_periods_sec = list(sequence)
        list_of_instructions.append(copy.deepcopy(paceline_description))

    solutions: List[PacelineComputationReport] = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_params = {
            executor.submit(generate_a_single_paceline_solution_complying_with_exertion_constraints, p): p
            for p in list_of_instructions
        }
        for future in concurrent.futures.as_completed(future_to_params):
            try:
                result = future.result()

                if (result is None or
                    not hasattr(result, "rider_contributions") or
                    result.rider_contributions is None or
                    not isinstance(result.rider_contributions, dict)):
                    logger.warning(f"Skipping invalid result: {result}")
                    continue

                solutions.append(PacelineComputationReport(
                    algorithm_ran_to_completion              = result.algorithm_ran_to_completion,
                    compute_iterations_performed_count       = result.compute_iterations_performed_count,
                    calculated_average_speed_of_paceline_kph = result.calculated_average_speed_of_paceline_kph,
                exertion_intensity_constraint_used           = paceline_ingredients.max_exertion_intensity_factor,
                    rider_contributions                      = result.rider_contributions,
                ))
            except Exception as exc:
                logger.error(f"Exception in function generate_a_single_paceline_solution_complying_with_exertion_constraints(): {exc}")


    return solutions


def generate_paceline_solutions_using_serial_and_parallel_algorithms(
    paceline_ingredients: PacelineIngredientsItem, paceline_rotation_sequence_alternatives : List[List[float]]
) -> List[PacelineComputationReport]:
    """
    Computes paceline solutions for a set of candidate pull period sequences using the most efficient processing strategy.

    This function automatically selects between serial and parallel processing based on the number of candidate alternatives.
    For a small number of alternatives, it uses serial (single-threaded) processing; for larger sets, it leverages parallel
    work-stealing to utilize multiple CPU cores for improved performance. Each alternative is evaluated to determine the optimal
    paceline speed and rider contributions under exertion constraints.

    Args:
        paceline_ingredients: PacelineIngredientsItem
            The base input parameters for the computation, including the list of riders, initial pull speeds,
            and exertion constraints. The pull periods are overridden for each alternative.
        paceline_rotation_sequence_alternatives: List[List[float]]
            A list of candidate pull period schedules to evaluate, where each schedule is a list of pull durations (seconds).

    Returns:
        List[PacelineComputationReport]: A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - The function chooses serial or parallel processing based on the __SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD__ constant.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - For large numbers of alternatives, parallel processing can significantly reduce computation time.
    """

    if len(paceline_rotation_sequence_alternatives) < SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD:
        return generate_paceline_solutions_using_serial_processing_algorithm(paceline_ingredients, paceline_rotation_sequence_alternatives)
    else:
        return generate_paceline_solutions_using_parallel_workstealing_algorithm(paceline_ingredients, paceline_rotation_sequence_alternatives)


def generate_two_groovy_paceline_solutions(paceline_ingredients: PacelineIngredientsItem
    ) -> PacelineSolutionsComputationReport:
    """
    Generates and returns two optimal paceline solutions based on the provided paceline ingredients.

    This function explores a large space of possible paceline rotation schedules, evaluates each under exertion constraints,
    and selects two "groovy" solutions: one with the highest average paceline speed, and one with the lowest standard deviation
    of rider intensity factors (i.e., the most balanced effort distribution). The function leverages efficient serial or parallel
    computation depending on the number of alternatives, and returns a detailed computation report including timing and iteration statistics.

    Args:
        paceline_ingredients (PacelineIngredientsItem): 
            The input parameters for the computation, including the list of riders, pull durations, initial pull speeds,
            and maximum exertion intensity factor.

    Returns:
        PacelineSolutionsComputationReport: 
            An object containing:
                - total_pull_sequences_examined (int): Number of candidate paceline rotation schedules evaluated.
                - total_compute_iterations_performed (int): Total number of compute iterations performed across all solutions.
                - computational_time (float): Total time taken for the computation (seconds).
                - solutions (List[PacelineComputationReport]): 
                    A list containing two solutions:
                        [0]: The solution with the lowest standard deviation of rider intensity factors (most balanced).
                        [1]: The solution with the highest average paceline speed.

    Raises:
        ValueError: If required input parameters are missing or invalid.
        RuntimeError: If no valid solutions are found.

    Notes:
        - The function first generates all feasible paceline rotation alternatives, then prunes the solution space for efficiency.
        - If the number of alternatives is very large, a warning is logged.
        - Only solutions with valid, finite metrics are considered for selection.
        - The returned solutions are intended to represent both the fastest and the most equitable paceline configurations.
    """

    if not paceline_ingredients.riders_list:
        raise ValueError("No riders provided to generate_paceline_solutions_using_serial_processing_algorithm.")
    if not paceline_ingredients.sequence_of_pull_periods_sec:
        raise ValueError("No standard pull durations provided to generate_paceline_solutions_using_serial_processing_algorithm.")
    if any(d <= 0 or not np.isfinite(d) for d in paceline_ingredients.sequence_of_pull_periods_sec):
        raise ValueError("All standard pull durations must be positive and finite.")
    if not paceline_ingredients.pull_speeds_kph or not np.isfinite(paceline_ingredients.pull_speeds_kph[0]) or paceline_ingredients.pull_speeds_kph[0] <= 0:
        raise ValueError("binary_search_seed must be positive and finite.")
    
    all_conceivable_paceline_rotation_alternatives= generate_a_scaffold_of_the_total_solution_space(len(paceline_ingredients.riders_list), paceline_ingredients.sequence_of_pull_periods_sec)

    paceline_rotation_sequence_alternatives = radically_shrink_the_solution_space(all_conceivable_paceline_rotation_alternatives, paceline_ingredients.riders_list)

    if len(paceline_rotation_sequence_alternatives) > 2_000:
        logger.warning(f"Warning. Number of alternatives to be computed and evaluated is very large: {len(paceline_rotation_sequence_alternatives)}")

    start_time = time.perf_counter()

    all_paceline_solutions = generate_paceline_solutions_using_serial_and_parallel_algorithms(paceline_ingredients, paceline_rotation_sequence_alternatives)

    end_time = time.perf_counter()

    time_taken_to_compute = end_time - start_time

    # we have potentially hundreds or even thousands of all_paceline_solutions to run through to find just 
    # the top two that feature the highest_speed and the lowest_std_deviation. so let's get ready  ..
    current_highest_speed: float = float('-inf')
    current_highest_speed_paceline_solution = None

    current_lowest_std_deviation: float = float('inf')
    current_lowest_std_deviation_paceline_solution = None

    total_compute_iterations_performed = 0 

    for this_solution in all_paceline_solutions:

        total_compute_iterations_performed += this_solution.compute_iterations_performed_count

        scratchpatch_speed_kph = this_solution.calculated_average_speed_of_paceline_kph # criterion

        if not np.isfinite(scratchpatch_speed_kph):
            logger.warning(f"Binary search iteration error. Non-finite scratchpatch_speed_kph encountered: {scratchpatch_speed_kph}")
            continue

        if scratchpatch_speed_kph > current_highest_speed:
            current_highest_speed = scratchpatch_speed_kph
            current_highest_speed_paceline_solution = this_solution # the meat

        rider_contibution_intensity_factors = [contribution.intensity_factor for _, contribution in this_solution.rider_contributions.items()]

        if not rider_contibution_intensity_factors:
            logger.warning("No valid rider_contibution_intensity_factors in dict_of_rider_contributions.")
            continue

        std_deviation_of_intensity_factors = float(np.std(rider_contibution_intensity_factors)) # criterion

        if not np.isfinite(std_deviation_of_intensity_factors):
            logger.warning(f"Non-finite std_deviation_of_intensity_factors encountered: {std_deviation_of_intensity_factors}")
            continue

        if std_deviation_of_intensity_factors < current_lowest_std_deviation:
            current_lowest_std_deviation = std_deviation_of_intensity_factors
            current_lowest_std_deviation_paceline_solution = this_solution # the meat


    if current_highest_speed_paceline_solution is None and current_lowest_std_deviation_paceline_solution is None:
        raise RuntimeError("No valid solution found (both current_highest_speed_paceline_solution and current_lowest_std_deviation_paceline_solution are None)")
    elif current_highest_speed_paceline_solution is None:
        raise RuntimeError("No valid this_solution found (current_highest_speed_paceline_solution is None)")
    elif current_lowest_std_deviation_paceline_solution is None:
        raise RuntimeError("No valid this_solution found (current_lowest_std_deviation_paceline_solution is None)")

    desirable_solutions = [current_lowest_std_deviation_paceline_solution, current_highest_speed_paceline_solution]

    return PacelineSolutionsComputationReport(
        total_pull_sequences_examined      = len(paceline_rotation_sequence_alternatives),
        total_compute_iterations_performed = total_compute_iterations_performed,
        computational_time                 = time_taken_to_compute,
        solutions                          = desirable_solutions
    )


def main01():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    save_filename_without_ext = f"benchmark_parallel_processing_{len(riders)}_riders"

    logger.info(f"Starting: benchmarking serial vs parallel processing with {len(riders)} riders")

    all_conceivable_paceline_rotation_schedules = generate_a_scaffold_of_the_total_solution_space(len(riders), ARRAY_OF_STANDARD_PULL_PERIODS_SEC)

    plan_params = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = ARRAY_OF_STANDARD_PULL_PERIODS_SEC,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )

    # Serial run as the base case
    s1 = time.perf_counter()
    _ = generate_paceline_solutions_using_serial_processing_algorithm(plan_params, all_conceivable_paceline_rotation_schedules)
    s2 = time.perf_counter()
    logger.info(f"Base-case: serial run compute time (measured): {round(s2 - s1, 2)} seconds")

    # Parallel run
    p1 = time.perf_counter()
    _ = generate_paceline_solutions_using_parallel_workstealing_algorithm(plan_params, all_conceivable_paceline_rotation_schedules)
    p2 = time.perf_counter()

    logger.info(f"Test-case: parallel run compute time (measured): {round(p2 - p1,2)} seconds")

    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Serial run:\n")
    report_lines.append(f"  Compute time (measured): {round(s2 - s1, 2)} seconds\n")
    report_lines.append("Parallel run (work-stealing):\n")
    report_lines.append(f"  Compute time (measured): {round(p2 - p1,2)} seconds\n")
    report_lines.append(f"Time saved by parallelisation: {round((s2 - s1) - (p2 - p1), 2)} seconds")
    report_lines.append("\n")

    logger.info("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Serial", "Compute Time (s)": s2 - s1},
        {"Method": "Parallel (work stealing)", "Compute Time (s)": p2 - p1},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title("Compute Time: Serial vs Parallel (work stealing)")
    plt.ylabel("Compute Time (seconds)")
    plt.xlabel("Method")
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}.png")
    plt.show()
    logger.info(f"Bar chart saved to {save_filename_without_ext}.png")


def main02():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC


    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    save_filename_without_ext = f"run_optimised_filters_and_parallelisation_with_{len(riders)}_riders"

    logger.info(f"Testing: running sensible empirically-measured thresholds for no-filtering -> filtering and serial -> parallel processing with {len(riders)} riders")

    params = PacelineIngredientsItem(
        riders_list                  = riders,
        sequence_of_pull_periods_sec    = ARRAY_OF_STANDARD_PULL_PERIODS_SEC,
        pull_speeds_kph              = [30.0] * len(riders),
        max_exertion_intensity_factor= 0.95
    )

    computation_report = generate_two_groovy_paceline_solutions(params)
    logger.info(f"Test-case: compute time using most performant algorithm (measured): {round(computation_report.computational_time,2)} seconds")

    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Most performant algorithm:\n")
    report_lines.append(f"  Compute time (measured): {round(computation_report.computational_time,2)} seconds\n")
    report_lines.append("\n")

    logger.info("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

if __name__ == "__main__":
    main01()    
    # main02()