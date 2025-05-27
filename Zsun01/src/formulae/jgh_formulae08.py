from typing import  List, Tuple, Union
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

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)



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
    Determines the maxima of permitted pull speed among all permitted pull durations of all riders.
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
    Determines the minima permitted pull speed among all permitted pull durations of all riders.

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


def populate_rider_pull_plans(riders: List[ZsunRiderItem], standard_pull_periods_seconds: List[float], pull_speeds_kph: List[float], max_intensity_factor : float)-> defaultdict[ZsunRiderItem, RiderPullPlanItem]:
    
    work_assignments = populate_rider_work_assignments(riders, standard_pull_periods_seconds, pull_speeds_kph)

    # log_rider_work_assignments("Example riders",work_assignments, logger)

    rider_exertions = populate_rider_exertions(work_assignments)

    # log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

    rider_pullplan_items = populate_pull_plan_from_rider_exertions(rider_exertions)

    rider_pullplan_items = diagnose_what_governed_the_top_speed(rider_pullplan_items, max_intensity_factor)

    # log_pull_plan(f"{len(riders)} riders in paceline", rider_pullplan_items, logger)


    return rider_pullplan_items


def diagnose_what_governed_the_top_speed(rider_plans: defaultdict[ZsunRiderItem, RiderPullPlanItem], max_intensity_factor : float = 0.95) -> defaultdict[ZsunRiderItem, RiderPullPlanItem]:
    for rider, plan in rider_plans.items():
        msg = ""
        # Step 1: Intensity factor checks
        intensity_factor = calculate_intensity_factor(rider, plan)
        if intensity_factor >= max_intensity_factor:
            msg += f" IF > {max_intensity_factor}"

        # Step 2: Pull watt limit checks
        pull_limit = rider.lookup_standard_pull_watts(plan.p1_duration)
        if plan.p1_w >= pull_limit:
            msg += " pull (p1) > limit"

        plan.diagnostic_message = msg
    return rider_plans


def make_a_pull_plan_complying_with_exertion_constraints(riders: list[ZsunRiderItem], standard_pull_periods_seconds: list[float], lowest_conceivable_kph: list[float], max_intensity_factor : float,
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
        rider_pullplan_items = populate_rider_pull_plans(riders, standard_pull_periods_seconds, test_speeds, max_intensity_factor)
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
        rider_pullplan_items = populate_rider_pull_plans(riders, standard_pull_periods_seconds, test_speeds, max_intensity_factor)
        compute_iterations += 1
        if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
            upper = mid
            halting_rider = next(rider for rider, answer in rider_pullplan_items.items() if answer.diagnostic_message)
        else:
            lower = mid
            last_valid_items = rider_pullplan_items


    # Use the halting (upper) speed after binary search
    final_speeds = [upper] * len(riders)
    rider_pullplan_items = populate_rider_pull_plans(riders, standard_pull_periods_seconds, final_speeds, max_intensity_factor)
    if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
        halting_rider = next(rider for rider, answer in rider_pullplan_items.items() if answer.diagnostic_message)
    else:
        halting_rider = None

    return compute_iterations, rider_pullplan_items, halting_rider


def make_a_pull_plan(args: Tuple[
        List[ZsunRiderItem],           # riders
        List[float],                   # standard_pull_periods_seconds
        List[float],                   # pull_speeds
        float                         # max_intensity_factor
    ]
) -> Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], Union[None, ZsunRiderItem]]:
    # Unpack arguments
    riders, standard_pull_periods_seconds, pull_speeds, max_intensity_factor = args
    # Call the simulation for this combination
    return make_a_pull_plan_complying_with_exertion_constraints(
        riders, list(standard_pull_periods_seconds), pull_speeds, max_intensity_factor
    )

# --- Main function to search for optimal pull plans using concurrent work-stealing algorithm - no chunking ---
def search_for_optimal_pull_plans_concurrently(riders: List[ZsunRiderItem],standard_pull_periods_seconds: List[float], binary_search_seed: float,  max_intensity_factor : float
) -> Tuple[List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
        int,  # total_num_of_all_conceivable_plans investigated
        int,   # total_compute_iterations done
        float]: # elapsed computer time in seconds

    # --- Input validation ---
    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plans_concurrently.")
    if not standard_pull_periods_seconds:
        raise ValueError("No permitted pull durations provided to search_for_optimal_pull_plans_concurrently.")
    if any(d <= 0 or not np.isfinite(d) for d in standard_pull_periods_seconds):
        raise ValueError("All permitted pull durations must be positive and finite.")
    if not np.isfinite(binary_search_seed) or binary_search_seed <= 0:
        raise ValueError("binary_search_seed must be positive and finite.")

    start_time = time.perf_counter()

    all_conceivable_paceline_rotation_schedules = list(itertools.product(standard_pull_periods_seconds, repeat=len(riders)))
    total_num_of_all_conceivable_plans : int = len(all_conceivable_paceline_rotation_schedules)
    total_compute_iterations : int = 0
    lower_bound_paceline_speed_as_array : list[float] = [binary_search_seed] * len(riders)

    if total_num_of_all_conceivable_plans  > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_num_of_all_conceivable_plans)

    # Prepare arguments for each process
    args_list = [
        (riders, standard_pull_periods_seconds, lower_bound_paceline_speed_as_array, max_intensity_factor)
        for standard_pull_periods_seconds in all_conceivable_paceline_rotation_schedules
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
    concurrent_computational_time = end_time - start_time

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
        raise RuntimeError("search_for_optimal_pull_plans_concurrently: No valid solution found (both highest_speed_pull_plan_solution and lowest_dispersion_pull_plan_soluton are None)")
    elif highest_speed_pull_plan_solution is None:
        raise RuntimeError("search_for_optimal_pull_plans_concurrently: No valid solution found (highest_speed_pull_plan_solution is None)")
    elif lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_concurrently: No valid solution found (lowest_dispersion_pull_plan_soluton is None)")

    return ([highest_speed_pull_plan_solution, lowest_dispersion_pull_plan_soluton], total_num_of_all_conceivable_plans, total_compute_iterations, concurrent_computational_time)

