from typing import  List, Tuple, Union
from collections import defaultdict
import time
import numpy as np
import itertools
import concurrent.futures
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderPullPlanItem
from jgh_formulae04 import populate_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions
from jgh_formulae06 import populate_pull_plan_from_exertions

import logging
from jgh_logging import jgh_configure_logging
import time
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

permitted_pull_durations = [30.0, 60.0, 120.0, 180.0, 240.0] # in seconds

def fmt(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 2 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.2e+03' or '12'.
    """
    return f"{x:.2g}"

def fmtl(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 4 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.234e+03' or '1234'.
    """
    return f"{x:.4g}"

def fmtc(x: Union[int, float]) -> str:
    """
    Format a number with thousands separators and up to 2 decimal places.
    For floats, trailing zeros and decimal points are removed if unnecessary.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1,234' or '1,234.56'.
    """
    if isinstance(x, int):
        return f"{x:,}"
    elif isinstance(x, float):
        return f"{x:,.2f}".rstrip('0').rstrip('.') if '.' in f"{x:,.2f}" else f"{x:,.2f}"
    else:
        return str(x)

def format_hms(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    # Format seconds with one leading zero if < 10, else no leading zero
    sec_str = f"{secs:03.1f}" if secs < 10 else f"{secs:0.1f}"
    if hours >= 1:
        return f"{int(hours)} hours {int(minutes):02} minutes {sec_str} seconds"
    elif minutes >= 1:
        return f"{int(minutes):02} minutes {sec_str} seconds"
    else:
        return f"{sec_str} seconds"

def truncate(f : float, n : int):
    factor = 10 ** n
    return int(f * factor) / factor

def log_rider_one_hour_speeds(riders: list[ZsunRiderItem], logger: logging.Logger):
    from tabulate import tabulate

    table = []
    for rider in riders:
        table.append([
            rider.name,
            fmt(rider.calculate_strength_wkg()),
            fmt(rider.get_zwiftracingapp_zpFTP_wkg()),
            fmt(rider.get_zsun_1_hour_wkg()),
            fmt(rider.calculate_speed_at_1_hour_watts()),
            fmt(rider.zsun_one_hour_watts),
            fmt(rider.calculate_speed_at_permitted_30sec_pull_watts()),
            fmt(rider.get_permitted_30sec_pull_watts()),
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

    rider_answer_items = populate_pull_plan_from_exertions(rider_exertions)

    rider_answer_items = diagnose_what_governed_the_top_speed(rider_answer_items)

    # log_pull_plan(f"{len(riders)} riders in paceline", rider_answer_items, logger)


    return rider_answer_items

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
    Returns (iterations, rider_answer_items, halting_rider).
    """
    # Initial lower and upper bounds
    lower = truncate(lowest_conceivable_kph[0], 0)
    upper = lower

    # Find an upper bound where a diagnostic message appears
    for _ in range(10):
        test_speeds = [upper] * len(riders)
        rider_answer_items = populate_rider_pull_plans(riders, pull_durations, test_speeds)
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            break
        upper += 5.0  # Increase by a reasonable chunk
    else:
        # If we never find an upper bound, just return the last result
        return 1, rider_answer_items, None

    iterations : int = 0
    halting_rider : Union[None, ZsunRiderItem] = None
    last_valid_items : Union[None, defaultdict[ZsunRiderItem, RiderPullPlanItem]] = None # the last known good solution. not currently needed or used

    while (upper - lower) > precision and iterations < max_iter:
        mid = (lower + upper) / 2
        test_speeds = [mid] * len(riders)
        rider_answer_items = populate_rider_pull_plans(riders, pull_durations, test_speeds)
        iterations += 1
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            upper = mid
            halting_rider = next(rider for rider, answer in rider_answer_items.items() if answer.diagnostic_message)
        else:
            lower = mid
            last_valid_items = rider_answer_items


    # Use the halting (upper) speed after binary search
    final_speeds = [upper] * len(riders)
    rider_answer_items = populate_rider_pull_plans(riders, pull_durations, final_speeds)
    if any(answer.diagnostic_message for answer in rider_answer_items.values()):
        halting_rider = next(rider for rider, answer in rider_answer_items.items() if answer.diagnostic_message)
    else:
        halting_rider = None

    return iterations, rider_answer_items, halting_rider

def make_a_pull_plan( args: Tuple[List[ZsunRiderItem], List[float], List[float]]
) -> Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], Union[None, ZsunRiderItem]]:
    # Unpack arguments
    riders, pull_durations, pull_speeds = args
    # Call the simulation for this combination
    return make_a_pull_plan_with_a_sensible_top_speed(riders, list(pull_durations), pull_speeds)

def search_for_optimal_pull_plans(riders: List[ZsunRiderItem],permitted_durations: List[float], lower_bound_speed: float
) -> Tuple[List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
        int,  # total_alternatives investigated
        int,   # total_iterations done
        float]: # elapsed computer time in seconds

    # --- Input validation ---
    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plans.")
    if not permitted_durations:
        raise ValueError("No permitted pull durations provided to search_for_optimal_pull_plans.")
    if any(d <= 0 or not np.isfinite(d) for d in permitted_durations):
        raise ValueError("All permitted pull durations must be positive and finite.")
    if not np.isfinite(lower_bound_speed) or lower_bound_speed <= 0:
        raise ValueError("lower_bound_speed must be positive and finite.")

    start_time = time.time()


    all_combinations = list(itertools.product(permitted_durations, repeat=len(riders)))
    seed_speed_array : list[float] = [lower_bound_speed] * len(riders)
    total_alternatives : int = len(all_combinations)
    total_iterations : int = 0

    if total_alternatives  > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_alternatives)

    # Prepare arguments for each process
    args_list = [(riders, pull_durations, seed_speed_array) for pull_durations in all_combinations]

    results: List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]] = []

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
                results.append(result)
            except Exception as exc:
                logger.error("Exception in make_a_pull_plan: %s", exc)

    fastest_tuple = None
    fastest_speed : float = float('-inf')
    lowest_dispersion_tuple = None
    lowest_dispersion : float = float('inf')

    for iterations, rider_answer_items, halted_rider in results:
        total_iterations += iterations
        if halted_rider is None or rider_answer_items is None or not isinstance(rider_answer_items, dict):
            logger.warning("Invalid result in results list: %s", (iterations, rider_answer_items, halted_rider))
            continue
        halted_speed = rider_answer_items[halted_rider].speed_kph
        if not np.isfinite(halted_speed):
            logger.warning("Non-finite halted_speed encountered: %s", halted_speed)
            continue

        # Memo for fastest halted speed
        if halted_speed > fastest_speed:
            fastest_speed = halted_speed
            fastest_tuple = (iterations, rider_answer_items, halted_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [answer.np_intensity_factor for answer in rider_answer_items.values() if hasattr(answer, "np_intensity_factor")]
        if not np_intensity_factors:
            logger.warning("No valid np_intensity_factors in rider_answer_items.")
            continue
        dispersion = np.std(np_intensity_factors)
        if not np.isfinite(dispersion):
            logger.warning("Non-finite dispersion encountered: %s", dispersion)
            continue
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_tuple = (iterations, rider_answer_items, halted_rider)

    # --- Output consistency ---
    if fastest_tuple is None and lowest_dispersion_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plans: No valid solution found (both fastest_tuple and lowest_dispersion_tuple are None)")
    elif fastest_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plans: No valid solution found (fastest_tuple is None)")
    elif lowest_dispersion_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plans: No valid solution found (lowest_dispersion_tuple is None)")

    end_time = time.time()
    elapsed_time = end_time - start_time
    return ([fastest_tuple, lowest_dispersion_tuple], total_alternatives, total_iterations, elapsed_time)
