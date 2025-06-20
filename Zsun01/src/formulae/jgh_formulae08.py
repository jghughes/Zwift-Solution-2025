from typing import  List, DefaultDict, Tuple
import os
from collections import defaultdict
from copy import deepcopy
import concurrent.futures
import time
import numpy as np
from jgh_string import first_n_chars
from jgh_formatting import (truncate, format_number_comma_separators, format_number_1dp, format_number_2dp, format_number_4dp, format_number_3dp, format_pretty_duration_hms)
from jgh_number import safe_divide
from handy_utilities import log_multiline
from zsun_rider_item import ZsunRiderItem
from computation_classes import (PacelineIngredientsItem, RiderContributionItem, PacelineComputationReport, PacelineSolutionsComputationReport, WorthyCandidateSolution)
from jgh_formulae02 import (calculate_upper_bound_paceline_speed, calculate_upper_bound_paceline_speed_at_one_hour_watts, calculate_lower_bound_paceline_speed,calculate_lower_bound_paceline_speed_at_one_hour_watts, calculate_overall_average_speed_of_paceline_kph, generate_all_sequences_of_pull_periods_in_the_total_solution_space, prune_all_sequences_of_pull_periods_in_the_total_solution_space, calculate_dispersion_of_intensity_of_effort)
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_rider_contributions
from constants import (SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD, SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_CONSTRAINT_VIOLATING_SPEED_KPH, INCREASE_IN_SPEED_PER_ITERATION_KPH, DESIRED_PRECISION_KPH, MAX_PERMITTED_ITERATIONS, SOLUTION_SPACE_SIZE_CONSTRAINT, ARRAY_OF_STANDARD_PULL_PERIODS_SEC)

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger("numba").setLevel(logging.ERROR)

# NB. AT NO STAGE USE LOGGING DIRECTLY OR INDIRECTLY INSIDE ANY CODE CALLED BY THE PARALLEL PROCESSING CODE. 
# IT WILL LEAD TO GARBAGE OUTPUT. THE LOGGER CANT HANDLE MULTIPLE THREADS IN MULTIPLE CORES WRITING TO IT AT 
# THE SAME TIME. USE LOGGING ONLY IN THE MAIN THREAD. EVEN WHEN DEBUGGING, THE PROBLEM IS INSURMOUNTABLE.

def log_speed_bounds_of_exertion_constrained_paceline_solutions(riders: List[ZsunRiderItem], logger: logging.Logger):

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


def log_workload_suffix_message(report : PacelineSolutionsComputationReport, logger: logging.Logger) -> None:

    message_lines = [
        f"\nBrute report: did {format_number_comma_separators(report.total_compute_iterations_performed)} iterations to evaluate {format_number_comma_separators(report.total_pull_sequences_examined)} alternative plans in {format_pretty_duration_hms(report.computational_time)}.",
        "Intensity Factor is Normalized Power/one-hour power. zFTP metrics are displayed, but play no role in computations.",
        "Pull capacities are obtained from individual 90-day best power graphs on ZwiftPower.",
        "",
        "30 second pull capacity = best power for 3.5 minutes",
        "1 minute pull capacity  = best power for  5 minutes",
        "2 minute pull capacity  = best power for 12 minutes",
        "3 minute pull capacity  = best power for 15 minutes",
        "4 minute pull capacity  = best power for 20 minutes",
        "",
        "Riders with superior pull capacity are prioritised for longer pulls.",
        "The speed of the paceline is constant and does not vary from one rider to the next.",
        "The pull capacity of the slowest puller governs the speed, leaving room for upside.",
        "The paceline puts weaker riders in the middle.",
        "Based on data from Zwiftpower as at March/April 2025. Some ZSUN riders have more comprehensive data than others.\n\n",
    ]
    log_multiline(logger, message_lines)


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
    # the binary search to work correctly to pin down the precise speed.

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_CONSTRAINT_VIOLATING_SPEED_KPH):

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders, max_exertion_intensity_factor)

        if any(contribution.effort_constraint_violation_reason for contribution in dict_of_rider_contributions.values()):
            break # break out of the loop as soon as we successfuly find a speed that violates at least one rider's ability
        
        upper_bound_for_next_search_iteration_kph += INCREASE_IN_SPEED_PER_ITERATION_KPH

        compute_iterations_performed += 1
    else:
        # If we never find an upper_bound_for_next_search_iteration_kph bound, just bale and return the last result
        return PacelineComputationReport(
            algorithm_ran_to_completion                     = False,  # We did not run to completion, we hit the max iterations
            exertion_intensity_constraint_used              = paceline_ingredients.max_exertion_intensity_factor,
            compute_iterations_performed_count              = compute_iterations_performed,
            calculated_average_speed_of_paceline_kph        =0,
            calculated_dispersion_of_intensity_of_effort    = 999,
            rider_contributions                             = dict_of_rider_contributions,
        )

    # Do the binary search. The concept is to search by bouncing back and forth between speeds bounded by  
    # lower_bound_for_next_search_iteration_kph and upper_bound_for_next_search_iteration_kph, continuing
    # until the difference between the two bounds is less than DESIRED_PRECISION_KPH i.e. until we are within a small enough range
    # of speeds that we can consider the solution precise enough. We have thus found the speed at the point at which it 
    # violates the contribution of at least one rider. The cause of the violation is flagged inside populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(..). 
    # At this moment, we know that the speed of the paceline is somewhere between the lower and upper bounds, the difference 
    # between which is negligible i.e. less than DESIRED_PRECISION_KPH. Use the upper_bound_for_next_search_iteration_kph as our answer


    while (upper_bound_for_next_search_iteration_kph - lower_bound_for_next_search_iteration_kph) > DESIRED_PRECISION_KPH and compute_iterations_performed < MAX_PERMITTED_ITERATIONS:

        mid_point_kph =safe_divide( (lower_bound_for_next_search_iteration_kph + upper_bound_for_next_search_iteration_kph), 2)

        _, dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [mid_point_kph] * num_riders, max_exertion_intensity_factor)

        compute_iterations_performed += 1

        if any(rider_contribution.effort_constraint_violation_reason for rider_contribution in dict_of_rider_contributions.values()):
            upper_bound_for_next_search_iteration_kph = mid_point_kph
        else:
            lower_bound_for_next_search_iteration_kph = mid_point_kph

    # Knowing the speed, we can rework the contributions and thus the solution
    speed_of_paceline,dict_of_rider_contributions = populate_rider_contributions_in_a_single_paceline_solution_complying_with_exertion_constraints(riders, standard_pull_periods_seconds, [upper_bound_for_next_search_iteration_kph] * num_riders , max_exertion_intensity_factor)

    answer = PacelineComputationReport(
        algorithm_ran_to_completion              = True,  
        compute_iterations_performed_count       = compute_iterations_performed,
        exertion_intensity_constraint_used       = paceline_ingredients.max_exertion_intensity_factor,
        calculated_average_speed_of_paceline_kph = speed_of_paceline,
        calculated_dispersion_of_intensity_of_effort= calculate_dispersion_of_intensity_of_effort(dict_of_rider_contributions),
        rider_contributions                      = dict_of_rider_contributions,

    )

    return answer


def generate_paceline_solutions_using_serial_processing_algorithm(
    paceline_ingredients: PacelineIngredientsItem,
    rotation_sequences: List[List[float]]
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
        rotation_sequences: List[List[float]]
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

    for sequence in rotation_sequences:
        try:
            paceline_description.sequence_of_pull_periods_sec = list(sequence)

            result = generate_a_single_paceline_solution_complying_with_exertion_constraints(paceline_description)

            answer = PacelineComputationReport(
                algorithm_ran_to_completion              = result.algorithm_ran_to_completion,
                compute_iterations_performed_count       = result.compute_iterations_performed_count,
                exertion_intensity_constraint_used       = paceline_ingredients.max_exertion_intensity_factor,
                calculated_average_speed_of_paceline_kph = result.calculated_average_speed_of_paceline_kph,
                calculated_dispersion_of_intensity_of_effort = calculate_dispersion_of_intensity_of_effort(result.rider_contributions),
                rider_contributions                      = result.rider_contributions,
            )
            solutions.append(answer)

        except Exception as exc:
            # serial processing, so we can log the error, logging OK
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
        list_of_instructions.append(deepcopy(paceline_description))

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

                answer = PacelineComputationReport(
                    algorithm_ran_to_completion              = result.algorithm_ran_to_completion,
                    compute_iterations_performed_count       = result.compute_iterations_performed_count,
                    exertion_intensity_constraint_used       = paceline_ingredients.max_exertion_intensity_factor,
                    calculated_average_speed_of_paceline_kph = result.calculated_average_speed_of_paceline_kph,
                    calculated_dispersion_of_intensity_of_effort = calculate_dispersion_of_intensity_of_effort(result.rider_contributions),
                    rider_contributions                      = result.rider_contributions,
                )
                solutions.append(answer)
            except Exception as exc:
                logger.error(f"Exception in function generate_a_single_paceline_solution_complying_with_exertion_constraints(): {exc}")


    return solutions


def generate_paceline_solutions_using_serial_and_parallel_algorithms(
    paceline_ingredients: PacelineIngredientsItem, rotation_sequences : List[List[float]]
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
        rotation_sequences: List[List[float]]
            A list of candidate pull period schedules to evaluate, where each schedule is a list of pull durations (seconds).

    Returns:
        List[PacelineComputationReport]: A list of computation reports, one for each successfully evaluated alternative.
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


def is_valid_solution(this_solution: PacelineComputationReport, logger: logging.Logger) -> bool:
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
        logger.warning(f"Error: failed to calculate std_deviation of intensity of effort: error value = {dispersion}")
        return False

    return True


def is_zero_dispersion_permissible_for_simple_solution(this_solution: PacelineComputationReport) -> bool:
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

def is_basic_solution_candidate(
    this_solution: PacelineComputationReport,
    candidate: WorthyCandidateSolution
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

def is_simple_solution_candidate(
    this_solution: PacelineComputationReport,
    candidate: WorthyCandidateSolution
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

def is_balanced_solution_candidate(
        this_solution: PacelineComputationReport,
        candidate: WorthyCandidateSolution
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

def is_tempo_solution_candidate(
    this_solution: PacelineComputationReport,
    candidate: WorthyCandidateSolution
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

def is_drop_solution_candidate(
    this_solution: PacelineComputationReport,
    candidate: WorthyCandidateSolution
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

def is_balanced_drop_solution_candidate(
    this_solution: PacelineComputationReport,
    candidate: WorthyCandidateSolution
) -> bool:
    """
    Determines if the given solution qualifies as a 'balanced drop solution' candidate.

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
    any_zero = any(rider.p1_duration == 0.0 for rider in this_solution.rider_contributions.values())
    any_nonzero = any(rider.p1_duration != 0.0 for rider in this_solution.rider_contributions.values())

    zero_dispersion_ok = (
        this_solution_dispersion != 0.0 or
        is_zero_dispersion_permissible_for_simple_solution(this_solution)
    )

    answer = ((this_solution_speed_kph > candidate.speed_kph
            or (this_solution_speed_kph == candidate.speed_kph and this_solution_dispersion < candidate.dispersion))
        and zero_dispersion_ok
        and any_zero
        and any_nonzero

    )

    # if answer:
    #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

    return answer







# def is_wtrl_race_solution_candidate(
#     this_solution: PacelineComputationReport,
#     candidate: WorthyCandidateSolution
# ) -> bool:

#     this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph
#     this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort
#     any_zero = any(rider.p1_duration == 0.0 for rider in this_solution.rider_contributions.values())
#     any_nonzero = any(rider.p1_duration != 0.0 for rider in this_solution.rider_contributions.values())

#     zero_dispersion_ok = (
#         this_solution_dispersion != 0.0 or
#         is_zero_dispersion_permissible_for_simple_solution(this_solution)
#     )

#     answer = (
#         this_solution_speed_kph >= candidate.speed_kph
#         and this_solution_dispersion < candidate.dispersion
#         and zero_dispersion_ok
#         and any_zero
#         and any_nonzero

#     )

#     # if answer:
#     #     logger.debug(f"{first_n_chars(this_solution.guid,2)} {candidate.tag} {format_number_2dp(this_solution_speed_kph)}kph {format_number_3dp(this_solution_dispersion)}sigma isCandidate")

#     return answer


def update_candidate_solution(
    this_solution: PacelineComputationReport,
    candidate: WorthyCandidateSolution,
    logger: logging.Logger
) -> None:
    """
    Updates the candidate WorthyCandidateSolution in-place if the current solution is better.

    Args:
        this_solution: The candidate PacelineComputationReport.
        candidate: The WorthyCandidateSolution instance to update.
        logger: Logger instance.

    Returns:
        None. The candidate object is updated in-place.
    """
    this_solution_speed_kph = this_solution.calculated_average_speed_of_paceline_kph
    this_solution_dispersion = this_solution.calculated_dispersion_of_intensity_of_effort

    candidate.speed_kph  = this_solution_speed_kph
    candidate.dispersion = this_solution_dispersion
    candidate.solution   = this_solution

def raise_error_if_any_solutions_missing(
    basic_candidate: WorthyCandidateSolution,
    simple_candidate: WorthyCandidateSolution,
    balanced_candidate: WorthyCandidateSolution,
    tempo_candidate: WorthyCandidateSolution,
    drop_candidate: WorthyCandidateSolution
) -> None:
    """
    Raises RuntimeError if any required candidate solution is missing.
    """
    if (
        basic_candidate.solution is None
        and simple_candidate.solution is None
        and balanced_candidate.solution is None
        and tempo_candidate.solution is None
        and drop_candidate.solution is None
    ):
        raise RuntimeError("No valid solutions found for simple, balanced-IF, tempo, and drop solutions.")

    if basic_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (basic_solution is None)")
    if simple_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (simple_solution is None)")
    if tempo_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (tempo_solution is None)")
    if balanced_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (balanced_solution is None)")
    if drop_candidate.solution is None:
        raise RuntimeError("No valid this_solution found (drop_solution is None)")


def generate_ingenious_paceline_solutions(paceline_ingredients: PacelineIngredientsItem
    ) -> PacelineSolutionsComputationReport:
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
        PacelineSolutionsComputationReport: 
            An object containing:
                - total_pull_sequences_examined (int): Number of candidate paceline rotation schedules evaluated.
                - total_compute_iterations_performed (int): Total number of compute iterations performed across all solutions.
                - computational_time (float): Total time taken for the computation (seconds).
                - simple_solution (PacelineComputationReport): The best simple solution found.
                - balanced_intensity_of_effort_solution (PacelineComputationReport): The most balanced solution found.
                - tempo_solution (PacelineComputationReport): The best tempo solution found.
                - drop_solution (PacelineComputationReport): The best drop solution found.

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

    universe_of_rotation_sequences= generate_all_sequences_of_pull_periods_in_the_total_solution_space(len(paceline_ingredients.riders_list), paceline_ingredients.sequence_of_pull_periods_sec)

    pruned_sequences = prune_all_sequences_of_pull_periods_in_the_total_solution_space(
        universe_of_rotation_sequences, paceline_ingredients.riders_list
    )

    # Convert to list of lists for downstream compatibility
    pruned_sequences = pruned_sequences.tolist()

    # logger.debug(f"Number of paceline rotation sequence alternatives generated: {len(pruned_sequences)}")

    if len(pruned_sequences) > 1_024:
        logger.warning(f"\nWarning. The number of riders is {len(paceline_ingredients.riders_list)}. The number of allowed pull-periods is {len(ARRAY_OF_STANDARD_PULL_PERIODS_SEC)}. For n riders and k allowed pull periods, the Cartesian product generates k^n possible sequences to be evaluated. This is {len(universe_of_rotation_sequences)}. We have pruned these down to {len(pruned_sequences)} sequences. This is still a big number. Computation could take a while. If this is a problem, reduce the number of riders. Pull-periods are specified in system Constants and should not be reduced if possible.\n")

    start_time = time.perf_counter()

    all_computation_reports = generate_paceline_solutions_using_serial_and_parallel_algorithms(paceline_ingredients, pruned_sequences)

    # for idx, solution in enumerate(all_computation_reports):
    #     logger.debug(f"sln: {idx+1} {first_n_chars(solution.guid, 2)}  {format_number_3dp(solution.calculated_average_speed_of_paceline_kph)}kph")

    time_taken_to_compute = time.perf_counter() - start_time

    basic_candidate   = WorthyCandidateSolution(tag="basic")
    simple_candidate   = WorthyCandidateSolution(tag="simpl")
    balanced_candidate = WorthyCandidateSolution(tag="bal   ")
    tempo_candidate    = WorthyCandidateSolution(tag="t    ")
    drop_candidate     = WorthyCandidateSolution(tag="drop ")

    total_compute_iterations_performed = 0 

    for this_solution in all_computation_reports:

        total_compute_iterations_performed += this_solution.compute_iterations_performed_count

        if not is_valid_solution(this_solution, logger):
                continue

        if is_basic_solution_candidate(this_solution, basic_candidate):
            update_candidate_solution(this_solution, basic_candidate, logger)

        if is_simple_solution_candidate(this_solution, simple_candidate):
            update_candidate_solution(this_solution, simple_candidate, logger)

        if is_balanced_solution_candidate(this_solution, balanced_candidate):
            update_candidate_solution(this_solution, balanced_candidate, logger)

        if is_tempo_solution_candidate(this_solution, tempo_candidate):
            update_candidate_solution(this_solution, tempo_candidate, logger)

        if is_drop_solution_candidate(this_solution, drop_candidate):
            update_candidate_solution(this_solution, drop_candidate, logger)

    raise_error_if_any_solutions_missing(
        basic_candidate,
        simple_candidate,
        balanced_candidate,
        tempo_candidate,
        drop_candidate
    )

    return PacelineSolutionsComputationReport(
        total_pull_sequences_examined           = len(pruned_sequences),
        total_compute_iterations_performed      = total_compute_iterations_performed,
        computational_time                      = time_taken_to_compute,
        basic_solution                          = basic_candidate.solution,
        simple_solution                         = simple_candidate.solution,
        balanced_intensity_of_effort_solution   = balanced_candidate.solution,
        tempo_solution                          = tempo_candidate.solution,
        drop_solution                           = drop_candidate.solution,
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

    all_conceivable_paceline_rotation_schedules = generate_all_sequences_of_pull_periods_in_the_total_solution_space(len(riders), ARRAY_OF_STANDARD_PULL_PERIODS_SEC)

    plan_params = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = ARRAY_OF_STANDARD_PULL_PERIODS_SEC,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )


    save_filename_without_ext = f"benchmark_parallel_processing_{len(riders)}_riders"

    logger.debug(f"Starting: benchmarking serial vs parallel processing with {len(riders)} riders")


    # Serial run as the base case
    s1 = time.perf_counter()
    _ = generate_paceline_solutions_using_serial_processing_algorithm(plan_params, all_conceivable_paceline_rotation_schedules)
    s2 = time.perf_counter()
    logger.debug(f"Base-case: serial run compute time (measured): {round(s2 - s1, 2)} seconds")

    # Parallel run
    p1 = time.perf_counter()
    _ = generate_paceline_solutions_using_parallel_workstealing_algorithm(plan_params, all_conceivable_paceline_rotation_schedules)
    p2 = time.perf_counter()

    logger.debug(f"Test-case: parallel run compute time (measured): {round(p2 - p1,2)} seconds")

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

    logger.debug("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.debug(f"Summary report written to {save_filename_without_ext}.txt")

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
    logger.debug(f"Bar chart saved to {save_filename_without_ext}.png")


def main02():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC
    from zsun_rider_dto import ZsunRiderDTO

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"
    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    params = PacelineIngredientsItem(
        riders_list                  = riders,
        sequence_of_pull_periods_sec = ARRAY_OF_STANDARD_PULL_PERIODS_SEC,
        pull_speeds_kph              = [10.0] * len(riders), # this is definitely not a dictated speed in this context, it's the seed speed for the binary search algorithm. arbitrary low value.
        max_exertion_intensity_factor= 0.95
    )

    save_filename_without_ext = f"run_optimised_filters_and_parallelisation_with_{len(riders)}_riders"

    logger.debug(f"Testing: running sensible empirically-measured thresholds for no-filtering -> filtering and serial -> parallel processing with {len(riders)} riders")

    computation_report = generate_ingenious_paceline_solutions(params)

    simple_solution = computation_report.simple_solution
    balanced_solution = computation_report.balanced_intensity_of_effort_solution
    tempo_solution = computation_report.tempo_solution
    drop_solution = computation_report.drop_solution

    simple_speed = simple_solution.calculated_average_speed_of_paceline_kph if simple_solution else None
    balanced_speed = balanced_solution.calculated_average_speed_of_paceline_kph if balanced_solution else None
    tempo_speed = tempo_solution.calculated_average_speed_of_paceline_kph if tempo_solution else None
    drop_speed = drop_solution.calculated_average_speed_of_paceline_kph if drop_solution else None

    logger.debug(f"Test-case: time taken using most performant algorithm (measured): {round(computation_report.computational_time,2)} seconds.")

    simple_guid    = first_n_chars(simple_solution.guid, 2) if simple_solution else "--"
    balanced_guid  = first_n_chars(balanced_solution.guid, 2) if balanced_solution else "--"
    tempo_guid     = first_n_chars(tempo_solution.guid, 2) if tempo_solution else "--"
    drop_guid      = first_n_chars(drop_solution.guid, 2) if drop_solution else "--"

    logger.debug(f"simple solution speed (kph)           : {simple_guid} : {simple_speed}")
    logger.debug(f"balanced-effort solution speed (kph)  : {balanced_guid} : {balanced_speed}")
    logger.debug(f"tempo solution speed (kph)            : {tempo_guid} : {tempo_speed}")
    logger.debug(f"drop solution speed (kph)             : {drop_guid} : {drop_speed}")

    # --- Summary Report ---
    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Most performant algorithm:\n")
    report_lines.append(f"  Compute-time (measured): {round(computation_report.computational_time,2)} seconds\n")
    report_lines.append("\n")

    logger.debug("".join(report_lines))

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.debug(f"Summary report written to {save_filename_without_ext}.txt")

if __name__ == "__main__":
    # main01()    
    main02()