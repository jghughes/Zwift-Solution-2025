from typing import  List, DefaultDict, Union, Callable
import os
from collections import defaultdict
import copy
import concurrent.futures
import time
import numpy as np
import itertools
from jgh_formatting import truncate
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem, RiderContributionItem, PacelineComputationReport, PacelineSolutionsComputationReport
from jgh_formulae02 import calculate_overall_intensity_factor_of_rider_contribution
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_rider_contributions
from constants import (SOLUTION_SPACE_SIZE_CONSTRAINT, SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD, SAFE_NUM_OF_ITERATIONS_TO_FIND_UPPER_BOUND_CONSTRAINT_BUSTING_SPEED_KPH, INCREASE_IN_SPEED_PER_ITERATION_KPH, DESIRED_PRECISION_KPH)

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger("numba").setLevel(logging.ERROR)






def populate_paceline_solution_alternative(
    riders:                        List[ZsunRiderItem],
    standard_pull_periods_seconds: List[float],
    pull_speeds_kph:               List[float],
    max_exertion_intensity_factor: float
) -> DefaultDict[ZsunRiderItem, RiderContributionItem]:
    """
    Generate a mapping of riders to their computed pull plan contributions for a given paceline configuration.

    This function calculates the work assignments, exertions, and resulting contributions for each rider
    based on the provided pull durations and target speeds. It also annotates each rider's contribution
    with diagnostic messages indicating if their plan is limited by intensity factor or pull watt constraints.

    Args:
        riders:                        List of rider objects to generate pull plans for.
        standard_pull_periods_seconds: Allowed pull durations (in seconds) for each rider.
        pull_speeds_kph:               Target speeds (in kph) for each rider's pull.
        max_exertion_intensity_factor: Maximum allowed exertion intensity factor for any rider.

    Returns:
        DefaultDict[ZsunRiderItem, RiderContributionItem]: Mapping of each rider to their computed contribution plan,
            including diagnostic messages if constraints are exceeded.

    Raises:
        ValueError:  If input lists are empty or their lengths do not match.
        RuntimeError: If downstream computations fail.

    Notes:
        - Diagnostic messages are attached to each RiderContributionItem to indicate if a rider's plan is limited
          by intensity factor or pull watt constraints.
        - This function is typically used as part of the paceline optimization workflow.
    """

    def invalidate_rider_contribution_if_it_breeches_pulling_power_or_intensity_factor_constraints(
        dict_of_rider_contributions: DefaultDict[ZsunRiderItem, RiderContributionItem],
        max_exertion_intensity_factor: float = 0.95
    ) -> DefaultDict[ZsunRiderItem, RiderContributionItem]:
        """
        Annotate each rider's contribution with diagnostic messages indicating what limited the overall paceline speed.

        This function examines each rider's contribution plan and determines if their exertion intensity factor
        or pull power exceeded the allowed limits. It appends a diagnostic message to each RiderContributionItem
        indicating whether the intensity factor or pull wattage was the limiting factor for that rider.

        Args:
            dict_of_rider_contributions (DefaultDict[ZsunRiderItem, RiderContributionItem]):
                Mapping of riders to their computed contribution plans.
            max_exertion_intensity_factor (float, optional):
                The maximum allowed exertion intensity factor for any rider (default: 0.95).

        Returns:
            DefaultDict[ZsunRiderItem, RiderContributionItem]:
                The same mapping, with each RiderContributionItem's `invalidation_reason` field updated to
                reflect any limiting factors (e.g., intensity factor or pull watt limit).
        """

        for rider, rider_contribution in dict_of_rider_contributions.items():
            msg = ""
            # Step 1: Intensity factor checks
            rider_intensity_factor = calculate_overall_intensity_factor_of_rider_contribution(rider, rider_contribution)
            if rider_intensity_factor >= max_exertion_intensity_factor:
                msg += f" IF>{round(100*max_exertion_intensity_factor)}%"

            # Step 2: Pull power limit checks
            rider_pull_watts_limitation = rider.get_standard_pull_watts(rider_contribution.p1_duration)
            if rider_contribution.p1_w >= rider_pull_watts_limitation:
                msg += " pull>max W"

            rider_contribution.invalidation_reason = msg

        return dict_of_rider_contributions

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, standard_pull_periods_seconds, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    dict_of_rider_contributions = populate_rider_contributions(dict_of_rider_exertions)

    annotated_dict_of_rider_contributions = invalidate_rider_contribution_if_it_breeches_pulling_power_or_intensity_factor_constraints(dict_of_rider_contributions, max_exertion_intensity_factor)

    return annotated_dict_of_rider_contributions


def weaker_than_weakest_rider_filter(
    paceline_rotation_alternatives_being_filtered: List[List[float]],
    riders: List[ZsunRiderItem]
) -> List[List[float]]:
    """
    Filter out paceline rotation schedules where any rider's pull period is less than that of the weakest rider.

    This function examines each candidate paceline rotation schedule (a list of pull periods for each rider)
    and removes any schedule where a rider (other than the second weakest) is assigned a pull period
    shorter than the weakest rider's pull period. The filter is based on the relative strength of riders,
    as determined by their w/kg values.

    Args:
        paceline_rotation_alternatives_being_filtered: List of candidate paceline rotation schedules,
            where each schedule is a list of pull periods (seconds) for each rider.
        riders: List of ZsunRiderItem objects representing the riders, used to determine strength order.

    Returns:
        List[List[float]]: The filtered list of paceline rotation schedules, with schedules violating
            the weakest rider constraint removed.

    Notes:
        - The function assumes that the order of pull periods in each schedule corresponds to the order of riders.
        - The second weakest rider is exempt from this filter to allow for some flexibility in assignments.
    """


    if not riders:
        # logger.info("weaker_than_weakest_rider_filter: No riders, returning empty list.")
        return []
    answer: List[List[float]] = []

    strengths = [r.get_strength_wkg() for r in riders]
    sorted_indices = sorted(range(len(strengths)), key=lambda i: strengths[i])
    weakest_rider_index = sorted_indices[0] if sorted_indices else None
    second_weakest_rider_index = sorted_indices[1] if len(sorted_indices) > 1 else None

    for sequence in paceline_rotation_alternatives_being_filtered:
        if weakest_rider_index is None or weakest_rider_index >= len(sequence):
            continue
        weakest_value = sequence[weakest_rider_index]
        if any(
            value < weakest_value
            for idx, value in enumerate(sequence)
            if idx != second_weakest_rider_index
        ):
            continue
        answer.append(sequence)

    # input_len = len(paceline_rotation_alternatives_being_filtered)
    # output_len = len(answer)
    # reduction = input_len - output_len
    # percent = (reduction / input_len * 100) if input_len else 0.0
    # logger.info(
    #     f"weaker_than_weakest_rider_filter applied: input {input_len} output {output_len} "
    #     f"reduction: {reduction} ({percent:.1f}%)"
    # )

    return answer


def stronger_than_nth_strongest_rider_filter(
    paceline_rotation_alternatives_being_filtered: List[List[float]],
    riders: List[ZsunRiderItem],
    n: int
) -> List[List[float]]:
    """
    Filter out paceline rotation schedules where any rider's pull period is greater than that of the nth strongest rider.

    This function examines each candidate paceline rotation schedule (a list of pull periods for each rider)
    and removes any schedule where a rider (other than the top (n-1) strongest) is assigned a pull period
    longer than the nth strongest rider's pull period. The filter is based on the relative strength of riders,
    as determined by their w/kg values, in descending order.

    Args:
        paceline_rotation_alternatives_being_filtered: List of candidate paceline rotation schedules,
            where each schedule is a list of pull periods (seconds) for each rider.
        riders: List of ZsunRiderItem objects representing the riders, used to determine strength order.
        n: The rank of the strongest rider to use as the threshold (1 = strongest, 2 = second strongest, etc.).

    Returns:
        List[List[float]]: The filtered list of paceline rotation schedules, with schedules violating
            the nth strongest rider constraint removed.

    Notes:
        - The function assumes that the order of pull periods in each schedule corresponds to the order of riders.
        - The top (n-1) strongest riders are exempt from this filter to allow for flexibility in assignments.
    """

    if not riders or n < 1:
        return []
    answer: List[List[float]] = []
    strengths = [r.get_strength_wkg() for r in riders]
    sorted_indices = sorted(range(len(strengths)), key=lambda i: strengths[i], reverse=True)
    indices = [sorted_indices[i] if len(sorted_indices) > i else None for i in range(n)]
    nth_strongest_rider_index = indices[n-1]
    for sequence in paceline_rotation_alternatives_being_filtered:
        if nth_strongest_rider_index is None or nth_strongest_rider_index >= len(sequence):
            answer.append(sequence)
            continue
        nth_strongest_value = sequence[nth_strongest_rider_index]
        if any(
            value > nth_strongest_value
            for idx, value in enumerate(sequence)
            if idx not in indices[:n-1]
        ):
            continue
        answer.append(sequence)
    # input_len = len(paceline_rotation_alternatives_being_filtered)
    # output_len = len(answer)
    # reduction = input_len - output_len
    # percent = (reduction / input_len * 100) if input_len else 0.0
    # label = f"stronger_than_{n}_strongest_rider_filter"
    # logger.info(
    #     f"{label} applied: input {input_len} output {output_len} "
    #     f"reduction: {reduction} ({percent:.1f}%)"
    # )
    return answer


def radically_shrink_the_solution_space(
    paceline_rotation_alternatives_being_filtered: List[List[float]],
    riders: List[ZsunRiderItem]
) -> List[List[float]]:
    """
    Applies a sequence of empirical filters to reduce the number of paceline rotation schedules
    (pull period assignments) considered for further computation.

    This function is designed to efficiently prune the solution space when the number of candidate
    schedules exceeds a configurable size threshold in terms of computation speed. 
    The goal is too use as few filters as possible so as not not inadventantly excluded non-obvious but ingenious
    solutions that only a brute-force algorithm can reliably detect. It applies the following filters in order:
      1. Removes any sequence where a rider's pull period is less than that of the weakest rider.
      2. Removes any sequence where a rider's pull period is greater than the strongest rider's pull period.
      3. Progressively applies similar filters for the 2nd, 3rd, ..., up to the 12th strongest rider,
         each time removing schedules where a rider's pull period exceeds that of the nth strongest rider.
    Filtering stops early the instant the number of remaining schedules drops below the solution space constraint.
    The function is intended to improve computational performance by discarding unlikely or suboptimal
    schedules before more expensive computations are performed. The savings can be spectacular, but are dependent
    on the number of riders and the distribution of their strengths. For example, for a case of nine riders 
    I studied, the number of pull plan period schedules were reduced from 1.9 million to just 220 where 
    the SOLUTION_SPACE_SIZE_CONSTRAINT = 1024. For eight riders using a similar case, the reduction was 
    from 390k to to 825 schedules!

    Args:
        paceline_rotation_alternatives_being_filtered (List[List[float]]): 
            List of candidate paceline rotation schedules, where each sequence is a list of pull periods (seconds).
        riders (List[ZsunRiderItem]): 
            List of rider objects, used to determine rider strength order for filtering.

    Returns:
        List[List[float]]: 
            The filtered list of paceline rotation schedules, reduced according to empirical rules.

    Notes:
        - Filtering is only applied if the number of input schedules exceeds the solution space size constraint.
        - The function is intended to improve computational performance by discarding unlikely or suboptimal
          schedules before more expensive computations are performed.
        - Filtering logic is based on empirical observations and may be tuned for best performance.
    """

    if len(paceline_rotation_alternatives_being_filtered) < SOLUTION_SPACE_SIZE_CONSTRAINT + 1:
        return paceline_rotation_alternatives_being_filtered

    filters: List[Callable[[List[List[float]], List[ZsunRiderItem]], List[List[float]]]] = [
        weaker_than_weakest_rider_filter,
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 1),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 2),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 3),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 4),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 5),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 6),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 7),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 8),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 9),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 10),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 11),
        lambda schedules, riders: stronger_than_nth_strongest_rider_filter(schedules, riders, 12),
    ]

    filtered_schedules = paceline_rotation_alternatives_being_filtered

    for filter_func in filters:
        filtered_schedules = filter_func(filtered_schedules, riders)
        if len(filtered_schedules) < SOLUTION_SPACE_SIZE_CONSTRAINT:
            return filtered_schedules

    return filtered_schedules


def generate_a_scaffold_of_the_total_solution_space(
    length_of_paceline: int,
    standard_pull_periods_seconds: List[float]
) -> List[List[float]]:
    """
    Generate all possible assignments of pull periods to a paceline.

    This function produces the Cartesian product of the allowed pull periods for each rider.
    For n riders and k allowed pull periods, it generates k^n possible schedules.
    Each sequence is a list of length n, where each element is a pull period assigned to a rider.
    This is not a permutation or combination in the strict combinatorial sense, but rather
    the full Cartesian product of options for each rider.

    Args:
        length_of_paceline (int) : number of riders in the paceline.
        standard_pull_periods_seconds (List[float]): Allowed pull durations (in seconds).

    Returns:
        List[List[float]]: All possible paceline rotation schedules as lists of pull periods.
    """
    all_schedules = [list(sequence) for sequence in itertools.product(standard_pull_periods_seconds, repeat=length_of_paceline)]
    return all_schedules


def compute_a_single_paceline_solution_complying_with_exertion_constraints(
    instruction: PacelineIngredientsItem,
    max_iter: int = 30
) -> PacelineComputationReport:
    """
    Computes a feasible paceline solution for a group of riders, subject to exertion and power constraints.

    This function uses a binary search to determine the maximum paceline speed at which all riders can
    complete their pulls without exceeding a specified exertion intensity factor or pull watts. 
    It iteratively tests increasing speeds, generating pull plans and checking for constraint 
    violations, until it finds the highest feasible speed within the given desired_precision_kph and iteration limits.

    Args:
        instruction (PacelineIngredientsItem): Dataclass containing all input parameters for the computation.
        desired_precision_kph (float, optional): Precision for the binary search on speed (default: 0.01).
        max_iter (int, optional): Maximum number of binary search iterations (default: 30).

    Returns:
        PacelineComputationReport: Dataclass containing the number of search iterations, the mapping of each rider
        to their computed RiderContributionItem, and the limiting rider (who first hit the exertion constraint, or None).
    """

    riders = instruction.riders_list
    standard_pull_periods_seconds = list(instruction.sequence_of_pull_periods_sec)
    lowest_conceivable_kph = instruction.pull_speeds_kph
    max_exertion_intensity_factor = instruction.max_exertion_intensity_factor

    # Initial lowest_bound_for_binary_search_kph and highest_bound_for_binary_search_kph bounds of speed for the binary search
    lowest_bound_for_binary_search_kph = truncate(lowest_conceivable_kph[0], 0)
    highest_bound_for_binary_search_kph = lowest_bound_for_binary_search_kph

    dict_of_rider_contributions: DefaultDict[ZsunRiderItem, RiderContributionItem] = defaultdict(RiderContributionItem)  # <-- Initialization


    # Find a highest_bound_for_binary_search_kph bound speed at which at least one rider's plan is invalid.
    # This is required for the binary search to work correctly.

    for _ in range(SAFE_NUM_OF_ITERATIONS_TO_FIND_UPPER_BOUND_CONSTRAINT_BUSTING_SPEED_KPH):
        cadidate_busting_speed_as_array_kph = [highest_bound_for_binary_search_kph] * len(riders)
        dict_of_rider_contributions = populate_paceline_solution_alternative(
            riders, standard_pull_periods_seconds, cadidate_busting_speed_as_array_kph, max_exertion_intensity_factor
        )
        if any(answer.invalidation_reason for answer in dict_of_rider_contributions.values()):
            break
        highest_bound_for_binary_search_kph += INCREASE_IN_SPEED_PER_ITERATION_KPH
    else:
        # If we never find an highest_bound_for_binary_search_kph bound, just return the last result
        return PacelineComputationReport(
            num_compute_iterations_performed=1,
            rider_contributions=dict_of_rider_contributions,
            rider_that_breeched_contraints=None
        )

    # Do the binary search. The concept is to search by bouncing back and forth between  
    # lowest_bound_for_binary_search_kph and highest_bound_for_binary_search_kph
    # to zero in on the precise speed that invalidates the contribution of any one or more riders.
    # Invalidation is determined inside populate_paceline_solution_alternative(..)


    compute_iterations_performed: int = 0 # Number of iterations performed in the binary search, for reporting purposes
    constraint_busting_rider: Union[None, ZsunRiderItem] = None

    while (highest_bound_for_binary_search_kph - lowest_bound_for_binary_search_kph) > DESIRED_PRECISION_KPH and compute_iterations_performed < max_iter:
        mid = (lowest_bound_for_binary_search_kph + highest_bound_for_binary_search_kph) / 2
        cadidate_busting_speed_as_array_kph = [mid] * len(riders)
        dict_of_rider_contributions = populate_paceline_solution_alternative(
            riders, standard_pull_periods_seconds, cadidate_busting_speed_as_array_kph, max_exertion_intensity_factor)
        compute_iterations_performed += 1
        if any(answer.invalidation_reason for answer in dict_of_rider_contributions.values()):
            highest_bound_for_binary_search_kph = mid
            constraint_busting_rider = next(rider for rider, answer in dict_of_rider_contributions.items() if answer.invalidation_reason)
        else:
            lowest_bound_for_binary_search_kph = mid

    # Use the halting (highest_bound_for_binary_search_kph) speed after binary search
    precise_constraint_busting_speed_as_array = [highest_bound_for_binary_search_kph] * len(riders)
    dict_of_rider_contributions = populate_paceline_solution_alternative(
        riders, standard_pull_periods_seconds, precise_constraint_busting_speed_as_array, max_exertion_intensity_factor)
    if any(answer.invalidation_reason for answer in dict_of_rider_contributions.values()):
        constraint_busting_rider = next(rider for rider, answer in dict_of_rider_contributions.items() if answer.invalidation_reason)
    else:
        constraint_busting_rider = None

    return PacelineComputationReport(
        num_compute_iterations_performed    = compute_iterations_performed,
        rider_contributions                 = dict_of_rider_contributions,
        rider_that_breeched_contraints                      = constraint_busting_rider
    )


def summarize_paceline_rotation_solutions(
    solutions: List[PacelineComputationReport],
    num_of_alternatives_examined: int,
    time_taken_to_compute: float
) -> PacelineSolutionsComputationReport:
    """
    Summarize and select the most desirable paceline solutions from a list of computed alternatives.

    This function analyzes a list of PacelineComputationReport objects, each representing a computed paceline solution,
    and identifies two key solutions: the one with the highest speed and the one with the lowest std_deviation_of_intensity_factors
    (standard deviation) of intensity factors among riders. It also aggregates statistics such as the total number
    of compute iterations performed and the total computation time.

    Args:
        solutions: List of PacelineComputationReport objects, each representing a computed paceline solution.
        num_of_alternatives_examined: The total number of candidate rotation sequences that were evaluated.
        time_taken_to_compute: The total time taken to compute all solutions, in seconds.

    Returns:
        PacelineSolutionsComputationReport: An object containing summary statistics and the most desirable solutions,
        specifically the highest speed and lowest std_deviation_of_intensity_factors solutions.

    Raises:
        RuntimeError: If no valid solution is found, or if either the highest speed or lowest std_deviation_of_intensity_factors solution is missing.

    Notes:
        - The function logs warnings for invalid or non-finite solutions.
        - The desirable solutions list will contain up to two solutions: [candidate_lowest_std_deviation, candidate_highest_speed].
    """

    highest_speed_paceline_solution = None
    candidate_highest_speed: float = float('-inf')
    lowest_std_deviation_paceline_solution = None
    candidate_lowest_std_deviation: float = float('inf')
    total_compute_iterations_performed = 0 

    for solution in solutions:

        total_compute_iterations_performed += solution.num_compute_iterations_performed

        if solution.rider_that_breeched_contraints is None:
            logger.warning(f"Invalid result in solutions list. No rider halted the attempt to compute solution: {solution}. ")
            continue

        paceline_speed_ceiling = solution.rider_contributions[solution.rider_that_breeched_contraints].speed_kph # criterion
        if not np.isfinite(paceline_speed_ceiling):
            logger.warning(f"Binary search iteration error. Non-finite paceline_speed_ceiling encountered: {paceline_speed_ceiling}")
            continue

        if paceline_speed_ceiling > candidate_highest_speed:
            candidate_highest_speed = paceline_speed_ceiling
            highest_speed_paceline_solution = solution # the meat

        rider_contibution_intensity_factors = [calculate_overall_intensity_factor_of_rider_contribution(rider, contribution) for rider, contribution in solution.rider_contributions.items()]

        if not rider_contibution_intensity_factors:
            logger.warning("No valid rider_contibution_intensity_factors in dict_of_rider_contributions.")
            continue

        std_deviation_of_intensity_factors = float(np.std(rider_contibution_intensity_factors)) # criterion

        if not np.isfinite(std_deviation_of_intensity_factors):
            logger.warning(f"Non-finite std_deviation_of_intensity_factors encountered: {std_deviation_of_intensity_factors}")
            continue

        if std_deviation_of_intensity_factors < candidate_lowest_std_deviation:
            candidate_lowest_std_deviation = std_deviation_of_intensity_factors
            lowest_std_deviation_paceline_solution = solution # the meat

    if highest_speed_paceline_solution is None and lowest_std_deviation_paceline_solution is None:
        raise RuntimeError("No valid solution found (both highest_speed_paceline_solution and lowest_std_deviation_paceline_solution are None)")
    elif highest_speed_paceline_solution is None:
        raise RuntimeError("search_for_paceline_rotation_solutions: No valid solution found (highest_speed_paceline_solution is None)")
    elif lowest_std_deviation_paceline_solution is None:
        raise RuntimeError("search_for_paceline_rotation_solutions: No valid solution found (lowest_std_deviation_paceline_solution is None)")

    desirable_solutions = [lowest_std_deviation_paceline_solution, highest_speed_paceline_solution]

    return PacelineSolutionsComputationReport(
        candidate_rotation_sequences_count       = num_of_alternatives_examined,
        total_compute_iterations_performed_count = total_compute_iterations_performed,
        computational_time                       = time_taken_to_compute,
        solutions                                = desirable_solutions
    )


def search_for_paceline_rotation_solutions_using_serial_processing(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: List[List[float]]
) -> PacelineSolutionsComputationReport:
    """
    Perform an exhaustive serial search for optimal paceline pull plans given a set of riders and candidate pull period schedules.

    This function evaluates each candidate paceline rotation schedule in sequence, computing the resulting paceline solution
    for each. It collects all valid solutions, tracks the number of alternatives examined, and measures the total computation time.
    The function returns a summary report containing the most desirable solutions (highest speed and lowest std_deviation_of_intensity_factors) and statistics.

    Args:
        paceline_ingredients:                  PacelineIngredientsItem containing all input parameters for the computation except the schedules.
        paceline_rotation_sequence_alternatives: List of candidate pull period schedules to evaluate, where each schedule is a list of pull periods (seconds).

    Returns:
        PacelineSolutionsComputationReport: Summary report containing all solutions, the number of alternatives examined,
            total compute iterations, computation time, and the most desirable solutions.

    Raises:
        Exception: If an error occurs during the computation of a single paceline solution, it is logged and the process continues.

    Notes:
        - Logs a warning if the number of alternatives to be computed is very large.
        - Only valid solutions are included in the summary report.
        - This function is intended for use when the number of alternatives is small enough to be processed serially.
    """

    num_of_alternatives_examined: int = len(paceline_rotation_sequence_alternatives)

    if num_of_alternatives_examined > 10_000:
        logger.warning(f"Warning. Number of alternatives to be computed and evaluated is very large: {num_of_alternatives_examined}")

    paceline_description = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)


    solutions: List[PacelineComputationReport] = []

    start_time = time.perf_counter()

    for sequence in paceline_rotation_sequence_alternatives:
        try:
            paceline_description.sequence_of_pull_periods_sec = list(sequence)

            result = compute_a_single_paceline_solution_complying_with_exertion_constraints(paceline_description)

            solutions.append(PacelineComputationReport(
                num_compute_iterations_performed    = result.num_compute_iterations_performed,
                rider_contributions                    = result.rider_contributions,
                rider_that_breeched_contraints                      = result.rider_that_breeched_contraints
            ))
        except Exception as exc:
            logger.error(f"Exception in function compute_a_single_paceline_solution_complying_with_exertion_constraints(): {exc}")

    end_time = time.perf_counter()
    time_taken_to_compute = end_time - start_time

    return summarize_paceline_rotation_solutions(
        solutions,
        num_of_alternatives_examined,
        time_taken_to_compute
    )


def search_for_paceline_rotation_solutions_using_parallel_workstealing(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: List[List[float]]
) -> PacelineSolutionsComputationReport:
    """
    Perform an exhaustive parallelized search for optimal paceline pull plans using a work-stealing process pool.

    This function evaluates each candidate paceline rotation schedule in parallel, distributing the computation
    across available CPU cores using a process pool. Each schedule is used to generate a PacelineIngredientsItem,
    and the resulting solutions are collected and summarized. The function returns a report containing the most
    desirable solutions (highest speed and lowest std_deviation_of_intensity_factors) and summary statistics.

    Args:
        paceline_ingredients:                  PacelineIngredientsItem containing all input parameters for the computation except the schedules.
        paceline_rotation_sequence_alternatives: List of candidate pull period schedules to evaluate, where each schedule is a list of pull periods (seconds).

    Returns:
        PacelineSolutionsComputationReport: Summary report containing all solutions, the number of alternatives examined,
            total compute iterations, computation time, and the most desirable solutions.

    Notes:
        - Logs a warning if the number of alternatives to be computed is very large.
        - Invalid or incomplete results are skipped and logged as warnings.
        - This function is intended for use when the number of alternatives is large enough to benefit from parallel processing.
    """


    num_of_alternatives_examined: int = len(paceline_rotation_sequence_alternatives)

    if num_of_alternatives_examined > 10_000:
        logger.warning(f"Warning. Number of alternatives to be computed and evaluated is very large: {num_of_alternatives_examined}")

    paceline_description = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)


    list_of_instructions: List[PacelineIngredientsItem] = []    
    
    for sequence in paceline_rotation_sequence_alternatives:
        paceline_description.sequence_of_pull_periods_sec = list(sequence)
        list_of_instructions.append(copy.deepcopy(paceline_description))

    solutions: List[PacelineComputationReport] = []

    start_time = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_params = {
            executor.submit(compute_a_single_paceline_solution_complying_with_exertion_constraints, p): p
            for p in list_of_instructions
        }
        for future in concurrent.futures.as_completed(future_to_params):
            try:
                result = future.result()
                if (result is None or
                    not hasattr(result, "rider_contributions") or
                    result.rider_contributions is None or
                    result.rider_that_breeched_contraints is None or
                    not isinstance(result.rider_contributions, dict)):
                    logger.warning(f"Skipping invalid result: {result}")
                    continue
                solutions.append(PacelineComputationReport(
                    num_compute_iterations_performed=result.num_compute_iterations_performed,
                    rider_contributions=result.rider_contributions,
                    rider_that_breeched_contraints=result.rider_that_breeched_contraints
                ))
            except Exception as exc:
                logger.error(f"Exception in function compute_a_single_paceline_solution_complying_with_exertion_constraints(): {exc}")

    end_time = time.perf_counter()
    time_taken_to_compute = end_time - start_time

    return summarize_paceline_rotation_solutions(
        solutions,
        num_of_alternatives_examined,
        time_taken_to_compute
    )


def search_for_paceline_rotation_solutions_using_most_performant_algorithm(
    paceline_ingredients: PacelineIngredientsItem
) -> PacelineSolutionsComputationReport:
    """
    Determine the optimal paceline pull plans for a set of riders using the most efficient available algorithm.

    This function generates all possible paceline rotation alternatives based on the provided riders and pull periods,
    then applies empirical filters to reduce the solution space. Depending on the number of remaining alternatives,
    it selects either serial or parallel processing to compute and evaluate all feasible paceline solutions.
    The function returns a summary report containing the most desirable solutions (highest speed and lowest std_deviation_of_intensity_factors)
    and relevant statistics.

    Args:
        paceline_ingredients: PacelineIngredientsItem containing all input parameters for the computation,
            including the list of riders, allowed pull periods, target speeds, and exertion constraints.

    Returns:
        PacelineSolutionsComputationReport: Summary report containing all solutions, the number of alternatives examined,
            total compute iterations, computation time, and the most desirable solutions.

    Raises:
        ValueError: If required input parameters are missing or invalid (e.g., no riders, no pull periods, or non-finite values).

    Notes:
        - The function automatically chooses between serial and parallel processing based on the size of the solution space.
        - Empirical filters are applied to reduce computational load before solution evaluation.
        - This is the recommended entry point for finding optimal paceline solutions in production code.
    """

    if not paceline_ingredients.riders_list:
        raise ValueError("No riders provided to search_for_paceline_rotation_solutions_using_serial_processing.")
    if not paceline_ingredients.sequence_of_pull_periods_sec:
        raise ValueError("No standard pull durations provided to search_for_paceline_rotation_solutions_using_serial_processing.")
    if any(d <= 0 or not np.isfinite(d) for d in paceline_ingredients.sequence_of_pull_periods_sec):
        raise ValueError("All standard pull durations must be positive and finite.")
    if not paceline_ingredients.pull_speeds_kph or not np.isfinite(paceline_ingredients.pull_speeds_kph[0]) or paceline_ingredients.pull_speeds_kph[0] <= 0:
        raise ValueError("binary_search_seed must be positive and finite.")

    all_conceivable_paceline_rotation_alternatives= generate_a_scaffold_of_the_total_solution_space(
        len(paceline_ingredients.riders_list), paceline_ingredients.sequence_of_pull_periods_sec)

    paceline_rotation_sequence_alternatives = radically_shrink_the_solution_space(
        all_conceivable_paceline_rotation_alternatives, paceline_ingredients.riders_list)

    if len(paceline_rotation_sequence_alternatives) < SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD:
        return search_for_paceline_rotation_solutions_using_serial_processing(paceline_ingredients, paceline_rotation_sequence_alternatives)
    else:
        return search_for_paceline_rotation_solutions_using_parallel_workstealing(paceline_ingredients, paceline_rotation_sequence_alternatives)


def main01():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import STANDARD_PULL_PERIODS_SEC
    from jgh_formulae08 import search_for_paceline_rotation_solutions_using_parallel_workstealing, search_for_paceline_rotation_solutions_using_serial_processing
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

    all_conceivable_paceline_rotation_schedules = generate_a_scaffold_of_the_total_solution_space(len(riders), STANDARD_PULL_PERIODS_SEC)

    plan_params = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec     = STANDARD_PULL_PERIODS_SEC,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )

    # Serial run as the base case
    serial_result = search_for_paceline_rotation_solutions_using_serial_processing(plan_params, all_conceivable_paceline_rotation_schedules)
    logger.info(f"Base-case: ordinary run compute time (measured): {round(serial_result.computational_time, 2)} seconds")

    # Parallel run
    parallel_result = search_for_paceline_rotation_solutions_using_parallel_workstealing(plan_params, all_conceivable_paceline_rotation_schedules)
    logger.info(f"Test-case: parallel run compute time (measured): {round(parallel_result.computational_time,2)} seconds")

    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Serial run:\n")
    report_lines.append(f"  Compute time (measured): {round(serial_result.computational_time, 2)} seconds\n")
    report_lines.append("Parallel run (work-stealing):\n")
    report_lines.append(f"  Compute time (measured): {round(parallel_result.computational_time,2)} seconds\n")
    report_lines.append(f"Time saved by parallelisation: {round(serial_result.computational_time - parallel_result.computational_time, 2)} seconds")
    report_lines.append("\n")

    logger.info("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Serial", "Compute Time (s)": serial_result.computational_time},
        {"Method": "Parallel", "Compute Time (s)": parallel_result.computational_time},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title("Compute Time: Serial vs Parallel")
    plt.ylabel("Compute Time (seconds)")
    plt.xlabel("Method")
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}.png")
    plt.show()
    logger.info(f"Bar chart saved to {save_filename_without_ext}.png")


def main02():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import STANDARD_PULL_PERIODS_SEC
    from jgh_formulae08 import search_for_paceline_rotation_solutions_using_most_performant_algorithm

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    save_filename_without_ext = f"run_optimised_filters_and_parallelisation_with_{len(riders)}_riders"

    logger.info(f"Testing: running sensible empirically-measured thresholds for no-filtering -> filtering and serial -> parallel processing with {len(riders)} riders")

    params = PacelineIngredientsItem(
        riders_list                  = riders,
        sequence_of_pull_periods_sec    = STANDARD_PULL_PERIODS_SEC,
        pull_speeds_kph              = [30.0] * len(riders),
        max_exertion_intensity_factor= 0.95
    )

    optimised_result = search_for_paceline_rotation_solutions_using_most_performant_algorithm(params)
    logger.info(f"Test-case: compute time using most performant algorithm (measured): {round(optimised_result.computational_time,2)} seconds")

    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Most performant algorithm:\n")
    report_lines.append(f"  Compute time (measured): {round(optimised_result.computational_time,2)} seconds\n")
    report_lines.append("\n")

    logger.info("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

if __name__ == "__main__":
    # main01()    
    main02()