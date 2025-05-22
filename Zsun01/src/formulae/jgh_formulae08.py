from typing import  List, Tuple, Union, Any, DefaultDict, Optional, Generator 
from collections import defaultdict
import concurrent.futures
import os
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

permitted_pull_durations = [30.0, 60.0, 120.0, 180.0, 240.0] # in seconds


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
            format_number_2sig(rider.calculate_speed_at_permitted_30sec_pull_watts()),
            format_number_2sig(rider.get_permitted_30sec_pull_watts()),
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
    fastest_speed = 0.0  # Arbitrarily low speed
    duration_methods = [
        (30.0, 'calculate_speed_at_permitted_30sec_pull_watts'),
        (60.0, 'calculate_speed_at_permitted_1_minute_pull_watts'),
        (120.0, 'calculate_speed_at_permitted_2_minute_pull_watts'),
        (180.0, 'calculate_speed_at_permitted_3_minute_pull_watts'),
        (240.0, 'calculate_speed_at_permitted_4_minute_pull_watts'),
    ]
    for rider in riders:
        for duration, method_name in duration_methods:
            speed = getattr(rider, method_name)()
            if speed > fastest_speed:
                fastest_speed = speed
                fastest_rider = rider
                fastest_duration = duration
    return fastest_rider, fastest_duration, fastest_speed

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
        (30.0, 'calculate_speed_at_permitted_30sec_pull_watts'),
        (60.0, 'calculate_speed_at_permitted_1_minute_pull_watts'),
        (120.0, 'calculate_speed_at_permitted_2_minute_pull_watts'),
        (180.0, 'calculate_speed_at_permitted_3_minute_pull_watts'),
        (240.0, 'calculate_speed_at_permitted_4_minute_pull_watts'),
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
    fastest_speed = fastest_rider.calculate_speed_at_1_hour_watts()
    for rider in riders:
        speed = rider.calculate_speed_at_1_hour_watts()
        if speed > fastest_speed:
            fastest_speed = speed
            fastest_rider = rider
            # duration is always 1 hour for this function
            fastest_duration = 3600.0
    return fastest_rider, fastest_duration, fastest_speed

def populate_rider_pull_plans(riders: List[ZsunRiderItem], pull_durations: List[float], pull_speeds_kph: List[float])-> defaultdict[ZsunRiderItem, RiderPullPlanItem]:
    
    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    # log_rider_work_assignments("Example riders",work_assignments, logger)

    rider_exertions = populate_rider_exertions(work_assignments)

    # log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

    rider_pullplan_items = populate_pull_plan_from_rider_exertions(rider_exertions)

    rider_pullplan_items = diagnose_what_governed_the_top_speed(rider_pullplan_items)

    # log_pull_plan(f"{len(riders)} riders in paceline", rider_pullplan_items, logger)


    return rider_pullplan_items

def diagnose_what_governed_the_top_speed(rider_answers: defaultdict[ZsunRiderItem, RiderPullPlanItem]) -> defaultdict[ZsunRiderItem, RiderPullPlanItem]:
    for rider, answer in rider_answers.items():
        msg = ""
        # Step 1: Intensity factor checks
        if answer.np_intensity_factor >= 0.95:
            msg += " IF > 0.95"

        # Step 2: Pull watt limit checks
        pull_limit = rider.lookup_permissable_pull_watts(answer.p1_duration)
        if answer.p1_w >= pull_limit:
            msg += " p1 > limit"

        answer.diagnostic_message = msg
    return rider_answers

def make_a_pull_plan_with_a_sensible_top_speed(riders: list[ZsunRiderItem], pull_durations: list[float], lowest_conceivable_kph: list[float],
    precision: float = 0.1,
    max_iter: int = 20
) -> tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], Union[None, ZsunRiderItem]]:
    """
    Uses binary search to find the maximum speed before a diagnostic message appears.
    Returns (iterations, rider_pullplan_items, halting_rider).
    """
    # Initial lower and upper bounds
    lower = truncate(lowest_conceivable_kph[0], 0)
    upper = lower

    # Find an upper bound where a diagnostic message appears
    for _ in range(10):
        test_speeds = [upper] * len(riders)
        rider_pullplan_items = populate_rider_pull_plans(riders, pull_durations, test_speeds)
        if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
            break
        upper += 5.0  # Increase by a reasonable chunk
    else:
        # If we never find an upper bound, just return the last result
        return 1, rider_pullplan_items, None

    iterations : int = 0
    halting_rider : Union[None, ZsunRiderItem] = None
    last_valid_items : Union[None, defaultdict[ZsunRiderItem, RiderPullPlanItem]] = None # the last known good solution. not currently needed or used

    while (upper - lower) > precision and iterations < max_iter:
        mid = (lower + upper) / 2
        test_speeds = [mid] * len(riders)
        rider_pullplan_items = populate_rider_pull_plans(riders, pull_durations, test_speeds)
        iterations += 1
        if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
            upper = mid
            halting_rider = next(rider for rider, answer in rider_pullplan_items.items() if answer.diagnostic_message)
        else:
            lower = mid
            last_valid_items = rider_pullplan_items


    # Use the halting (upper) speed after binary search
    final_speeds = [upper] * len(riders)
    rider_pullplan_items = populate_rider_pull_plans(riders, pull_durations, final_speeds)
    if any(answer.diagnostic_message for answer in rider_pullplan_items.values()):
        halting_rider = next(rider for rider, answer in rider_pullplan_items.items() if answer.diagnostic_message)
    else:
        halting_rider = None

    return iterations, rider_pullplan_items, halting_rider

def make_a_pull_plan( args: Tuple[List[ZsunRiderItem], List[float], List[float]]
) -> Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], Union[None, ZsunRiderItem]]:
    # Unpack arguments
    riders, pull_durations, pull_speeds = args
    # Call the simulation for this combination
    return make_a_pull_plan_with_a_sensible_top_speed(riders, list(pull_durations), pull_speeds)

def search_for_optimal_pull_plans(riders: List[ZsunRiderItem],pull_duration_options: List[float], lower_bound_speed: float
) -> Tuple[List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
        int,  # total_alternatives investigated
        int,   # total_iterations done
        float]: # elapsed computer time in seconds

    # --- Input validation ---
    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plans.")
    if not pull_duration_options:
        raise ValueError("No permitted pull durations provided to search_for_optimal_pull_plans.")
    if any(d <= 0 or not np.isfinite(d) for d in pull_duration_options):
        raise ValueError("All permitted pull durations must be positive and finite.")
    if not np.isfinite(lower_bound_speed) or lower_bound_speed <= 0:
        raise ValueError("lower_bound_speed must be positive and finite.")

    start_time = time.time()


    all_combinations_of_pull_durations = list(itertools.product(pull_duration_options, repeat=len(riders)))
    seed_speed_array : list[float] = [lower_bound_speed] * len(riders)
    total_alternatives : int = len(all_combinations_of_pull_durations)
    total_iterations : int = 0

    if total_alternatives  > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_alternatives)

    # Prepare arguments for each process
    args_list = [(riders, pull_durations, seed_speed_array) for pull_durations in all_combinations_of_pull_durations]

    solutions: List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]] = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
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
                logger.error("Exception in make_a_pull_plan: %s", exc)

    fastest_speed_tuple = None
    fastest_speed : float = float('-inf')
    lowest_dispersion_tuple = None
    lowest_dispersion : float = float('inf')

    for iterations, rider_pullplan_items, halted_rider in solutions:
        total_iterations += iterations
        if halted_rider is None or rider_pullplan_items is None or not isinstance(rider_pullplan_items, dict):
            logger.warning("Invalid result in solutions list: %s", (iterations, rider_pullplan_items, halted_rider))
            continue
        halted_speed = rider_pullplan_items[halted_rider].speed_kph
        if not np.isfinite(halted_speed):
            logger.warning("Non-finite halted_speed encountered: %s", halted_speed)
            continue

        # Memo for fastest halted speed
        if halted_speed > fastest_speed:
            fastest_speed = halted_speed
            fastest_speed_tuple = (iterations, rider_pullplan_items, halted_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [answer.np_intensity_factor for answer in rider_pullplan_items.values() if hasattr(answer, "np_intensity_factor")]
        if not np_intensity_factors:
            logger.warning("No valid np_intensity_factors in rider_pullplan_items.")
            continue
        dispersion = np.std(np_intensity_factors)
        if not np.isfinite(dispersion):
            logger.warning("Non-finite dispersion encountered: %s", dispersion)
            continue
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_tuple = (iterations, rider_pullplan_items, halted_rider)

    # --- Output consistency ---
    if fastest_speed_tuple is None and lowest_dispersion_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plans: No valid solution found (both fastest_speed_tuple and lowest_dispersion_tuple are None)")
    elif fastest_speed_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plans: No valid solution found (fastest_speed_tuple is None)")
    elif lowest_dispersion_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plans: No valid solution found (lowest_dispersion_tuple is None)")

    end_time = time.time()
    elapsed_time = end_time - start_time
    return ([fastest_speed_tuple, lowest_dispersion_tuple], total_alternatives, total_iterations, elapsed_time)

    # Worker function to process a chunk

