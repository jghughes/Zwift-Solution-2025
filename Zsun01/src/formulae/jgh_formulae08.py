"""
Module: jgh_formulae08
======================

Advanced algorithms and utilities for computing optimal paceline solutions for cycling teams,
with a focus on exertion-constrained rotations. Supports both serial and parallel processing
to efficiently evaluate large numbers of candidate paceline rotation sequences, leveraging
work-stealing for multi-core performance.

Key Features:
-------------
- Calculates upper and lower bounds for paceline speed under exertion constraints.
- Generates all feasible paceline rotation sequences and prunes the solution space.
- Computes rider work assignments, exertions, and contributions for each solution.
- Supports both serial and parallel (process pool) computation strategies.
- Selects optimal solutions for several categories: simple (30s/60s), balanced, tempo, and drop.
- Provides benchmarking and visualization tools for performance analysis.
- Includes robust validation and error handling for input parameters and solutions.

Usage:
------
Import this module and use the main function `generate_package_of_paceline_solutions`
to compute and select optimal paceline strategies for a given set of riders and
pull periods. Use the benchmarking functions (`test01`, `test02`) to compare serial
and parallel processing performance and the impact of solution space pruning.

Example:
--------
    from jgh_formulae08 import generate_package_of_paceline_solutions
    result = generate_package_of_paceline_solutions(paceline_ingredients)
    print(result)

Notes:
------
- Logging is restricted to the main thread; do not use logging inside functions
  called by ProcessPoolExecutor.
- The module is designed for extensibility and robust error handling.
- For large teams or many pull-period options, computation time may be significant.

Author: GitHub Copilot
Date: August 25, 2025
"""

import os

import concurrent.futures
import time
from collections import defaultdict
from copy import deepcopy
from tabulate import tabulate
from typing import Dict, List, Tuple

import numpy as np
from numpy.typing import NDArray

from paceline_modelling_items import (
    PacelineComputationReportItem,
    PacelineIngredientsItem,
    PackageOfPacelineComputationReportItem,
    RiderContributionItem,
    WorthyCandidateSolutionItem,
)
from paceline_display_objects import (
    PacelinePlanTypeEnum,
    PackageOfPacelineComputationReportDisplayObject,
)
from constants import (
    ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL,
    SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD,
    PULL_DURATION_OPTIONS_SEC,
    DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC
)
from jgh_enums import PacelinePlanTypeEnum
from jgh_formatting import (
    format_number_1dp,
    format_number_with_comma_separators,
    format_pretty_duration_hms,
    truncate,
)
from jgh_formulae03 import (
    calculate_dispersion_of_intensity_of_effort,
    # solve_for_lower_bound_paceline_speed,
    # solve_for_lower_bound_paceline_speed_at_one_hour_watts,
    calculate_overall_average_speed_of_paceline_kph,
    # solve_for_upper_bound_paceline_speed,
    # solve_for_upper_bound_paceline_speed_at_one_hour_watts,
    generate_all_suitable_paceline_rotation_sequences_in_the_solution_space,
    solve_for_proxy_standard_30sec_pull_speed_for_all_riders,
    solve_for_speed_at_one_hour_watts_for_all_riders
)
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_rider_contributions
from jgh_number import safe_divide
from rider_compute_item import RiderComputeItem

# CRUCIAL WARNING. AT NO STAGE USE LOGGING STATEMENTS DIRECTLY OR INDIRECTLY INSIDE ANY CODE CALLED WITHIN THE ProcessPoolExecutor. 
# IT WILL LEAD TO GARBAGE OUTPUT. THE LOGGER CANT HANDLE MULTIPLE THREADS IN MULTIPLE CORES WRITING TO IT AT 
# THE SAME TIME. USE LOGGING ONLY IN THE MAIN THREAD. EVEN WHEN DEBUGGING, THE PROBLEM IS INSURMOUNTABLE. 

def log_multiline(lines: list[str]) -> None:
    print("\n".join(lines))

def show_table_of_standard_proxy_speeds_for_all_riders(riders: List[RiderComputeItem]) -> None:
    print(f"\nILLUSTRATIVE RIDER CAPABILITIES : (gradient = {DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC}%) : Intensity Factor = 1.0\n")
    names: List[str] = [rider.name for rider in riders]
    zFTPs: List[float] = [round(safe_divide(rider.velo_zwiftpower_zFTP_watts, rider.weight_kg), 1) for rider in riders]
    proxy_standard_30sec_pull_speeds_dict = solve_for_proxy_standard_30sec_pull_speed_for_all_riders(riders, DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC)
    proxy_standard_30sec_pull_speed_values: List[float] = [round(proxy_standard_30sec_pull_speeds_dict[rider], 1) for rider in riders]
    standard_solo_speeds_at_one_hour_watts__dict = solve_for_speed_at_one_hour_watts_for_all_riders(riders, DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC)
    standard_solo_speeds_at_one_hour_values: List[float] = [round(standard_solo_speeds_at_one_hour_watts__dict[rider], 1) for rider in riders]
    table = zip(names, zFTPs, proxy_standard_30sec_pull_speed_values, standard_solo_speeds_at_one_hour_values)
    print(tabulate(table, headers=["Rider", "zFTP (w/kg)", "30sec Pull (kph)", "1 Hour Solo (kph)"]))

def show_workload_suffix_message() -> None:
    message_lines = [
        f"\nzFTP metrics are displayed, but play no role in computations.",
        "Pull capacities are obtained from individual 90-day best power graphs on ZwiftPower.",
        "\n30 second pull capacity = 3.5 minute pull-curve ordinate",
        "1 minute pull capacity  =  5 minute pull-curve ordinate",
        "2 minute pull capacity  = 12 minute pull-curve ordinate",
        "3 minute pull capacity  = 15 minute pull-curve ordinate",
        "4 minute pull capacity  = 18 minute pull-curve ordinate",
        "\nRiders with superior pull capacity are prioritised for longer pulls.",
        "The speed of the paceline is constant and does not vary from one rider to the next.",
        "The pull capacity of the slowest puller governs the speed, leaving room for upside.",
        "Based on data from Zwiftpower from DaveK. Some ZSUN riders have more comprehensive data than others.",
    ]
    log_multiline(message_lines)

def populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(
    riders:                        List[RiderComputeItem],
    standard_pull_periods_seconds: List[float],
    pull_speeds_kph:               List[float],
    slope:                         float,
    max_exertion_intensity_factor: float
) -> Tuple[float, Dict[RiderComputeItem, RiderContributionItem]]:
    """
    Computes the contributions of each rider in a single paceline solution.

    This function determines the work assignments, exertions, and final contributions for each rider
    based on the provided pull periods, target speeds, slope, and maximum allowed exertion intensity.
    It returns the overall average speed of the paceline and a mapping of each rider to their computed contribution.

    Args:
        riders: List of RiderComputeItem objects representing the riders in the paceline.
        standard_pull_periods_seconds: List of pull durations (in seconds) for each rider.
        pull_speeds_kph: List of target pull speeds (in kph) for each rider.
        slope: The slope of the terrain (in percentage).
        max_exertion_intensity_factor: Maximum allowed exertion intensity factor for any rider.

    Returns:
        Tuple containing:
            - overall_av_speed_of_paceline (float): The computed average speed of the paceline (kph).
            - dict_of_rider_contributions (Dict[RiderComputeItem, RiderContributionItem]):
                Mapping of each rider to their computed RiderContributionItem, including effort metrics and constraint violations.
    """
    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, standard_pull_periods_seconds, pull_speeds_kph, slope)
        
    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    overall_av_speed_of_paceline = calculate_overall_average_speed_of_paceline_kph(dict_of_rider_exertions)

    dict_of_rider_contributions = populate_rider_contributions(dict_of_rider_exertions, max_exertion_intensity_factor)

    return overall_av_speed_of_paceline, dict_of_rider_contributions

def solve_for_a_single_paceline_solution_complying_with_exertion_constraints_using_binary_search(paceline_ingredients: PacelineIngredientsItem,
) -> PacelineComputationReportItem:
    """
    Finds the highest paceline speed at which at least one rider's exertion intensity
    constraint is exactly met, using a two-phase binary search.

    Phase 1 — Upper-bound scan:
        Starting from pull_speeds_kph[0] (the caller-supplied lower bound, truncated to
        3 decimal places), the speed is stepped up by CHUNK_OF_KPH_PER_ITERATION (5.0 kph)
        on each iteration until at least one rider's effort_constraint_violation_reason is
        non-empty, establishing a safe upper bound.  The loop is capped at
        SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND (20) iterations.
        If no violation is found within that cap, the function returns immediately with
        algorithm_ran_to_completion=False and sentinel values
        (calculated_average_speed_of_paceline_kph=0,
        calculated_dispersion_of_intensity_of_effort=999).

    Phase 2 — Binary search:
        The interval [lower_bound, upper_bound] is halved on each iteration.
        The mid-point is tested: if any rider is in violation the upper bound is moved
        down to mid-point; otherwise the lower bound is moved up.  The loop terminates
        when the interval width falls below REQUIRED_PRECISION_OF_SPEED_KPH (0.05 kph)
        or the combined iteration count (Phase 1 + Phase 2) reaches
        MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION (30).

    Answer:
        The converged upper bound is the answer — the lowest speed at which at least one
        rider is in violation.  A final call to
        populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(..)
        at that speed produces the definitive rider contributions and the reported paceline
        average speed.

    Args:
        paceline_ingredients (PacelineIngredientsItem): All inputs for the computation:
            - riders_list (List[RiderComputeItem]): The riders in the paceline.
            - sequence_of_pull_periods_sec (List[float]): Pull duration (seconds) for each rider.
            - pull_speeds_kph (List[float]): Only pull_speeds_kph[0] is consumed, as the
              starting lower bound for the speed search.  Remaining elements are ignored.
            - slope_pc (float): Road slope as a percentage (e.g. 5.0 for 5 %). Defaults to 0.0.
            - max_exertion_intensity_factor (float): The ceiling intensity factor
              (normalised_watts / one-hour_watts) permitted for any rider.

    Returns:
        PacelineComputationReportItem: The computation result, containing:
            - algorithm_ran_to_completion (bool): True if the binary search converged
              normally; False if Phase 1 exhausted its iteration cap without finding a
              violation.
            - compute_iterations_performed_count (int): Total iterations across both phases.
              Does not count the final confirmation call.
            - computational_time (float): Wall-clock elapsed time in seconds.
            - exertion_intensity_constraint_used (float): The max_exertion_intensity_factor
              value that was applied.
            - calculated_average_speed_of_paceline_kph (float): The converged paceline speed.
              0 if algorithm_ran_to_completion is False.
            - calculated_dispersion_of_intensity_of_effort (float): Spread of intensity
              factors across riders at the converged speed.  999 if
              algorithm_ran_to_completion is False.
            - rider_contributions (Dict[RiderComputeItem, RiderContributionItem]): Each
              rider's detailed effort metrics and constraint-violation status at the
              converged speed.

    WARNING: DO NOT USE LOGGING IN THIS FUNCTION OR ANY FUNCTIONS IT CALLS DIRECTLY OR
    INDIRECTLY.  IT IS CALLED BY ProcessPoolExecutor.  ANY LOGGING OFF THE MAIN THREAD
    WILL PRODUCE GARBAGE OUTPUT.
    """
    start_time = time.perf_counter()

    # get ready
    riders = paceline_ingredients.riders_list
    standard_pull_periods_seconds: List[float] = list(paceline_ingredients.sequence_of_pull_periods_sec)
    lowest_conceivable_kph = truncate(paceline_ingredients.pull_speeds_kph[0],3) #This line sets the starting lower bound for the paceline speed search, using the first provided speed (formatted to three decimal places), ensuring the algorithm begins with a valid, precise, and user-supplied minimum speed
    # print (f"DEBUG: lowest conceivable speed for the paceline is {lowest_conceivable_kph}kph")
    max_exertion_intensity_factor = paceline_ingredients.max_exertion_intensity_factor
    slope = paceline_ingredients.slope_pc 
    num_riders = len(riders)
    lower_bound_for_next_search_iteration_kph = lowest_conceivable_kph
    upper_bound_for_next_search_iteration_kph = lower_bound_for_next_search_iteration_kph
    upper_bound_scan_iterations: int = 0 
    binary_search_iterations: int = 0

    dict_of_rider_contributions: Dict[RiderComputeItem, RiderContributionItem] = defaultdict(RiderContributionItem)  # part of the answer

    # 1. Find Safe Upper Bound for binary-search.

    CHUNK_OF_KPH_PER_ITERATION = 5.0
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 200 # arbitrary. we can achieve huge speeds on steep slopes whe CdA is et to zero in testing

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders, slope, max_exertion_intensity_factor)

        if any(contribution.effort_constraint_violation_reason for contribution in dict_of_rider_contributions.values()):
            break # break out of the loop as soon as we successfuly find a speed that violates at least one rider's ability
        
        upper_bound_for_next_search_iteration_kph += CHUNK_OF_KPH_PER_ITERATION

        upper_bound_scan_iterations += 1
    else:
        # If we never find an upper_bound_for_next_search_iteration_kph bound, just bale and return the last result
        return PacelineComputationReportItem(
            algorithm_ran_to_completion                     = False,  # We did not run to completion, we hit the max iterations
            exertion_intensity_constraint_used              = paceline_ingredients.max_exertion_intensity_factor,
            compute_iterations_performed_count              = upper_bound_scan_iterations,
            computational_time                              = time.perf_counter() - start_time,
            calculated_average_speed_of_paceline_kph        = 0,
            calculated_dispersion_of_intensity_of_effort    = 999,
            rider_contributions                             = dict_of_rider_contributions,
        )

    # 2. Do binary-search.

    REQUIRED_PRECISION_OF_SPEED_KPH = 0.05 
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 100 # i have no idea if this is adequate or not

    while (upper_bound_for_next_search_iteration_kph - lower_bound_for_next_search_iteration_kph) > REQUIRED_PRECISION_OF_SPEED_KPH and binary_search_iterations < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:

        mid_point_kph =safe_divide( (lower_bound_for_next_search_iteration_kph + upper_bound_for_next_search_iteration_kph), 2)

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [mid_point_kph] * num_riders, slope, max_exertion_intensity_factor)

        binary_search_iterations += 1

        if any(rider_contribution.effort_constraint_violation_reason for rider_contribution in dict_of_rider_contributions.values()):
            upper_bound_for_next_search_iteration_kph = mid_point_kph
        else:
            lower_bound_for_next_search_iteration_kph = mid_point_kph

    # Knowing the speed, we can rework the contributions and thus the solution
    speed_of_paceline,dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders , slope, max_exertion_intensity_factor)

    answer = PacelineComputationReportItem(
        algorithm_ran_to_completion                 = True,  
        compute_iterations_performed_count          = upper_bound_scan_iterations + binary_search_iterations,
        computational_time                          = time.perf_counter() - start_time,
        exertion_intensity_constraint_used          = paceline_ingredients.max_exertion_intensity_factor,
        calculated_average_speed_of_paceline_kph    = speed_of_paceline,
        calculated_dispersion_of_intensity_of_effort= calculate_dispersion_of_intensity_of_effort(dict_of_rider_contributions),
        rider_contributions                         = dict_of_rider_contributions,

    )

    return answer

def generate_paceline_solutions_using_serial_processing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: NDArray[np.float64]
) -> List[PacelineComputationReportItem]:
    """
    Computes paceline solutions for a set of candidate pull period sequences using serial (single-threaded) processing.

    This function evaluates each candidate paceline rotation schedule one at a time, generating a solution for each by
    invoking the exertion-constrained paceline solver. For each alternative, it constructs a PacelineIngredientsItem
    with the specified pull periods, computes the optimal paceline speed and rider contributions, and collects the results.
    Any exceptions encountered during computation are logged and the corresponding alternative is skipped.

    Args:
        paceline_ingredients (PacelineIngredientsItem):
            The base input parameters for the computation, including the list of riders, initial pull speeds,
            and exertion constraints. The pull periods are overridden for each alternative.
        paceline_rotation_sequence_alternatives (NDArray[np.float64]):
            A 2D numpy array where each row is a candidate pull period schedule (list of pull durations in seconds).

    Returns:
        List[PacelineComputationReportItem]:
            A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - This function processes alternatives sequentially and is intended for use when the number of alternatives is small.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - For large numbers of alternatives, consider using parallel processing for improved performance.
        - Logging is performed in the main thread and is safe in this function.
    """
    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        slope_pc                        = paceline_ingredients.slope_pc,
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)

    paceline_computation_reports: List[PacelineComputationReportItem] = []

    for sequence in paceline_rotation_sequence_alternatives:
        try:
            paceline_ingredients.sequence_of_pull_periods_sec = list(sequence)
            result = solve_for_a_single_paceline_solution_complying_with_exertion_constraints_using_binary_search(paceline_ingredients)
            answer = PacelineComputationReportItem(
                algorithm_ran_to_completion                 = result.algorithm_ran_to_completion,
                compute_iterations_performed_count          = result.compute_iterations_performed_count,
                exertion_intensity_constraint_used          = paceline_ingredients.max_exertion_intensity_factor,
                calculated_average_speed_of_paceline_kph    = result.calculated_average_speed_of_paceline_kph,
                calculated_dispersion_of_intensity_of_effort = calculate_dispersion_of_intensity_of_effort(result.rider_contributions),
                rider_contributions                         = result.rider_contributions,
            )

            paceline_computation_reports.append(answer)

        except Exception as exc:
            # serial processing, so we can log the error, logging OK
            print(f"Exception in function generate_paceline_solutions_using_serial_processing_algorithm(): {exc}")

    return paceline_computation_reports

def generate_paceline_solutions_using_parallel_workstealing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: NDArray[np.float64]
) -> List[PacelineComputationReportItem]:
    """
    Computes paceline solutions for multiple candidate pull period sequences using parallel processing with a work-stealing process pool.

    This function distributes the evaluation of each candidate paceline rotation schedule across available CPU cores using a process pool,
    allowing for efficient computation when the number of alternatives is large. For each alternative, it constructs a PacelineIngredientsItem
    with the specified pull periods, computes the optimal paceline speed and rider contributions, and collects the results. Invalid or incomplete
    results are skipped. Logging is only performed in the main thread; do not use logging in any code executed by the ProcessPoolExecutor.

    Args:
        paceline_ingredients (PacelineIngredientsItem):
            The base input parameters for the computation, including the list of riders, initial pull speeds,
            and exertion constraints. The pull periods are overridden for each alternative.
        paceline_rotation_sequence_alternatives (NDArray[np.float64]):
            A 2D numpy array where each row is a candidate pull period schedule (list of pull durations in seconds).

    Returns:
        List[PacelineComputationReportItem]:
            A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - This function is intended for use when the number of alternatives is large enough to benefit from parallel processing.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - Invalid or incomplete results are logged as warnings and not included in the output list.
        - Logging must not be used in any function executed by the ProcessPoolExecutor to avoid output corruption.
    """
    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        slope_pc                        = paceline_ingredients.slope_pc,   
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)

    list_of_instructions: List[PacelineIngredientsItem] = []    
    
    for sequence in paceline_rotation_sequence_alternatives:
        paceline_ingredients.sequence_of_pull_periods_sec = list(sequence)
        list_of_instructions.append(deepcopy(paceline_ingredients))

    paceline_computation_reports: List[PacelineComputationReportItem] = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_params = {
            executor.submit(solve_for_a_single_paceline_solution_complying_with_exertion_constraints_using_binary_search, p): p
            for p in list_of_instructions
        }
        for future in concurrent.futures.as_completed(future_to_params):
            try:
                result = future.result()

                answer = PacelineComputationReportItem(
                    algorithm_ran_to_completion              = result.algorithm_ran_to_completion,
                    compute_iterations_performed_count       = result.compute_iterations_performed_count,
                    exertion_intensity_constraint_used       = paceline_ingredients.max_exertion_intensity_factor,
                    calculated_average_speed_of_paceline_kph = result.calculated_average_speed_of_paceline_kph,
                    calculated_dispersion_of_intensity_of_effort = calculate_dispersion_of_intensity_of_effort(result.rider_contributions),
                    rider_contributions                      = result.rider_contributions,
                )
                paceline_computation_reports.append(answer)
            except Exception as exc:
                print(f"Exception in function generate_paceline_solutions_using_parallel_workstealing_algorithm(): {exc}")


    return paceline_computation_reports

def generate_paceline_solutions_using_serial_and_parallel_algorithms(
    paceline_ingredients: PacelineIngredientsItem,
    rotation_sequences: NDArray[np.float64]
) -> List[PacelineComputationReportItem]:
    """
    Computes paceline solutions for a set of candidate pull period sequences using either serial or parallel processing, 
    automatically selecting the most efficient strategy based on the number of alternatives.

    This function evaluates each candidate paceline rotation schedule to determine the optimal paceline speed and rider 
    contributions under exertion constraints. For a small number of alternatives, it uses serial (single-threaded) 
    processing; for larger sets, it leverages parallel work-stealing to utilize multiple CPU cores for improved performance.

    Args:
        paceline_ingredients (PacelineIngredientsItem): 
            The base input parameters for the computation, including the list of riders, initial pull speeds, 
            and exertion constraints. The pull periods are overridden for each alternative.
        rotation_sequences (NDArray[np.float64]): 
            A 2D numpy array where each row is a candidate pull period schedule (list of pull durations in seconds).

    Returns:
        List[PacelineComputationReportItem]: 
            A list of computation reports, one for each successfully evaluated alternative. Each report contains 
            the number of compute iterations performed and the computed rider contributions.

    Notes:
        - The function chooses serial or parallel processing based on the SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD constant.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - For large numbers of alternatives, parallel processing can significantly reduce computation time.
        - Logging is only performed in the main thread; do not use logging in code executed by the ProcessPoolExecutor.

    """
    if len(rotation_sequences) < SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD:
        return generate_paceline_solutions_using_serial_processing_algorithm(paceline_ingredients, rotation_sequences)
    else:
        return generate_paceline_solutions_using_parallel_workstealing_algorithm(paceline_ingredients, rotation_sequences)

def validate_paceline_ingredients(paceline_ingredients: PacelineIngredientsItem) -> None:
    """
    Validates the input PacelineIngredientsItem for paceline solution generation.
    Raises ValueError if any required field is missing or invalid.
    """
    if not paceline_ingredients.riders_list:
        raise ValueError("No riders provided to generate_paceline_solutions_using_serial_processing_algorithm.")
    if not paceline_ingredients.sequence_of_pull_periods_sec:
        raise ValueError("No standard pull durations provided to generate_paceline_solutions_using_serial_processing_algorithm.")
    if any(d < 0 or not np.isfinite(d) for d in paceline_ingredients.sequence_of_pull_periods_sec):
        raise ValueError("All standard pull durations must be positive and finite.")
    if (
        not paceline_ingredients.pull_speeds_kph
        or not np.isfinite(paceline_ingredients.pull_speeds_kph[0])
        or paceline_ingredients.pull_speeds_kph[0] <= 0
    ):
        raise ValueError("binary_search_seed must be positive and finite.")

def is_valid_solution(this_solution: PacelineComputationReportItem) -> bool:
    """
    Validates the solution's speed and dispersion.
    Returns True if both are finite and dispersion is not the error value (100).
    Logs a warning and returns False otherwise.
    """
    speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    if not np.isfinite(speed_kph):
        print(f"Binary search algorithm failure: iteration error: Non-finite speed_kph encountered: {speed_kph}")
        return False

    dispersion = this_solution.calculated_dispersion_of_intensity_of_effort
    if not np.isfinite(dispersion) or dispersion == 100:
        return False

    return True

def raise_error_if_any_solutions_missingV2(
    balanced_intensity_candidate: WorthyCandidateSolutionItem,
    everybody_pulls_hard_candidate: WorthyCandidateSolutionItem,
    race_candidate: WorthyCandidateSolutionItem
) -> None:
    """
    Raises RuntimeError if any required candidate solution is missing.
    """
    if (
        balanced_intensity_candidate.solution is None
        and everybody_pulls_hard_candidate.solution is None
        and race_candidate.solution is None
    ):
        raise RuntimeError("No valid solutions found for simple, balanced-IF, tempo, and drop solutions.")

    if everybody_pulls_hard_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (everybody_pull_hard_solution is None)")
    if balanced_intensity_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (balanced_intensity_solution is None)")
    if race_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (race_solution is None)")

def is_zero_dispersion_permissible_for_simple_solution(this_solution: PacelineComputationReportItem) -> bool:
    """
    Returns True if a dispersion of 0.0 is permissible for a 'simple solution' candidate.
    Rules:
      - If there are no riders or only one rider, zero dispersion is allowed.
      - If there are multiple riders, zero dispersion is only allowed if all pull durations
        and all pull watts are identical.
    """
    rider_contributions: List[RiderContributionItem] = list(this_solution.rider_contributions.values())
    num_riders = len(rider_contributions)
    if num_riders <= 1:
        return True
    # Check if all pull durations are the same
    durations: set[float] = {r.p1_duration for r in rider_contributions}
    watts: set[object] = {getattr(r, "p1_watts", None) for r in rider_contributions}
    return len(durations) == 1 and len(watts) == 1

def is_balanced_intensity_solution_candidate(this_solution: PacelineComputationReportItem,
        candidate: WorthyCandidateSolutionItem
    ) -> bool:
    """
    Determines if the given solution qualifies as a 'balanced solution' candidate.

    Definition:
        A 'balanced solution' is a paceline configuration that minimizes the standard deviation of rider intensity factors,
        distributing effort as evenly as possible among all riders, regardless of their absolute power or pull duration.

    Impact on Race Strategy:
        - Sustainability: Reduces the risk of burning out any single rider, helping the team maintain a strong pace for longer.
        - Inclusivity: Keeps the group together, as no one is pushed beyond their sustainable limit.
        - Performance: May not achieve the absolute fastest time, but increases the likelihood that all riders finish together and strong.
        - Best for: Endurance races, mixed-ability teams, or scenarios where group finish is a priority.

    Technical Description:
        - Checks that all riders have nonzero pull durations (`all_nonzero`).
        - Ensures the solution's dispersion is less than or equal to the current candidate's.
        - Allows zero dispersion only if all durations and watts are identical (using `is_zero_dispersion_permissible_for_simple_solution`).
        - A solution is considered superior and will replace the current candidate if:
            * It is has a lower dispersionthan the current candidate (regardless of speed), OR
            * It has the same dispersion as the current candidate and higher speed.
        - Returns True if all these conditions are met.
    """

    this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph # accessed only for debug logger, see below
    this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort
    all_nonzero = all(rider.p1_duration != 0.0 for rider in this_solution.rider_contributions.values())

    zero_dispersion_ok = (
        this_solution_dispersion != 0.0 or
        is_zero_dispersion_permissible_for_simple_solution(this_solution)
    )

    answer = (
        (
            (this_solution_dispersion < candidate.dispersion) or
            (this_solution_dispersion == candidate.dispersion and this_solution_speed_kph > candidate.speed_kph)
        )

        and zero_dispersion_ok
        and all_nonzero
        # and this_solution_speed_kph >= candidate.speed_kph # do not make this a requirement for a balanced solution! you will get unintended consequences!
    )
    # if answer:
    #     print(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_everyone_pull_hard_solution_candidate(this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem
) -> bool:
    """
    Determines if the given solution qualifies as a 'tempo solution' candidate.

    Definition:
        A 'tempo solution' is a paceline configuration where all riders contribute nonzero pulls (no one sits out),
        and the solution is optimized for the highest possible speed under this constraint.

    Impact on Race Strategy:
        - Speed: Maximizes team speed while maintaining full participation.
        - Motivation: Keeps all riders engaged, as everyone is contributing.
        - Efficiency: Stronger riders may take longer or harder pulls, optimizing the group's overall pace.
        - Best for: Competitive races where maximizing speed is important, but all riders are expected to contribute.

    Technical Description:
        - Checks that all riders have nonzero pull durations (`all_nonzero`).
        - Ensures the solution is at least as fast as the current candidate and has lower dispersion.
        - Allows zero dispersion only if all durations and watts are identical (using `is_zero_dispersion_permissible_for_simple_solution`).
        - A solution is considered superior and will replace the current candidate if:
            * It is faster than the current candidate (regardless of dispersion), OR
            * It is the same speed as the current candidate and has lower dispersion.
        - Returns True if all these conditions are met.
    """

    this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort
    all_nonzero = all(rider.p1_duration != 0.0 for rider in this_solution.rider_contributions.values())


    zero_dispersion_ok = (
        this_solution_dispersion != 0.0 or
        is_zero_dispersion_permissible_for_simple_solution(this_solution)
    )

    answer = ((this_solution_speed_kph > candidate.speed_kph
            or (this_solution_speed_kph == candidate.speed_kph and this_solution_dispersion < candidate.dispersion))
        and zero_dispersion_ok
        and all_nonzero

    )
    # if answer:
    #     print(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_race_solution_with_possibility_of_drop_candidate(this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem
) -> bool:
    """
    Determines if the given solution qualifies as a 'drop solution' candidate.

    Definition:
        A 'drop solution' is a paceline configuration where at least one rider does not pull (i.e., has a zero pull duration),
        allowing the strongest riders to do all the work or for the group to drop the weakest links to maximize speed.

    Impact on Race Strategy:
        - Maximum Speed: Allows the team to go as fast as possible by letting the strongest riders take over, or by dropping the weakest riders from pulling.
        - Tactical Flexibility: Useful for late-race surges, time trials, or when the team must respond to attacks.
        - Risk: Sacrifices inclusivity and may hurt team morale; dropped riders may not finish with the group.
        - Best for: High-stakes races, time trials, or when only the fastest possible result matters.

    Technical Description:
        - Checks that at least one rider has a zero pull duration (`any_zero`) and at least one has a nonzero duration (`any_nonzero`).
        - Ensures the solution is at least as fast as the current candidate and has lower dispersion.
        - Allows zero dispersion only if all durations and watts are identical (using `is_zero_dispersion_permissible_for_simple_solution`).
        - A solution is considered superior and will replace the current candidate if:
            * It is faster than the current candidate (regardless of dispersion), OR
            * It is the same speed as the current candidate and has lower dispersion.
        - Returns True if all these conditions are met.
    """


    this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort
    # any_zero = any(rider.p1_duration == 0.0 for rider in this_solution.rider_contributions.values())
    # any_nonzero = any(rider.p1_duration != 0.0 for rider in this_solution.rider_contributions.values())

    zero_dispersion_ok = (
        this_solution_dispersion != 0.0 or
        is_zero_dispersion_permissible_for_simple_solution(this_solution)
    )

    answer = ((this_solution_speed_kph > candidate.speed_kph
            or (this_solution_speed_kph == candidate.speed_kph and this_solution_dispersion < candidate.dispersion))
        and zero_dispersion_ok
        # and any_zero
        # and any_nonzero

    )

    # if answer:
    #     print(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def update_candidate_solution(this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem,
) -> None:
    """
    Updates the candidate WorthyCandidateSolutionItem in-place if the current solution is better.

    Args:
        this_solution: The candidate PacelineComputationReportItem.
        candidate: The WorthyCandidateSolutionItem instance to update.
        logger: Logger instance.

    Returns:
        None. The candidate object is updated in-place.
    """
    this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort

    candidate.speed_kph  = this_solution_speed_kph
    candidate.dispersion = this_solution_dispersion
    candidate.solution   = this_solution

# heap powerful
def generate_package_of_paceline_solutions(paceline_ingredients: PacelineIngredientsItem
    ) -> PackageOfPacelineComputationReportItem:
    """
    Generates and returns optimal paceline solutions based on the provided paceline ingredients.

    This function explores a large space of possible paceline rotation schedules, evaluates each under exertion constraints,
    and selects the best solutions for several categories:
      - Simple: All riders pull for equal, nonzero durations.
      - Balanced: The solution with the lowest standard deviation of rider intensity factors (most balanced effort).
      - Tempo: The fastest solution where all riders contribute nonzero pulls.
      - Drop: The fastest solution where at least one rider does not pull.

    The function leverages efficient serial or parallel computation depending on the number of alternatives, and returns a detailed
    computation report including timing and iteration statistics.

    Args:
        paceline_ingredients (PacelineIngredientsItem): 
            The input parameters for the computation, including the list of riders, pull durations, initial pull speeds,
            and maximum exertion intensity factor.

    Returns:
        PackageOfPacelineComputationReportItem: 
            An object containing:
                - total_pull_sequences_examined (int): Number of candidate paceline rotation schedules evaluated.
                - total_compute_iterations_performed (int): Total number of compute iterations performed across all solutions.
                - computational_time (float): Total time taken for the computation (seconds).
                - sixty_sec_solution (PacelineComputationReportItem): The best simple solution found.
                - balanced_intensity_of_effort_solution (PacelineComputationReportItem): The most balanced solution found.
                - everybody_pull_hard_solution (PacelineComputationReportItem): The best tempo solution found.
                - race_solution_with_possible_drop (PacelineComputationReportItem): The best drop solution found.

    Raises:
        ValueError: If required input parameters are missing or invalid.
        RuntimeError: If no valid solutions are found for any of the categories.

    Notes:
        - The function first_name generates all feasible paceline rotation alternatives, then prunes the solution space for efficiency.
        - If the number of alternatives is very large, a warning is logged.
        - Only solutions with valid, finite metrics are considered for selection.
        - The returned solutions are intended to represent both the fastest and the most equitable paceline configurations.
    """

    validate_paceline_ingredients(paceline_ingredients)  

    pruned_sequences = generate_all_suitable_paceline_rotation_sequences_in_the_solution_space(paceline_ingredients)

    # Convert to list of lists for downstream compatibility
    # pruned_sequences = pruned_sequences.tolist()

    if len(pruned_sequences) > ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL:
        print(f"\n\nWarning. The number of riders is {len(paceline_ingredients.riders_list)}. The number of different pull-periods in the system is {format_number_with_comma_separators(len(PULL_DURATION_OPTIONS_SEC))}. For n riders and k pull-periods, the Cartesian product generates k^n possible rider sequences to be evaluated. We have pruned the rider sequences to be evaluated down to {format_number_with_comma_separators(len(pruned_sequences))} sequences. This is still a big number. Computation could take a while - like more than twenty seconds or even more than a minute. If this is a problem, reduce the number of riders. Pull-periods are specified in system Constants and it would be a pity to reduce them because it would make solutions less broad.\n\n")


    start_time = time.perf_counter()

    all_computation_reports = generate_paceline_solutions_using_serial_and_parallel_algorithms(paceline_ingredients, pruned_sequences)

    time_taken_to_compute = time.perf_counter() - start_time

    # the tags are merely for pretty debugging and logging purposes
    balanced_intensity_candidate        = WorthyCandidateSolutionItem(tag="bal     ")
    everybody_pulls_hard_candidate      = WorthyCandidateSolutionItem(tag="allpush ")
    race_with_possible_drop_candidate   = WorthyCandidateSolutionItem(tag="race    ")

    total_compute_iterations_performed = 0 

    for this_solution in all_computation_reports:

        this_solution.computational_time = time_taken_to_compute

        total_compute_iterations_performed += this_solution.compute_iterations_performed_count

        if not is_valid_solution(this_solution):
                continue

        if is_balanced_intensity_solution_candidate(this_solution, balanced_intensity_candidate):
            update_candidate_solution(this_solution, balanced_intensity_candidate)

        if is_everyone_pull_hard_solution_candidate(this_solution, everybody_pulls_hard_candidate):
            update_candidate_solution(this_solution, everybody_pulls_hard_candidate)

        if is_race_solution_with_possibility_of_drop_candidate(this_solution, race_with_possible_drop_candidate):
            update_candidate_solution(this_solution, race_with_possible_drop_candidate)

    raise_error_if_any_solutions_missingV2(
        balanced_intensity_candidate,
        everybody_pulls_hard_candidate,
        race_with_possible_drop_candidate
    )

    answer : PackageOfPacelineComputationReportItem = PackageOfPacelineComputationReportItem(
        total_pull_sequences_examined           = len(pruned_sequences),
        total_compute_iterations_performed      = total_compute_iterations_performed,
    )
    if balanced_intensity_candidate.solution is not None:
        answer.dict_of_solutions[PacelinePlanTypeEnum.BALANCED_INTENSITY] = balanced_intensity_candidate.solution
    if everybody_pulls_hard_candidate.solution is not None:
        answer.dict_of_solutions[PacelinePlanTypeEnum.EVERYBODY_PULL_HARD] = everybody_pulls_hard_candidate.solution    
    if race_with_possible_drop_candidate.solution is not None:
        answer.dict_of_solutions[PacelinePlanTypeEnum.FASTEST] = race_with_possible_drop_candidate.solution 
        
    return answer


