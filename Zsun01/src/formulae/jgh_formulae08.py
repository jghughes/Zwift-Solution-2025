from typing import  List, DefaultDict, Tuple
import os
from collections import defaultdict
from copy import deepcopy
import concurrent.futures
import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from jgh_string import first_n_chars
from jgh_formatting import (truncate, format_number_with_comma_separators, format_number_1dp, format_pretty_duration_hms)
from jgh_number import safe_divide
from handy_utilities import log_multiline
from zsun_rider_item import ZsunItem
from computation_classes import (PacelineIngredientsItem, RiderContributionItem, PacelineComputationReportItem, PacelineSolutionsComputationReportItem, WorthyCandidateSolutionItem)
from computation_classes_display_objects import PacelineSolutionsComputationReportDisplayObject
from jgh_formulae02 import (calculate_upper_bound_paceline_speed, calculate_upper_bound_paceline_speed_at_one_hour_watts, calculate_lower_bound_paceline_speed,calculate_lower_bound_paceline_speed_at_one_hour_watts, calculate_overall_average_speed_of_paceline_kph, generate_all_paceline_rotation_sequences_in_the_total_solution_space, prune_all_sequences_of_pull_periods_in_the_total_solution_space, calculate_dispersion_of_intensity_of_effort)
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_rider_contributions

from constants import (SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD, SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH, CHUNK_OF_KPH_PER_ITERATION, REQUIRED_PRECISION_OF_SPEED, MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION, ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL, STANDARD_PULL_PERIODS_SEC_AS_LIST)

import logging

# CRUCIAL WARNING. AT NO STAGE USE LOGGING STATEMENTS DIRECTLY OR INDIRECTLY INSIDE ANY CODE CALLED WITHIN THE ProcessPoolExecutor. 
# IT WILL LEAD TO GARBAGE OUTPUT. THE LOGGER CANT HANDLE MULTIPLE THREADS IN MULTIPLE CORES WRITING TO IT AT 
# THE SAME TIME. USE LOGGING ONLY IN THE MAIN THREAD. EVEN WHEN DEBUGGING, THE PROBLEM IS INSURMOUNTABLE. 

def log_speed_bounds_of_exertion_constrained_paceline_solutions(riders: List[ZsunItem], logger: logging.Logger):

    upper_bound_pull_rider, upper_bound_pull_rider_duration, upper_bound_pull_rider_speed   = calculate_upper_bound_paceline_speed(riders)
    upper_bound_1_hour_rider, _, upper_bound_1_hour_rider_speed                             = calculate_upper_bound_paceline_speed_at_one_hour_watts(riders)
    lower_bound_pull_rider, lower_bound_pull_rider_duration, lower_bound_pull_rider_speed   = calculate_lower_bound_paceline_speed(riders)
    lower_bound_1_hour_rider, _, lower_bound_1_hour_rider_speed                             = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)

    message_lines = [
        "\nPACELINE PULL SPEED: upper and lower bounds of exertion-constrained pull plans:\n",
        f"Upper bound pull        :  {round(upper_bound_pull_rider_speed)}kph @ {round(upper_bound_pull_rider.get_standard_30sec_pull_watts())}w "
        f"{format_number_1dp(safe_divide(upper_bound_pull_rider.get_standard_30sec_pull_watts(), upper_bound_pull_rider.weight_kg))}wkg by {upper_bound_pull_rider.name} "
        f"for a pull of {round(upper_bound_pull_rider_duration)} seconds.",
        f"Upper bound 1-hour pull :  {round(upper_bound_1_hour_rider_speed)}kph @ {round(upper_bound_1_hour_rider.get_one_hour_watts())}w "
        f"{format_number_1dp(safe_divide(upper_bound_1_hour_rider.get_one_hour_watts(), upper_bound_1_hour_rider.weight_kg))}wkg by {upper_bound_1_hour_rider.name}.",
        f"Lower bound pull        :  {round(lower_bound_pull_rider_speed)}kph @ {round(lower_bound_pull_rider.get_standard_4_minute_pull_watts())}w "
        f"{format_number_1dp(safe_divide(lower_bound_pull_rider.get_standard_4_minute_pull_watts(), lower_bound_pull_rider.weight_kg))}wkg by {lower_bound_pull_rider.name} "
        f"for a pull of {round(lower_bound_pull_rider_duration)} seconds.",
        f"Lower bound 1-hour pull :  {round(lower_bound_1_hour_rider_speed)}kph @ {round(lower_bound_1_hour_rider.get_one_hour_watts())}w "
        f"{format_number_1dp(safe_divide(lower_bound_1_hour_rider.get_one_hour_watts(), lower_bound_1_hour_rider.weight_kg))}wkg by {lower_bound_1_hour_rider.name}."
    ]
    log_multiline(logger, message_lines)


def log_workload_suffix_message(report : PacelineSolutionsComputationReportDisplayObject, logger: logging.Logger) -> None:

    message_lines = [
        f"\nBrute report: did {format_number_with_comma_separators(report.total_compute_iterations_performed)} iterations to evaluate {format_number_with_comma_separators(report.total_pull_sequences_examined)} alternative plans in {format_pretty_duration_hms(report.computational_time)}.",
        "Intensity Factor is Normalized Power/one-hour power. zFTP metrics are displayed, but play no role in computations.",
        "Pull capacities are obtained from individual 90-day best power graphs on ZwiftPower.",
        "",
        "30 second pull capacity = 3.5 minute pull-curve ordinate",
        "1 minute pull capacity  =  5 minute pull-curve ordinate",
        "2 minute pull capacity  = 12 minute pull-curve ordinate",
        "3 minute pull capacity  = 15 minute pull-curve ordinate",
        "4 minute pull capacity  = 18 minute pull-curve ordinate",
        "5 minute pull capacity  = 20 minute pull-curve ordinate",
        "",
        "Riders with superior pull capacity are prioritised for longer pulls.",
        "The speed of the paceline is constant and does not vary from one rider to the next.",
        "The pull capacity of the slowest puller governs the speed, leaving room for upside.",
        "The paceline puts weaker riders in the middle.",
        "Based on data from Zwiftpower as at March/April 2025. Some ZSUN riders have more comprehensive data than others.\n\n",
    ]
    log_multiline(logger, message_lines)


def populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(
    riders:                        List[ZsunItem],
    standard_pull_periods_seconds: List[float],
    pull_speeds_kph:               List[float],
    max_exertion_intensity_factor: float
) -> Tuple[float, DefaultDict[ZsunItem, RiderContributionItem]]:
    """
    Computes the contributions of each rider in a single paceline solution.

    This function determines the work assignments, exertions, and final contributions for each rider
    based on the provided pull periods, target speeds, and maximum allowed exertion intensity.
    It returns the overall average speed of the paceline and a mapping of each rider to their computed contribution.

    Args:
        riders: List of ZsunItem objects representing the riders in the paceline.
        standard_pull_periods_seconds: List of pull durations (in seconds) for each rider.
        pull_speeds_kph: List of target pull speeds (in kph) for each rider.
        max_exertion_intensity_factor: Maximum allowed exertion intensity factor for any rider.

    Returns:
        Tuple containing:
            - overall_av_speed_of_paceline (float): The computed average speed of the paceline (kph).
            - dict_of_rider_contributions (DefaultDict[ZsunItem, RiderContributionItem]):
                Mapping of each rider to their computed RiderContributionItem, including effort metrics and constraint violations.
    """
    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, standard_pull_periods_seconds, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    overall_av_speed_of_paceline = calculate_overall_average_speed_of_paceline_kph(dict_of_rider_exertions)

    dict_of_rider_contributions = populate_rider_contributions(dict_of_rider_exertions, max_exertion_intensity_factor)

    return overall_av_speed_of_paceline, dict_of_rider_contributions


def generate_a_single_paceline_solution_complying_with_exertion_constraints(
    paceline_ingredients: PacelineIngredientsItem,
) -> PacelineComputationReportItem:
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
                - riders_list: List of ZsunItem objects representing the riders.
                - sequence_of_pull_periods_sec: List of pull durations (in seconds) for each rider.
                - pull_speeds_kph: List of initial pull speeds (in kph).
                - max_exertion_intensity_factor: Maximum allowed exertion intensity factor for any rider.

    Returns:
        PacelineComputationReportItem: An object containing:
            - algorithm_ran_to_completion (bool): Whether the binary search completed within the permitted iterations.
            - compute_iterations_performed_count (int): Number of iterations performed during the search.
            - calculated_average_speed_of_paceline_kph (float): The computed average speed of the paceline (kph).
            - rider_contributions (DefaultDict[ZsunItem, RiderContributionItem]): Mapping of each rider to their computed contribution,
              including effort metrics and any constraint violations.

    Notes:
        - If a feasible solution cannot be found within the maximum permitted iterations, the function returns the last computed result
          and sets algorithm_ran_to_completion to False.
        - The function assumes all input parameters are valid and finite.

    WARNING: DO NOT USE LOGGING IN THIS FUNCTION OR ANY FUNCTIONS IT CALLS DIRECTLY OR INDIRECTLY. IT IS CALLED BY THE ProcessPoolExecutor. ANY CALL TO LOGGING OFF THE MAIN THREAD WILL LEAD TO GARBAGE OUTPUT.
    """
    riders = paceline_ingredients.riders_list
    standard_pull_periods_seconds = list(paceline_ingredients.sequence_of_pull_periods_sec)
    lowest_conceivable_kph = truncate(paceline_ingredients.pull_speeds_kph[0],3)
    max_exertion_intensity_factor = paceline_ingredients.max_exertion_intensity_factor

    num_riders = len(riders)

    compute_iterations_performed: int = 0 # Number of iterations performed in the binary search, part of the answer
    dict_of_rider_contributions: DefaultDict[ZsunItem, RiderContributionItem] = defaultdict(RiderContributionItem)  # <-- part of the answer

    # Initial parameters used to determine a safe upper_bound for the binary search
    lower_bound_for_next_search_iteration_kph = lowest_conceivable_kph
    upper_bound_for_next_search_iteration_kph = lower_bound_for_next_search_iteration_kph

    # Find a speed at which at least one rider's plan has already become in violation.
    # This is done by iteratively increasing the speed until we stumble upon a speed 
    # that violates the contribution of at least one rider. This speed is not the answer 
    # we are looking for. It will most likely be way above the precise speed that 
    # triggered the violation, but it is a safe upper bound. This is required for 
    # the binary search to work correctly to pin down the precise speed.

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH):

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders, max_exertion_intensity_factor)

        if any(contribution.effort_constraint_violation_reason for contribution in dict_of_rider_contributions.values()):
            break # break out of the loop as soon as we successfuly find a speed that violates at least one rider's ability
        
        upper_bound_for_next_search_iteration_kph += CHUNK_OF_KPH_PER_ITERATION

        compute_iterations_performed += 1
    else:
        # If we never find an upper_bound_for_next_search_iteration_kph bound, just bale and return the last result
        return PacelineComputationReportItem(
            algorithm_ran_to_completion                     = False,  # We did not run to completion, we hit the max iterations
            exertion_intensity_constraint_used              = paceline_ingredients.max_exertion_intensity_factor,
            compute_iterations_performed_count              = compute_iterations_performed,
            calculated_average_speed_of_paceline_kph        =0,
            calculated_dispersion_of_intensity_of_effort    = 999,
            rider_contributions                             = dict_of_rider_contributions,
        )

    # Do the binary search. The concept is to search by bouncing back and forth between speeds bounded by  
    # lower_bound_for_next_search_iteration_kph and upper_bound_for_next_search_iteration_kph, continuing
    # until the difference between the two bounds is less than REQUIRED_PRECISION_OF_SPEED i.e. until we are within a small enough range
    # of speeds that we can consider the solution precise enough. We have thus found the speed at the point at which it 
    # violates the contribution of at least one rider. The cause of the violation is flagged inside populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(..). 
    # At this moment, we know that the speed of the paceline is somewhere between the lower and upper bounds, the difference 
    # between which is negligible i.e. less than REQUIRED_PRECISION_OF_SPEED. Use the upper_bound_for_next_search_iteration_kph as our answer


    while (upper_bound_for_next_search_iteration_kph - lower_bound_for_next_search_iteration_kph) > REQUIRED_PRECISION_OF_SPEED and compute_iterations_performed < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:

        mid_point_kph =safe_divide( (lower_bound_for_next_search_iteration_kph + upper_bound_for_next_search_iteration_kph), 2)

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [mid_point_kph] * num_riders, max_exertion_intensity_factor)

        compute_iterations_performed += 1

        if any(rider_contribution.effort_constraint_violation_reason for rider_contribution in dict_of_rider_contributions.values()):
            upper_bound_for_next_search_iteration_kph = mid_point_kph
        else:
            lower_bound_for_next_search_iteration_kph = mid_point_kph

    # Knowing the speed, we can rework the contributions and thus the solution
    speed_of_paceline,dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders , max_exertion_intensity_factor)

    answer = PacelineComputationReportItem(
        algorithm_ran_to_completion                 = True,  
        compute_iterations_performed_count          = compute_iterations_performed,
        exertion_intensity_constraint_used          = paceline_ingredients.max_exertion_intensity_factor,
        calculated_average_speed_of_paceline_kph    = speed_of_paceline,
        calculated_dispersion_of_intensity_of_effort= calculate_dispersion_of_intensity_of_effort(dict_of_rider_contributions),
        rider_contributions                         = dict_of_rider_contributions,

    )

    return answer


def generate_paceline_solutions_using_serial_processing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: List[List[float]]
) -> List[PacelineComputationReportItem]:
    """
    Compute paceline paceline_computation_reports for a set of candidate pull period sequences using serial (single-threaded) processing.

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
        List[PacelineComputationReportItem]: A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - This function processes alternatives sequentially and is intended for use when the number of alternatives is small.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - For large numbers of alternatives, consider using parallel processing for improved performance.
    """

    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)

    paceline_computation_reports: List[PacelineComputationReportItem] = []

    for sequence in paceline_rotation_sequence_alternatives:
        try:
            paceline_ingredients.sequence_of_pull_periods_sec = list(sequence)
            result = generate_a_single_paceline_solution_complying_with_exertion_constraints(paceline_ingredients)
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
            logger.error(f"Exception in function generate_paceline_solutions_using_serial_processing_algorithm(): {exc}")

    return paceline_computation_reports


def generate_paceline_solutions_using_parallel_workstealing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    paceline_rotation_sequence_alternatives: List[List[float]]
) -> List[PacelineComputationReportItem]:
    """
    Computes paceline paceline_computation_reports for multiple candidate pull period sequences using parallel processing with a work-stealing process pool.

    This function distributes the evaluation of each candidate paceline rotation schedule across available CPU cores using a process pool,
    allowing for efficient computation when the number of alternatives is large. For each alternative, it constructs a PacelineIngredientsItem
    with the specified pull periods, computes the optimal paceline speed and rider contributions, and collects the results. Invalid or incomplete
    results are skipped. DO NOT USE LOGGING IN ANY FUNCTIONS CALLED BY THE ProcessPoolExecutor. IT WILL LEAD TO GARBAGE OUTPUT.

    Args:
        paceline_ingredients: PacelineIngredientsItem
            The base input parameters for the computation, including the list of riders, initial pull speeds,
            and exertion constraints. The pull periods are overridden for each alternative.
        paceline_rotation_sequence_alternatives: List[List[float]]
            A list of candidate pull period schedules to evaluate, where each schedule is a list of pull durations (seconds).

    Returns:
        List[PacelineComputationReportItem]: A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - This function is intended for use when the number of alternatives is large enough to benefit from parallel processing.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - Invalid or incomplete results are logged as warnings and not included in the output list.

    WARNING: DO NOT USE LOGGING IN ANY FUNCTIONS IT CALLS DIRECTLY OR INDIRECTLY WITHIN THE ProcessPoolExecutor. ANY CALL TO LOGGING OFF THE MAIN THREAD WILL LEAD TO GARBAGE OUTPUT.

    """

    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = paceline_ingredients.riders_list,
        pull_speeds_kph                 = [paceline_ingredients.pull_speeds_kph[0]] * len(paceline_ingredients.riders_list),
        max_exertion_intensity_factor   = paceline_ingredients.max_exertion_intensity_factor)

    list_of_instructions: List[PacelineIngredientsItem] = []    
    
    for sequence in paceline_rotation_sequence_alternatives:
        paceline_ingredients.sequence_of_pull_periods_sec = list(sequence)
        list_of_instructions.append(deepcopy(paceline_ingredients))

    paceline_computation_reports: List[PacelineComputationReportItem] = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_params = {
            executor.submit(generate_a_single_paceline_solution_complying_with_exertion_constraints, p): p
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
                logger.error(f"Exception in function generate_paceline_solutions_using_parallel_workstealing_algorithm(): {exc}")


    return paceline_computation_reports


def generate_paceline_solutions_using_serial_and_parallel_algorithms(
    paceline_ingredients: PacelineIngredientsItem, rotation_sequences : List[List[float]]
) -> List[PacelineComputationReportItem]:
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
        rotation_sequences: List[List[float]]
            A list of candidate pull period schedules to evaluate, where each schedule is a list of pull durations (seconds).

    Returns:
        List[PacelineComputationReportItem]: A list of computation reports, one for each successfully evaluated alternative.
            Each report contains the number of compute iterations performed and the computed rider contributions.

    Notes:
        - The function chooses serial or parallel processing based on the __SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD__ constant.
        - If an exception occurs for a particular alternative, it is logged and that alternative is skipped.
        - For large numbers of alternatives, parallel processing can significantly reduce computation time.
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


def is_valid_solution(this_solution: PacelineComputationReportItem, logger: logging.Logger) -> bool:
    """
    Validates the solution's speed and dispersion.
    Returns True if both are finite and dispersion is not the error value (100).
    Logs a warning and returns False otherwise.
    """
    speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    if not np.isfinite(speed_kph):
        logger.warning(f"Binary search algorithm failure: iteration error: Non-finite speed_kph encountered: {speed_kph}")
        return False

    dispersion = this_solution.calculated_dispersion_of_intensity_of_effort
    if not np.isfinite(dispersion) or dispersion == 100:
        return False

    return True


def raise_error_if_any_solutions_missing(
    thirty_sec_candidate: WorthyCandidateSolutionItem,
    sixty_sec_candidate: WorthyCandidateSolutionItem,
    balanced_intensity_candidate: WorthyCandidateSolutionItem,
    everybody_pulls_hard_candidate: WorthyCandidateSolutionItem,
    hang_in_candidate: WorthyCandidateSolutionItem
) -> None:
    """
    Raises RuntimeError if any required candidate solution is missing.
    """
    if (
        thirty_sec_candidate.solution is None
        and sixty_sec_candidate.solution is None
        and balanced_intensity_candidate.solution is None
        and everybody_pulls_hard_candidate.solution is None
        and hang_in_candidate.solution is None
    ):
        raise RuntimeError("No valid solutions found for simple, balanced-IF, tempo, and drop solutions.")

    if thirty_sec_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (thirty_sec_solution is None)")
    if sixty_sec_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (sixty_sec_solution is None)")
    if everybody_pulls_hard_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (everybody_pull_hard_solution is None)")
    if balanced_intensity_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (balanced_solution is None)")
    if hang_in_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (hang_in_solution is None)")


def is_zero_dispersion_permissible_for_simple_solution(this_solution: PacelineComputationReportItem) -> bool:
    """
    Returns True if a dispersion of 0.0 is permissible for a 'simple solution' candidate.
    Rules:
      - If there are no riders or only one rider, zero dispersion is allowed.
      - If there are multiple riders, zero dispersion is only allowed if all pull durations
        and all pull watts are identical.
    """
    rider_contributions = list(this_solution.rider_contributions.values())
    num_riders = len(rider_contributions)
    if num_riders <= 1:
        return True
    # Check if all pull durations are the same
    durations = {r.p1_duration for r in rider_contributions}
    watts = {getattr(r, "p1_watts", None) for r in rider_contributions}
    return len(durations) == 1 and len(watts) == 1

def is_thirty_second_pulls_solution_candidate(
    this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem
) -> bool:
    """
    Determines if the given solution qualifies as a 'basic solution' candidate.

    Definition:
        A 'basic solution' is a paceline configuration where all riders pull for equal intervals of 30 seconds.
        Every rider contributes the same amount of time at the front, and no one is left out.

    Impact on Race Strategy:
        - Predictability: Simplifies rotation and communication
        - Best for: Training

    Technical Description:
        - Checks that all riders have pull durations of 30 seconds ('all_thirty_seconds`).
        - Returns True if this condition is met.
    """

    all_thirty_seconds = all(rider.p1_duration == 30.0 for rider in this_solution.rider_contributions.values())

    answer = all_thirty_seconds

    # if answer:
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_sixty_second_pulls_solution_candidate(
    this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem
) -> bool:
    """
    Determines if the given solution qualifies as a 'basic solution' candidate.

    Definition:
        A 'basic solution' is a paceline configuration where all riders pull for equal intervals of 60 seconds.
        Every rider contributes the same amount of time at the front, and no one is left out.

    Impact on Race Strategy:
        - Predictability: Simplifies rotation and communication
        - Best for: Training

    Technical Description:
        - Checks that all riders have pull durations of 60 seconds ('all_sixty_seconds`).
        - Returns True if this condition is met.
    """

    all_sixty_seconds = all(rider.p1_duration == 60.0 for rider in this_solution.rider_contributions.values())

    answer = all_sixty_seconds

    # if answer:
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_sixty_second_pulls_solution_candidate_to_be_deleted(
    this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem
) -> bool:
    """
    Determines if the given solution qualifies as a 'simple solution' candidate.

    Definition:
        A 'simple solution' is a paceline configuration where all riders pull for equal, nonzero durations.
        Every rider contributes the same amount of time at the front, and no one is left out or does extra.

    Impact on Race Strategy:
        - Fairness & Cohesion: Maximizes equality and inclusivity, ensuring all riders share the workload identically.
        - Predictability: Simplifies rotation and communication, making it easy to execute, especially for less experienced teams.
        - Performance: May not maximize overall speed if rider strengths vary, as stronger riders are underutilized and weaker riders may be overextended.
        - Best for: Club rides, training, or events where team cohesion and fairness are prioritized over absolute speed.

    Technical Description:
        - Checks that all riders have nonzero pull durations (`all_nonzero`).
        - Checks that all pull durations are equal (`all_equal`).
        - Allows zero dispersion only if all durations and watts are identical (using `is_zero_dispersion_permissible_for_simple_solution`).
        - A solution is considered superior and will replace the current candidate if:
            * It is faster than the current candidate (regardless of dispersion), OR
            * It is the same speed as the current candidate and has lower dispersion.
        - Returns True if all these conditions are met.
    """

    this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort

    all_nonzero = all(rider.p1_duration != 0.0 for rider in this_solution.rider_contributions.values())
    all_equal = len({rider.p1_duration for rider in this_solution.rider_contributions.values()}) == 1

    zero_dispersion_ok = (
        this_solution_dispersion != 0.0 or
        is_zero_dispersion_permissible_for_simple_solution(this_solution)
    )

    answer = ((this_solution_speed_kph > candidate.speed_kph
            or (this_solution_speed_kph == candidate.speed_kph and this_solution_dispersion < candidate.dispersion))
        and zero_dispersion_ok
        and all_nonzero
        and all_equal
    )
    # if answer:
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_balanced_intensity_solution_candidate(
        this_solution: PacelineComputationReportItem,
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
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_everyone_pull_hard_solution_candidate(
    this_solution: PacelineComputationReportItem,
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
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def is_hang_in_solution_candidate(
    this_solution: PacelineComputationReportItem,
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
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer

def update_candidate_solution(
    this_solution: PacelineComputationReportItem,
    candidate: WorthyCandidateSolutionItem,
    logger: logging.Logger
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

def generate_ingenious_paceline_solutions(paceline_ingredients: PacelineIngredientsItem
    ) -> PacelineSolutionsComputationReportItem:
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
        PacelineSolutionsComputationReportItem: 
            An object containing:
                - total_pull_sequences_examined (int): Number of candidate paceline rotation schedules evaluated.
                - total_compute_iterations_performed (int): Total number of compute iterations performed across all solutions.
                - computational_time (float): Total time taken for the computation (seconds).
                - sixty_sec_solution (PacelineComputationReportItem): The best simple solution found.
                - balanced_intensity_of_effort_solution (PacelineComputationReportItem): The most balanced solution found.
                - everybody_pull_hard_solution (PacelineComputationReportItem): The best tempo solution found.
                - hang_in_solution (PacelineComputationReportItem): The best drop solution found.

    Raises:
        ValueError: If required input parameters are missing or invalid.
        RuntimeError: If no valid solutions are found for any of the categories.

    Notes:
        - The function first generates all feasible paceline rotation alternatives, then prunes the solution space for efficiency.
        - If the number of alternatives is very large, a warning is logged.
        - Only solutions with valid, finite metrics are considered for selection.
        - The returned solutions are intended to represent both the fastest and the most equitable paceline configurations.
    """

    validate_paceline_ingredients(paceline_ingredients)    

    universe_of_rotation_sequences= generate_all_paceline_rotation_sequences_in_the_total_solution_space(len(paceline_ingredients.riders_list), paceline_ingredients.sequence_of_pull_periods_sec)

    pruned_sequences = prune_all_sequences_of_pull_periods_in_the_total_solution_space(
        universe_of_rotation_sequences, paceline_ingredients.riders_list
    )

    # Convert to list of lists for downstream compatibility
    pruned_sequences = pruned_sequences.tolist()

    # logger.debug(f"Number of paceline rotation sequence alternatives generated: {len(pruned_sequences)}")

    if len(pruned_sequences) > ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL:
        logger.warning(f"\n\nWarning. The number of riders is {len(paceline_ingredients.riders_list)}. The number of different pull-periods in the system is {format_number_with_comma_separators(len(STANDARD_PULL_PERIODS_SEC_AS_LIST))}. For n riders and k pull-periods, the Cartesian product generates k^n possible rider sequences to be evaluated. This is {format_number_with_comma_separators(len(universe_of_rotation_sequences))}. We have pruned these down to {format_number_with_comma_separators(len(pruned_sequences))} sequences. This is still a big number. Computation could take a while - like more than twenty seconds. If this is a problem, reduce the number of riders. Pull-periods are specified in system Constants and it would be a pity to reduce them because it would make solutions less granular.\n\n")

    start_time = time.perf_counter()

    all_computation_reports = generate_paceline_solutions_using_serial_and_parallel_algorithms(paceline_ingredients, pruned_sequences)

    # for idx, solution in enumerate(all_computation_reports):
    #     logger.debug(f"sln: {idx+1} {first_n_chars(solution.guid, 2)}  {format_number_3dp(solution.calculated_average_speed_of_paceline_kph)}kph")

    time_taken_to_compute = time.perf_counter() - start_time

    thirty_sec_candidate                = WorthyCandidateSolutionItem(tag="30sec")
    sixty_sec_candidate                 = WorthyCandidateSolutionItem(tag="60sec")
    balanced_intensity_candidate        = WorthyCandidateSolutionItem(tag="bal  ")
    everybody_pulls_hard_candidate      = WorthyCandidateSolutionItem(tag="push ")
    hang_in_candidate                   = WorthyCandidateSolutionItem(tag="hang ")

    total_compute_iterations_performed = 0 

    for this_solution in all_computation_reports:

        total_compute_iterations_performed += this_solution.compute_iterations_performed_count

        if not is_valid_solution(this_solution, logger):
                continue

        if is_thirty_second_pulls_solution_candidate(this_solution, thirty_sec_candidate):
            update_candidate_solution(this_solution, thirty_sec_candidate, logger)

        if is_sixty_second_pulls_solution_candidate(this_solution, sixty_sec_candidate):
            update_candidate_solution(this_solution, sixty_sec_candidate, logger)

        if is_balanced_intensity_solution_candidate(this_solution, balanced_intensity_candidate):
            update_candidate_solution(this_solution, balanced_intensity_candidate, logger)

        if is_everyone_pull_hard_solution_candidate(this_solution, everybody_pulls_hard_candidate):
            update_candidate_solution(this_solution, everybody_pulls_hard_candidate, logger)

        if is_hang_in_solution_candidate(this_solution, hang_in_candidate):
            update_candidate_solution(this_solution, hang_in_candidate, logger)

    raise_error_if_any_solutions_missing(
        thirty_sec_candidate,
        sixty_sec_candidate,
        balanced_intensity_candidate,
        everybody_pulls_hard_candidate,
        hang_in_candidate
    )

    return PacelineSolutionsComputationReportItem(
        total_pull_sequences_examined           = len(pruned_sequences),
        total_compute_iterations_performed      = total_compute_iterations_performed,
        computational_time                      = time_taken_to_compute,
        thirty_sec_solution                     = thirty_sec_candidate.solution,
        sixty_sec_solution                      = sixty_sec_candidate.solution,
        balanced_intensity_of_effort_solution   = balanced_intensity_candidate.solution,
        everybody_pull_hard_solution            = everybody_pulls_hard_candidate.solution,
        hang_in_solution                        = hang_in_candidate.solution,
        all_solutions                           = all_computation_reports
    )


def main01():
    """
        Benchmarks and compares the compute time of serial-processing versus parallel
        processing for paceline-sequences according to the size of universe of
        paceline-sequences. The size is governed by the cross-product of the number
        of riders and the number of standard pull periods (currently 0, 30, 60, 120,
        180, 240, 300). Processing time is exponentially explosive as the number of
        sequences grows.

        The idea with this main01() is to manually increase the number of riders
        (i.e. the number of sequences) and to determine when parallel-processing
        overtakes serial-processing in terms of compute speed. I use main01() to
        empirically determine the sweet spot for the constant
        SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD. This constant is subsequently
        relied upon by Brute in all scenarios. It is therefore important to get the
        constant right. The parameter is tuned for my powerful laptop. It will be
        different for a puny server with fewer cores. At the time of writing (Aug
        2025), the numbers look like this:-

        Riders  Sequences           serial-processing               parallel-processing
            1           7                  <1s                          5s 
            2          49                  <1s                          9s
            3         343                   5s                          9s
            equality  512                   9s                          9s
                      729                  13s                          9s
                    1,000                  22s                         11s  
            4       2,401                  67s                         13s
            5      16,807                  10m                         78s - way to tedious to run
            6     117,649                4h06m                         13m - waay to tedious to run
            7     823,543               don't even bother
            8   5,764,801               don't even bother


    This function:
      - Loads rider data and team composition from JSON and utility functions.
      - Generates all possible paceline rotation sequences for the team and standard pull periods.
      - Runs the paceline solution algorithm using both serial and parallel approaches, timing each.
      - Logs and writes a summary report comparing the compute times and time saved by parallelization.
      - Visualizes the results in a bar chart and saves the chart as a PNG file.

    The function is intended for performance analysis and does not return a value. All results are 
    logged and saved as a .png.

    Side Effects:
      - Writes a summary report to a text file.
      - Saves a bar chart visualization as a PNG file.
      - Logs progress and results using the configured logger.

    Raises:
      - Exceptions are logged if encountered during computation.

    Dependencies:
      - Expects global variables RIDERS_FILE_NAME and DATA_DIRPATH to be set.
      - Requires pandas, seaborn, matplotlib, and other project-specific modules.
    """

    paceline_ingredients = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )

    save_filename_without_ext = f"compare_serial_processing_versus_parallel_processing_duration_{len(riders)}"

    logger.debug(f"Starting: head-to-head benchmarking of serial-processing versus parallel-processing with {len(riders)} riders, {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)} pull periods, and consequently {pretty_number_of_sequences_before_pruning} paceline_rotation sequences (no solution-space pruning. all sequences evaluated.")
    logger.debug(f"\nCommencing serial processing. This could take a very long time depending on the number of sequences. Please wait....")

    # Serial run as the base case (ignore squigglies here, they are inconsequential warnings)
    s1 = time.perf_counter()
    _ = generate_paceline_solutions_using_serial_processing_algorithm(paceline_ingredients, all_conceivable_paceline_rotation_sequences)
    s2 = time.perf_counter()
    logger.debug(f"\nBase-case: serial run compute time: {round(s2 - s1, 2)} seconds")
    logger.debug(f"\nCommencing parallel processing. Please wait....")
    # Parallel run (ignore squigglies here, they are inconsequential warnings)
    p1 = time.perf_counter()
    _ = generate_paceline_solutions_using_parallel_workstealing_algorithm(paceline_ingredients, all_conceivable_paceline_rotation_sequences)
    p2 = time.perf_counter()

    logger.debug(f"\nTest-case: parallel run compute time: {round(p2 - p1,2)} seconds")

    # --- Summary Report ---
    report_lines : List[str] = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append(f"Number of standard pull periods: {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)}\n\n")
    report_lines.append(f"Consequential number of paceline-rotation sequences: {pretty_number_of_sequences_before_pruning}\n\n")
    report_lines.append(f"Serial run: Compute time: {round(s2 - s1, 2)} seconds\n")
    report_lines.append(f"Parallel run (work-stealing): Compute time: {round(p2 - p1,2)} seconds\n")
    report_lines.append(f"Time saved by parallelisation: {round((s2 - s1) - (p2 - p1), 2)} seconds")
    report_lines.append("\n")

    logger.debug("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.debug(f"Summary report written to {save_filename_without_ext}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Serial-processing", "Compute Time (s)": s2 - s1},
        {"Method": "Parallel-processing (work stealing)", "Compute Time (s)": p2 - p1},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title(f"Compute Time: Serial-processing vs Parallel-processing (work stealing): Paceline rotation sequences: {pretty_number_of_sequences_before_pruning}")
    plt.ylabel("Compute Time (seconds)")
    plt.xlabel("Method")
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}.png")
    plt.show()
    logger.debug(f"Bar chart saved to {save_filename_without_ext}.png")


def main02():
    """
    Identical to main01() except that it uses the pruned list of paceline-rotation
    sequences rather than the full list of conceivable sequences, so as to
    demonstrate the benefits of pruning on compute time and how it renders the
    brute-force approach feasible for larger numbers of riders. Without pruning,
    the brute-force approach becomes unfeasible very quickly as the number of
    riders increases. Even with parallel processing, it becomes impractical beyond
    4 riders. With pruning, it is excellent up to 6, which is the max size of a
    paceline in ZRL events, remains decent up to 8 riders (the max in WTRL TTT
    events), and can even be tolerable for 9 riders. The pruning heuristic 
    takes a single parameter : ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL. 
    For the test results shown here, this is set somewhat arbitrarily at 1,024. 
    Notice how pruning radically reduces the solution space for 4 riders and beyond. 
    At the time of writing (Aug 2025), the numbers look like this:
        
        Riders  Sequences After pruning serial-processing parallel-processing
            1           7             7       <1s               5s 
            2          49            49       <1s               9s
            3         343           343        5s               9s
            4       2,401           980        7s               10s
            5      16,807           966       42s               11s
            6     117,649           924       56s               14s
            7     823,543         1,716      128s               22s
            8   5,764,801         3,003      282s               39s     
            9  40,353,607         5,055      575s               72s                       


    This function:
      - Loads rider data and team composition from JSON and utility functions.
      - Generates all possible paceline rotation sequences for the team and standard pull periods.
      - Runs the paceline solution algorithm using both serial and parallel approaches, timing each.
      - Logs and writes a summary report comparing the compute times and time saved by parallelization.
      - Visualizes the results in a bar chart and saves the chart as a PNG file.

    The function is intended for performance analysis and does not return a value. All results are 
    logged and saved as a .png.

    Side Effects:
      - Writes a summary report to a text file.
      - Saves a bar chart visualization as a PNG file.
      - Logs progress and results using the configured logger.

    Raises:
      - Exceptions are logged if encountered during computation.

    Dependencies:
      - Expects global variables RIDERS_FILE_NAME and DATA_DIRPATH, ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL to be set.
      - Requires pandas, seaborn, matplotlib, and other project-specific modules.
    """

    paceline_ingredients = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )

    save_filename_without_ext = f"compare_serial_processing_versus_parallel_processing_duration_after_pruning{len(riders)}"

    logger.debug(f"Starting: head-to-head benchmarking of serial-processing versus parallel-processing with {len(riders)} riders, {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)} pull periods, and consequently {pretty_number_of_sequences_before_pruning} paceline_rotation sequences before pruning and {pretty_number_of_sequences_after_pruning} sequences after pruning.")
    logger.debug(f"\nCommencing serial processing. This could take a very long time depending on the number of sequences. Please wait....")

    # Serial run as the base case (ignore squigglies here, they are inconsequential warnings)
    s1 = time.perf_counter()
    _ = generate_paceline_solutions_using_serial_processing_algorithm(paceline_ingredients, reduced_paceline_rotation_sequences_after_pruning)
    s2 = time.perf_counter()
    logger.debug(f"\nBase-case: serial run compute time: {round(s2 - s1, 2)} seconds")
    logger.debug(f"\nCommencing parallel processing. Please wait....")
    # Parallel run (ignore squigglies here, they are inconsequential warnings)
    p1 = time.perf_counter()
    _ = generate_paceline_solutions_using_parallel_workstealing_algorithm(paceline_ingredients, reduced_paceline_rotation_sequences_after_pruning)
    p2 = time.perf_counter()

    logger.debug(f"\nTest-case: parallel run compute time: {round(p2 - p1,2)} seconds")

    # --- Summary Report ---
    report_lines : List[str] = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n")
    report_lines.append(f"Number of standard pull periods: {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)}\n")
    report_lines.append(f"Universe of all paceline-rotation sequences: {pretty_number_of_sequences_before_pruning}\n")
    report_lines.append(f"Pruning goal: {ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL}\n")
    report_lines.append(f"Paceline-rotation sequences after pruning: {pretty_number_of_sequences_after_pruning}\n")
    report_lines.append(f"Serial run: Compute time: {round(s2 - s1, 2)} seconds\n")
    report_lines.append(f"Parallel run (work-stealing): Compute time: {round(p2 - p1,2)} seconds\n")
    report_lines.append(f"Time saved by parallelisation: {round((s2 - s1) - (p2 - p1), 2)} seconds")
    report_lines.append("\n")

    logger.debug("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.debug(f"Summary report written to {save_filename_without_ext}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Serial-processing", "Compute Time (s)": s2 - s1},
        {"Method": "Parallel-processing (work stealing)", "Compute Time (s)": p2 - p1},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title(f"Compute Time: Serial-processing vs Parallel-processing (work stealing): Paceline rotation sequences after pruning: {pretty_number_of_sequences_before_pruning}")
    plt.ylabel("Compute Time (seconds)")
    plt.xlabel("Method")
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}.png")
    plt.show()
    logger.debug(f"Bar chart saved to {save_filename_without_ext}.png")


if __name__ == "__main__":
    from jgh_formatting import format_number_with_comma_separators
    from handy_utilities import read_json_dict_of_ZsunDTO
    from repository_of_teams import get_team_riderIDs
    from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST

    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR) # numba generates a lot of INFO messages that are not useful here
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems_2025_07_08.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_ZsunItems = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs = get_team_riderIDs("test")
    riders = [dict_of_ZsunItems[rid] for rid in riderIDs]

    all_conceivable_paceline_rotation_sequences = generate_all_paceline_rotation_sequences_in_the_total_solution_space(len(riders), STANDARD_PULL_PERIODS_SEC_AS_LIST)

    pretty_number_of_sequences_before_pruning = format_number_with_comma_separators(len(all_conceivable_paceline_rotation_sequences))

    reduced_paceline_rotation_sequences_after_pruning = prune_all_sequences_of_pull_periods_in_the_total_solution_space(all_conceivable_paceline_rotation_sequences, riders)

    pretty_number_of_sequences_after_pruning = format_number_with_comma_separators(len(reduced_paceline_rotation_sequences_after_pruning))


    # main01()    
    main02()