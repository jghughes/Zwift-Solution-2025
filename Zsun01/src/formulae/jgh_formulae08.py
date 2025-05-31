from typing import  List, Tuple, Union, Any
import os
from collections import defaultdict
import concurrent.futures
import time
import numpy as np
import itertools
from jgh_formatting import format_number_2sig, truncate
from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_pull_plan_from_rider_exertions
from constants import EMPIRICALLY_DETERMINED_MAX_PULL_PLAN_EVALUATIONS, EMPIRICALY_DETERMINED_CROSSOVER_TO_PARALLEL_PROCESSING_THRESHOLD

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger("numba").setLevel(logging.ERROR)


def calculate_intensity_factor(rider: ZsunRiderItem, plan: RiderPullPlanItem) -> float:
    """
    Calculate the intensity factor for a given rider and exertion.
    Args:
        rider (ZsunRiderItem): The rider object.
        exertion (RiderPullPlanItem): The exertion object.
    Returns:
        float: The intensity factor.
    """
    if rider.get_1_hour_watts() == 0:
        return 0.0
    return plan.normalized_watts / rider.get_1_hour_watts()


def log_rider_one_hour_speeds(riders: list[ZsunRiderItem], logger: logging.Logger):
    from tabulate import tabulate

    table = []
    for rider in riders:
        table.append([
            rider.name,
            format_number_2sig(rider.calculate_strength_wkg()),
            format_number_2sig(rider.get_zwiftracingapp_zpFTP_wkg()),
            format_number_2sig(rider.get_zsun_1_hour_wkg()),
            format_number_2sig(rider.calculate_speed_at_1_hour_watts()),
            format_number_2sig(rider.zsun_one_hour_watts),
            format_number_2sig(rider.calculate_speed_at_standard_30sec_pull_watts()),
            format_number_2sig(rider.get_standard_30sec_pull_watts()),
        ])

    headers = [
        "Rider",
        "Pull 2m (w/kg)",
        "zFTP (w/kg)",
        "1hr (w/kg)",
        "1hr (kph)",
        "1hr (W)",
        "Pull 30s (kph)",
        "Pull 30s (W)",
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


def calculate_upper_bound_pull_speed(riders: list[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    """
    Determines the maxima of permitted pull speed among all standard pull durations of all riders.
    For each rider and each permitted pull duration (30s, 60s, 120s, 180s, 240s), this function calculates the speed
    the rider goes at their permitted pull watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall fastest speed found.
    Args:
        riders (list[ZsunRiderItem]): List of ZsunRiderItem objects representing the riders.
    Returns:
        Tuple[ZsunRiderItem, float, float]: A tuple containing:
            - The ZsunRiderItem with the highest speed,
            - The pull duration in seconds for which this maxima occurs,
            - The maxima speed in kph.
    """
    fastest_rider = riders[0]
    fastest_duration = 30.0 #arbitrary short
    highest_speed = 0.0  # Arbitrarily low speed
    duration_methods = [
        (30.0, 'calculate_speed_at_standard_30sec_pull_watts'),
        (60.0, 'calculate_speed_at_standard_1_minute_pull_watts'),
        (120.0, 'calculate_speed_at_standard_2_minute_pull_watts'),
        (180.0, 'calculate_speed_at_standard_3_minute_pull_watts'),
        (240.0, 'calculate_speed_at_standard_4_minute_pull_watts'),
    ]
    for rider in riders:
        for duration, method_name in duration_methods:
            speed = getattr(rider, method_name)()
            if speed > highest_speed:
                highest_speed = speed
                fastest_rider = rider
                fastest_duration = duration
    return fastest_rider, fastest_duration, highest_speed


def calculate_lower_bound_pull_speed(riders: list[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    """
    Determines the minima permitted pull speed among all standard pull durations of all riders.

    For each rider and each permitted pull duration (30s, 60s, 120s, 180s, 240s), this function calculates the speed
    the rider goes at their permitted pull watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall slowest speed found.

    Args:
        riders (list[ZsunRiderItem]): List of ZsunRiderItem objects representing the riders.

    Returns:
        Tuple[ZsunRiderItem, float, float]: A tuple containing:
            - The ZsunRiderItem with the lowest speed,
            - The pull duration in seconds for which this minima occurs,
            - The minima speed in kph.
    """
    slowest_rider = riders[0]
    slowest_duration = 30.0 #arbitrary short
    slowest_speed = 100.0  # Arbitrarily high speed

    duration_methods = [
        (30.0, 'calculate_speed_at_standard_30sec_pull_watts'),
        (60.0, 'calculate_speed_at_standard_1_minute_pull_watts'),
        (120.0, 'calculate_speed_at_standard_2_minute_pull_watts'),
        (180.0, 'calculate_speed_at_standard_3_minute_pull_watts'),
        (240.0, 'calculate_speed_at_standard_4_minute_pull_watts'),
    ]

    for rider in riders:
        for duration, method_name in duration_methods:
            speed = getattr(rider, method_name)()
            if speed < slowest_speed:
                slowest_speed = speed
                slowest_rider = rider
                slowest_duration = duration

    return slowest_rider, slowest_duration, slowest_speed


def calculate_lower_bound_speed_at_one_hour_watts(riders: list[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    slowest_rider = riders[0]
    slowest_duration = 3600.0  # 1 hour in seconds
    slowest_speed = slowest_rider.calculate_speed_at_1_hour_watts()

    for rider in riders:
        speed = rider.calculate_speed_at_1_hour_watts()
        if speed < slowest_speed:
            slowest_speed = speed
            slowest_rider = rider
            # duration is always 1 hour for this function
            slowest_duration = 3600.0

    return slowest_rider, slowest_duration, slowest_speed


def calculate_upper_bound_speed_at_one_hour_watts(riders: list[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    fastest_rider = riders[0]
    fastest_duration = 3600.0  # 1 hour in seconds
    highest_speed = fastest_rider.calculate_speed_at_1_hour_watts()
    for rider in riders:
        speed = rider.calculate_speed_at_1_hour_watts()
        if speed > highest_speed:
            highest_speed = speed
            fastest_rider = rider
            # duration is always 1 hour for this function
            fastest_duration = 3600.0
    return fastest_rider, fastest_duration, highest_speed


def populate_rider_pull_plans(riders: List[ZsunRiderItem], standard_pull_periods_seconds: List[float], pull_speeds_kph: List[float], max_exertion_intensity_factor : float)-> defaultdict[ZsunRiderItem, RiderPullPlanItem]:
    
    work_assignments = populate_rider_work_assignments(riders, standard_pull_periods_seconds, pull_speeds_kph)

    # log_rider_work_assignments("Example riders",work_assignments, logger)

    rider_exertions = populate_rider_exertions(work_assignments)

    # log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

    rider_pullplan_items = populate_pull_plan_from_rider_exertions(rider_exertions)

    rider_pullplan_items = diagnose_what_governed_the_top_speed(rider_pullplan_items, max_exertion_intensity_factor)

    # log_pull_plan(f"{len(riders)} riders in paceline", rider_pullplan_items, logger)


    return rider_pullplan_items


def diagnose_what_governed_the_top_speed(rider_plans: defaultdict[ZsunRiderItem, RiderPullPlanItem], max_exertion_intensity_factor : float = 0.95) -> defaultdict[ZsunRiderItem, RiderPullPlanItem]:
    for rider, plan in rider_plans.items():
        msg = ""
        # Step 1: Intensity factor checks
        intensity_factor = calculate_intensity_factor(rider, plan)
        if intensity_factor >= max_exertion_intensity_factor:
            msg += f" IF > {round(100*max_exertion_intensity_factor)}%"

        # Step 2: Pull watt limit checks
        pull_limit = rider.lookup_standard_pull_watts(plan.p1_duration)
        if plan.p1_w >= pull_limit:
            msg += " pull > max W"

        plan.diagnostic_message = msg
    return rider_plans


def make_a_pull_plan_complying_with_exertion_constraints(riders: list[ZsunRiderItem], standard_pull_periods_seconds: list[float], lowest_conceivable_kph: list[float], max_exertion_intensity_factor : float,
    precision: float = 0.1,
    max_iter: int = 20
) -> tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], Union[None, ZsunRiderItem]]:
    """
    Uses binary search to find the maximum speed before a diagnostic message appears.
    Returns (compute_iterations, rider_pullplan_items, halting_rider).
    """
    # Initial lower and upper bounds
    lower = truncate(lowest_conceivable_kph[0], 0)
    upper = lower

    # Find an upper bound where a diagnostic message appears
    for _ in range(10):
        test_speeds = [upper] * len(riders)
        rider_pullplan_items = populate_rider_pull_plans(riders, standard_pull_periods_seconds, test_speeds, max_exertion_intensity_factor)
        if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
            break
        upper += 5.0  # Increase by a reasonable chunk
    else:
        # If we never find an upper bound, just return the last result
        return 1, rider_pullplan_items, None

    compute_iterations : int = 0
    halting_rider : Union[None, ZsunRiderItem] = None
    last_valid_items : Union[None, defaultdict[ZsunRiderItem, RiderPullPlanItem]] = None # the last known good solution. not currently needed or used

    while (upper - lower) > precision and compute_iterations < max_iter:
        mid = (lower + upper) / 2
        test_speeds = [mid] * len(riders)
        rider_pullplan_items = populate_rider_pull_plans(riders, standard_pull_periods_seconds, test_speeds, max_exertion_intensity_factor)
        compute_iterations += 1
        if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
            upper = mid
            halting_rider = next(rider for rider, answer in rider_pullplan_items.items() if answer.diagnostic_message)
        else:
            lower = mid
            last_valid_items = rider_pullplan_items


    # Use the halting (upper) speed after binary search
    final_speeds = [upper] * len(riders)
    rider_pullplan_items = populate_rider_pull_plans(riders, standard_pull_periods_seconds, final_speeds, max_exertion_intensity_factor)
    if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
        halting_rider = next(rider for rider, answer in rider_pullplan_items.items() if answer.diagnostic_message)
    else:
        halting_rider = None

    return compute_iterations, rider_pullplan_items, halting_rider


def make_a_pull_plan(args: Tuple[
        List[ZsunRiderItem],           # riders
        List[float],                   # standard_pull_periods_seconds
        List[float],                   # pull_speeds
        float                         # max_exertion_intensity_factor
    ]
) -> Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], Union[None, ZsunRiderItem]]:
    # Unpack arguments
    riders, standard_pull_periods_seconds, pull_speeds, max_exertion_intensity_factor = args
    # Call the simulation for this combination
    return make_a_pull_plan_complying_with_exertion_constraints(
        riders, list(standard_pull_periods_seconds), pull_speeds, max_exertion_intensity_factor
    )

def stronger_than_strongest_rider_filter(
    paceline_rotation_schedules_being_filtered: List[Tuple[float, ...]],
    riders: List[ZsunRiderItem]
) -> List[Tuple[float, ...]]:
    if not riders:
        logger.info("stronger_than_strongest_rider_filter: No riders, returning empty list.")
        return []
    answer: List[Tuple[float, ...]] = []

    strengths = [r.calculate_strength_wkg() for r in riders]
    sorted_indices = sorted(range(len(strengths)), key=lambda i: strengths[i], reverse=True)
    strongest_rider_index = sorted_indices[0] if sorted_indices else None
    second_strongest_rider_index = sorted_indices[1] if len(sorted_indices) > 1 else None

    for schedule in paceline_rotation_schedules_being_filtered:
        if strongest_rider_index is None or strongest_rider_index >= len(schedule):
            continue
        strongest_value = schedule[strongest_rider_index]
        if any(
            value > strongest_value
            for idx, value in enumerate(schedule)
            if idx != second_strongest_rider_index
        ):
            continue
        answer.append(schedule)

    input_len = len(paceline_rotation_schedules_being_filtered)
    output_len = len(answer)
    reduction = input_len - output_len
    percent = (reduction / input_len * 100) if input_len else 0.0

    logger.info(
        f"stronger_than_strongest_rider_filter applied: input {input_len} output {output_len} "
        f"reduction: {reduction} ({percent:.1f}%)"
    )
    return answer

def stronger_than_second_strongest_rider_filter(
    paceline_rotation_schedules_being_filtered: List[Tuple[float, ...]],
    riders: List[ZsunRiderItem]
) -> List[Tuple[float, ...]]:
    if not riders:
        logger.info("stronger_than_second_strongest_rider_filter: No riders, returning empty list.")
        return []
    answer: List[Tuple[float, ...]] = []

    strengths = [r.calculate_strength_wkg() for r in riders]
    sorted_indices = sorted(range(len(strengths)), key=lambda i: strengths[i], reverse=True)
    strongest_rider_index = sorted_indices[0] if sorted_indices else None
    second_strongest_rider_index = sorted_indices[1] if len(sorted_indices) > 1 else None

    for schedule in paceline_rotation_schedules_being_filtered:
        if second_strongest_rider_index is None or second_strongest_rider_index >= len(schedule):
            answer.append(schedule)
            continue
        second_strongest_value = schedule[second_strongest_rider_index]
        if any(
            value > second_strongest_value
            for idx, value in enumerate(schedule)
            if idx != strongest_rider_index
        ):
            continue
        answer.append(schedule)

    input_len = len(paceline_rotation_schedules_being_filtered)
    output_len = len(answer)
    reduction = input_len - output_len
    percent = (reduction / input_len * 100) if input_len else 0.0

    logger.info(
        f"stronger_than_second_strongest_rider_filter applied: input {input_len} output {output_len} "
        f"reduction: {reduction} ({percent:.1f}%)"
    )
    return answer

def weaker_than_weakest_rider_filter(
    paceline_rotation_schedules_being_filtered: List[Tuple[float, ...]],
    riders: List[ZsunRiderItem]
) -> List[Tuple[float, ...]]:
    if not riders:
        logger.info("weaker_than_weakest_rider_filter: No riders, returning empty list.")
        return []
    answer: List[Tuple[float, ...]] = []

    strengths = [r.calculate_strength_wkg() for r in riders]
    sorted_indices = sorted(range(len(strengths)), key=lambda i: strengths[i])
    weakest_rider_index = sorted_indices[0] if sorted_indices else None
    second_weakest_rider_index = sorted_indices[1] if len(sorted_indices) > 1 else None

    for schedule in paceline_rotation_schedules_being_filtered:
        if weakest_rider_index is None or weakest_rider_index >= len(schedule):
            continue
        weakest_value = schedule[weakest_rider_index]
        if any(
            value < weakest_value
            for idx, value in enumerate(schedule)
            if idx != second_weakest_rider_index
        ):
            continue
        answer.append(schedule)

    input_len = len(paceline_rotation_schedules_being_filtered)
    output_len = len(answer)
    reduction = input_len - output_len
    percent = (reduction / input_len * 100) if input_len else 0.0

    logger.info(
        f"weaker_than_weakest_rider_filter applied: input {input_len} output {output_len} "
        f"reduction: {reduction} ({percent:.1f}%)"
    )
    return answer
def filter_pull_plan_rotation_schedules(
    paceline_rotation_schedules_being_filtered: List[Tuple[float, ...]],
    riders: List[ZsunRiderItem]
) -> List[Tuple[float, ...]]:
    """
    Filters paceline rotation schedules according to three rules:
    1. Reject if any element (except last) is greater than the 0th element.
    2. Reject if any element (except the 0th) is greater than the last element.
    3. Reject if any element is less than the value at the index of the weakest rider.
       Weakest rider is determined by the minimum value of rider.calculate_strength_wkg().
    Returns the reduced list of schedules.
    """

    # Early return if filtering is not needed - up to 5 riders can be handled without resorting to filtering. happy days
    if len(paceline_rotation_schedules_being_filtered) < EMPIRICALLY_DETERMINED_MAX_PULL_PLAN_EVALUATIONS + 1:
        return paceline_rotation_schedules_being_filtered

    # List of filter functions to apply in order
    filters = [
        stronger_than_strongest_rider_filter,
        stronger_than_second_strongest_rider_filter,
        weaker_than_weakest_rider_filter
    ]

    filtered_schedules = paceline_rotation_schedules_being_filtered
    for filter_func in filters:
        filtered_schedules = filter_func(filtered_schedules, riders)
        if len(filtered_schedules) < EMPIRICALLY_DETERMINED_MAX_PULL_PLAN_EVALUATIONS:
            return filtered_schedules

    return filtered_schedules

def make_pull_plan_rotation_schedule_solution_space(riders : list[ZsunRiderItem], standard_pull_periods_seconds: List[float]):
    """
    Stub for constraining the solution space of paceline rotation schedules.
    Currently returns the input schedules unchanged.

    Args:
        all_conceivable_paceline_rotation_schedules: Iterable of all possible paceline rotation schedules.
        riders: List of ZsunRiderItem objects.

    Returns:
        The (possibly filtered) list of paceline rotation schedules.
    """
    all_conceivable_paceline_rotation_schedules = list(itertools.product(standard_pull_periods_seconds, repeat=len(riders)))

    return all_conceivable_paceline_rotation_schedules

def search_for_optimal_pull_plans_with_serial_processing(riders: List[ZsunRiderItem], standard_pull_periods_seconds: List[float],
    binary_search_seed: float,
    max_exertion_intensity_factor: float, pull_plan_period_schedules : List[Tuple[float, ...]]
) -> Tuple[
    List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
    int,  # total_num_of_all_pull_plan_period_schedules investigated
    int,  # total_compute_iterations done
    float # elapsed computer time in seconds
]:
    # --- Input validation ---
    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plans_with_serial_processing.")
    if not standard_pull_periods_seconds:
        raise ValueError("No standard pull durations provided to search_for_optimal_pull_plans_with_serial_processing.")
    if any(d <= 0 or not np.isfinite(d) for d in standard_pull_periods_seconds):
        raise ValueError("All standard pull durations must be positive and finite.")
    if not np.isfinite(binary_search_seed) or binary_search_seed <= 0:
        raise ValueError("binary_search_seed must be positive and finite.")

    start_time = time.perf_counter()

    # all_conceivable_paceline_rotation_schedules =make_pull_plan_rotation_schedule_solution_space(riders, standard_pull_periods_seconds)
    total_num_of_all_pull_plan_period_schedules: int = len(pull_plan_period_schedules)
    total_compute_iterations: int = 0
    lower_bound_paceline_speed_as_array: list[float] = [binary_search_seed] * len(riders)

    if total_num_of_all_pull_plan_period_schedules > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_num_of_all_pull_plan_period_schedules)

    # Prepare arguments for each plan
    args_list = [
        (riders, list(standard_pull_periods_seconds), lower_bound_paceline_speed_as_array, max_exertion_intensity_factor)
        for standard_pull_periods_seconds in pull_plan_period_schedules
    ]
    solutions: List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]] = []

    for args in args_list:
        try:
            result = make_a_pull_plan(args)
            # --- Result validation ---
            if (result is None or
                not isinstance(result, tuple) or
                len(result) != 3 or
                result[1] is None or
                result[2] is None or
                not isinstance(result[1], dict)):
                logger.warning("Skipping invalid result: %s", result)
                continue
            solutions.append(result)
        except Exception as exc:
            logger.error("Exception in function make_a_pull_plan(): %s", exc)

    end_time = time.perf_counter()
    computational_time = end_time - start_time

    highest_speed_pull_plan_solution = None
    highest_speed: float = float('-inf')
    lowest_dispersion_pull_plan_soluton = None
    lowest_dispersion: float = float('inf')

    for compute_iterations, rider_pullplan_items, exertion_maxed_out_rider in solutions:
        total_compute_iterations += compute_iterations
        if exertion_maxed_out_rider is None or rider_pullplan_items is None or not isinstance(rider_pullplan_items, dict):
            logger.warning("Invalid result in solutions list: %s", (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider))
            continue
        pull_plan_speed_limit = rider_pullplan_items[exertion_maxed_out_rider].speed_kph
        if not np.isfinite(pull_plan_speed_limit):
            logger.warning("Non-finite pull_plan_speed_limit encountered: %s", pull_plan_speed_limit)
            continue

        # Memo for fastest halted speed
        if pull_plan_speed_limit > highest_speed:
            highest_speed = pull_plan_speed_limit
            highest_speed_pull_plan_solution = (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [calculate_intensity_factor(rider, plan) for rider, plan in rider_pullplan_items.items()]
        if not np_intensity_factors:
            logger.warning("No valid np_intensity_factors in rider_pullplan_items.")
            continue
        dispersion = np.std(np_intensity_factors)
        if not np.isfinite(dispersion):
            logger.warning("Non-finite dispersion encountered: %s", dispersion)
            continue
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_pull_plan_soluton = (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider)

    # --- Output consistency ---
    if highest_speed_pull_plan_solution is None and lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_serial_processing: No valid solution found (both highest_speed_pull_plan_solution and lowest_dispersion_pull_plan_soluton are None)")
    elif highest_speed_pull_plan_solution is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_serial_processing: No valid solution found (highest_speed_pull_plan_solution is None)")
    elif lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_serial_processing: No valid solution found (lowest_dispersion_pull_plan_soluton is None)")

    return ([highest_speed_pull_plan_solution, lowest_dispersion_pull_plan_soluton], total_num_of_all_pull_plan_period_schedules, total_compute_iterations, computational_time)


def search_for_optimal_pull_plans_with_parallel_workstealing(riders: List[ZsunRiderItem],standard_pull_periods_seconds: List[float], 
    binary_search_seed: float,  
    max_exertion_intensity_factor : float, pull_plan_period_schedules : List[Tuple[float, ...]]
) -> Tuple[List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
        int,  # total_num_of_all_pull_plan_period_schedules investigated
        int,   # total_compute_iterations done
        float]: # elapsed computer time in seconds

    # --- Input validation ---
    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plans_with_parallel_workstealing.")
    if not standard_pull_periods_seconds:
        raise ValueError("No standard pull durations provided to search_for_optimal_pull_plans_with_parallel_workstealing.")
    if any(d <= 0 or not np.isfinite(d) for d in standard_pull_periods_seconds):
        raise ValueError("All standard pull durations must be positive and finite.")
    if not np.isfinite(binary_search_seed) or binary_search_seed <= 0:
        raise ValueError("binary_search_seed must be positive and finite.")

    start_time = time.perf_counter()

    # all_conceivable_paceline_rotation_schedules =make_pull_plan_rotation_schedule_solution_space(riders, standard_pull_periods_seconds)

    total_num_of_all_pull_plan_period_schedules : int = len(pull_plan_period_schedules)
    total_compute_iterations : int = 0
    lower_bound_paceline_speed_as_array : list[float] = [binary_search_seed] * len(riders)

    if total_num_of_all_pull_plan_period_schedules  > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_num_of_all_pull_plan_period_schedules)

    # Prepare arguments for each process
    args_list = [
        (riders, standard_pull_periods_seconds, lower_bound_paceline_speed_as_array, max_exertion_intensity_factor)
        for standard_pull_periods_seconds in pull_plan_period_schedules
    ]
    solutions: List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]] = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_args = {executor.submit(make_a_pull_plan, args): args for args in args_list}
        for future in concurrent.futures.as_completed(future_to_args):
            try:
                result = future.result()
                # --- Result validation ---
                if (result is None or
                    not isinstance(result, tuple) or
                    len(result) != 3 or
                    result[1] is None or
                    result[2] is None or
                    not isinstance(result[1], dict)):
                    logger.warning("Skipping invalid result: %s", result)
                    continue
                solutions.append(result)
            except Exception as exc:
                logger.error("Exception in function make_a_pull_plan(): %s", exc)

    end_time = time.perf_counter()
    parallel_compute_time = end_time - start_time

    highest_speed_pull_plan_solution = None
    highest_speed : float = float('-inf')
    lowest_dispersion_pull_plan_soluton = None
    lowest_dispersion : float = float('inf')

    for compute_iterations, rider_pullplan_items, exertion_maxed_out_rider in solutions:
        total_compute_iterations += compute_iterations
        if exertion_maxed_out_rider is None or rider_pullplan_items is None or not isinstance(rider_pullplan_items, dict):
            logger.warning("Invalid result in solutions list: %s", (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider))
            continue
        pull_plan_speed_limit = rider_pullplan_items[exertion_maxed_out_rider].speed_kph
        if not np.isfinite(pull_plan_speed_limit):
            logger.warning("Non-finite pull_plan_speed_limit encountered: %s", pull_plan_speed_limit)
            continue

        # Memo for fastest halted speed
        if pull_plan_speed_limit > highest_speed:
            highest_speed = pull_plan_speed_limit
            highest_speed_pull_plan_solution = (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [calculate_intensity_factor(rider, plan) for rider, plan in rider_pullplan_items.items()]
        # np_intensity_factors = [answer.np_intensity_factor for answer in rider_pullplan_items.values() if hasattr(answer, "np_intensity_factor")]
        if not np_intensity_factors:
            logger.warning("No valid np_intensity_factors in rider_pullplan_items.")
            continue
        dispersion = np.std(np_intensity_factors)
        if not np.isfinite(dispersion):
            logger.warning("Non-finite dispersion encountered: %s", dispersion)
            continue
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_pull_plan_soluton = (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider)

    # --- Output consistency ---
    if highest_speed_pull_plan_solution is None and lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_parallel_workstealing: No valid solution found (both highest_speed_pull_plan_solution and lowest_dispersion_pull_plan_soluton are None)")
    elif highest_speed_pull_plan_solution is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_parallel_workstealing: No valid solution found (highest_speed_pull_plan_solution is None)")
    elif lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_parallel_workstealing: No valid solution found (lowest_dispersion_pull_plan_soluton is None)")

    return ([highest_speed_pull_plan_solution, lowest_dispersion_pull_plan_soluton], total_num_of_all_pull_plan_period_schedules, total_compute_iterations, parallel_compute_time)


def search_for_optimal_pull_plans_using_most_efficient_algorithm(riders: List[ZsunRiderItem], standard_pull_periods_seconds: List[float],
    binary_search_seed: float,
    max_exertion_intensity_factor: float
) -> Tuple[
    List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
    int,
    int,
    float
]:
    """
    Selects the most efficient algorithm for searching optimal pull plans based on the number of riders.
    Uses the parallel algorithm for 5 or more riders, otherwise uses the ordinary algorithm.
    """

    all_conceivable_paceline_rotation_schedules =make_pull_plan_rotation_schedule_solution_space(riders, standard_pull_periods_seconds)

    logger.info(f"All conceivable paceline rotation schedules : {len(all_conceivable_paceline_rotation_schedules)}")

    paceline_rotation_schedules = filter_pull_plan_rotation_schedules(all_conceivable_paceline_rotation_schedules, riders)

    if len(paceline_rotation_schedules) < EMPIRICALY_DETERMINED_CROSSOVER_TO_PARALLEL_PROCESSING_THRESHOLD:
        return search_for_optimal_pull_plans_with_serial_processing(
            riders,
            standard_pull_periods_seconds,
            binary_search_seed,
            max_exertion_intensity_factor, paceline_rotation_schedules
        )
    else:
        return search_for_optimal_pull_plans_with_parallel_workstealing(
            riders,
            standard_pull_periods_seconds,
            binary_search_seed,
            max_exertion_intensity_factor, paceline_rotation_schedules
        )


def main01():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import STANDARD_PULL_PERIODS_SEC
    from jgh_formulae08 import search_for_optimal_pull_plans_with_parallel_workstealing
    import time
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    save_filename_without_ext = f"benchmark_parallel_processing_{len(riders)}_riders"

    logger.info(f"Starting: benchmarking ordinary vs parallel processing with {len(riders)} riders")

    all_conceivable_paceline_rotation_schedules =make_pull_plan_rotation_schedule_solution_space(riders, STANDARD_PULL_PERIODS_SEC)

    # Non_parallel run as the base case
    ref_start = time.perf_counter()
    ref_result, _, _, ref_elapsed = search_for_optimal_pull_plans_with_serial_processing(riders, STANDARD_PULL_PERIODS_SEC, 30.0, 0.95, all_conceivable_paceline_rotation_schedules)
    ref_end = time.perf_counter()
    ref_fastest_speed = ref_result[0][1][ref_result[0][2]].speed_kph
    ref_elapsed_measured = ref_end - ref_start
    logger.info(f"Base-case: ordinary run compute time (measured): {ref_elapsed_measured:.2f} seconds")
    logger.info(f"Base-case: ordinary highest_speed paceline pull plan: {ref_fastest_speed} kph\n")

    # Test case
    res_start = time.perf_counter()
    res_result, _, _, res_elapsed = search_for_optimal_pull_plans_with_parallel_workstealing(riders, STANDARD_PULL_PERIODS_SEC, 30.0, 0.95, all_conceivable_paceline_rotation_schedules)
    res_end = time.perf_counter()
    res_fastest_speed = res_result[0][1][res_result[0][2]].speed_kph
    res_elapsed_measured = res_end - res_start
    logger.info(f"Test-case: parallel run compute time (measured): {res_elapsed_measured:.2f} seconds")
    logger.info(f"Test-case: parallel highest_speed paceline pull plan: {res_fastest_speed} kph\n")

    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Ordinary (non-parallel) run:\n")
    report_lines.append(f"  Compute time (measured): {ref_elapsed_measured:.2f} seconds\n")
    report_lines.append("Parallel run (work-stealing):\n")
    report_lines.append(f"  Compute time (measured): {res_elapsed_measured:.2f} seconds\n")
    report_lines.append("Time saved: {:.2f} seconds\n".format(ref_elapsed_measured - res_elapsed_measured))
    report_lines.append("\n")

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Ordinary", "Compute Time (s)": ref_elapsed_measured},
        {"Method": "Parallel", "Compute Time (s)": res_elapsed_measured},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title("Compute Time: Ordinary vs Parallel")
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
    from jgh_formulae08 import search_for_optimal_pull_plans_using_most_efficient_algorithm
    import time

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    save_filename_without_ext = f"run_optimised_filters_and_parallelisation_with_{len(riders)}_riders"

    logger.info(f"Testing: running optimised thresholds for no-filtering -> filtering and serial -> parallel processing with {len(riders)} riders")

        # Test case
    res_start = time.perf_counter()
    res_result, _, _, res_elapsed = search_for_optimal_pull_plans_using_most_efficient_algorithm(riders, STANDARD_PULL_PERIODS_SEC, 30.0, 0.95)
    res_end = time.perf_counter()
    res_fastest_speed = res_result[0][1][res_result[0][2]].speed_kph
    res_elapsed_measured = res_end - res_start
    logger.info(f"Test-case: optimised compute time (measured): {res_elapsed_measured:.2f} seconds")
    logger.info(f"Test-case: answer (fastest kph) = {res_fastest_speed} kph\n")

    # --- Summary Report ---
    report_lines = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append("Parallel run (work-stealing):\n")
    report_lines.append(f"  Compute time (measured): {res_elapsed_measured:.2f} seconds\n")
    report_lines.append("\n")

    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

if __name__ == "__main__":
    # main01()    
    main02()