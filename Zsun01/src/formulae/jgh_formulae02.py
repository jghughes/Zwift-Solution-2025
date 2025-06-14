from typing import  List, DefaultDict, Callable, Tuple
import itertools
from constants import SOLUTION_SPACE_SIZE_CONSTRAINT
from jgh_number import safe_divide
from rolling_average import calculate_rolling_averages
from jgh_formatting import truncate 
from jgh_formulae01 import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_drag_ratio_in_paceline
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderContributionItem, RiderExertionItem

def calculate_kph_riding_alone(rider : ZsunRiderItem, power: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight_kg (kg), and 
    height_cm (cm) using the Newton-Raphson method.

    Args:
    power (float): The power in watts.

    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(power, rider.weight_kg, rider.height_cm)
    return speed_kph

def calculate_wattage_riding_alone(rider : ZsunRiderItem, speed: float) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), weight_kg (kg), and 
    height_cm (cm).

    Args:
    speed (float): The speed in km/h.

    Returns:
    float: The calculated power in watts.
    """
    # Calculate the power using the estimate_watts_from_speed function
    power = estimate_watts_from_speed(speed, rider.weight_kg, rider.height_cm)
    return power

def calculate_wattage_riding_in_the_paceline(rider : ZsunRiderItem, speed: float, position: int
) -> float:
    """
    Calculate the wattage required for a rider given their speed and position 
    in the peloton.

    Args:
    rider (ZsunRiderItem): The rider object.
    speed (float): The speed in km/h.
    position (int): The position in the peloton.

    Returns:
    float: The required wattage in watts.
    """
    # Calculate the base power required for the given speed
    base_power = calculate_wattage_riding_alone(rider, speed)

    # Get the power factor based on the rider's position in the peloton
    power_factor = estimate_drag_ratio_in_paceline(position)

    # Adjust the power based on the power factor
    adjusted_power = base_power * power_factor

    return round(adjusted_power, 3)

def calculate_speed_riding_in_the_paceline(rider : ZsunRiderItem, power: float, position: int
) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    and position in the peloton.

    Args:
    power (float): The power output in watts.
    position (int): The position in the peloton.

    Returns:
    float: The estimated speed in km/h.
    """
    # Get the power factor based on the rider's position in the peloton
    power_factor = estimate_drag_ratio_in_paceline(position)

    # Adjust the power based on the power factor
    adjusted_watts = safe_divide(power, power_factor)

    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(adjusted_watts, rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_30sec_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_30sec_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_1_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_1_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_2_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_2_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_3_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_3_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_4_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_4_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_n_second_watts(rider : ZsunRiderItem, seconds: float) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    for a specific duration in seconds.
    Args:
    seconds (float): The duration in seconds.
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_n_second_watts(seconds), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_one_hour_watts(rider : ZsunRiderItem) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_one_hour_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_overall_average_watts(efforts: List[RiderExertionItem]) -> float:
    """
    Calculate the average power for a list of efforts.
    The average power is calculated as the total work done (in kilojoules) divided by 
    the total duration (in seconds). The function sums the kilojoules for each workload 
    item and divides by the total duration to obtain the average power.

    Args:
        efforts (List[RiderExertionItem]): The list of efforts.
    Returns:
        float: The average power.
    """
    if not efforts:
        return 0

    total_kilojoules = sum(item.kilojoules for item in efforts)
    total_duration = sum(item.duration for item in efforts)
    average_watts = safe_divide(1_000 * total_kilojoules, total_duration)
    return average_watts


def calculate_overall_normalized_watts(efforts: List[RiderExertionItem]) -> float:
    """
    Calculate the normalized power for a list of efforts.

    Normalized Power (NP) is a metric used to better quantify the physiological 
    demands of a workout compared to average power. It accounts for the variability 
    in power output and provides a more accurate representation of the effort 
    required. The calculation involves several steps:

    1. Create a list of instantaneous wattages for every second of the durations 
       of all efforts.
    2. Calculate the 30-second rolling average power.
    3. Raise the smoothed power values to the fourth power.
    4. Calculate the average of these values.
    5. Take the fourth root of the average.

    Args:
        efforts (List[RiderExertionItem]): The list of efforts. 
        Each item contains the wattage and duration for a specific segment of the 
        workout.

    Returns:
        float: The normalized power.

    Example:
        >>> efforts = [
        ...     RiderExertionItem(position=1, speed=35, duration=60, wattage=200, wattage_ftp_ratio=0.8, kilojoules=12000),
        ...     RiderExertionItem(position=2, speed=30, duration=30, wattage=180, wattage_ftp_ratio=0.72, kilojoules=5400)
        ... ]
        >>> calculate_overall_normalized_watts(efforts)
        192.0

    In this example, the normalized power is calculated for two efforts. 
    The first item has a duration of 60 seconds and a wattage of 200, and the 
    second item has a duration of 30 seconds and a wattage of 180. The function 
    computes the normalized power based on these values.
    """
    if not efforts:
        return 0

    # Create a list of instantaneous wattages for every second of the durations of all efforts
    instantaneous_wattages: List[float] = []
    for item in efforts:
        instantaneous_wattages.extend([item.wattage] * int(item.duration))

    # Calculate rolling average power - TrainingPeaks uses a 30-second rolling average
    # Our pulls are 30, 60, and 120 seconds long, so we'll use a (arbitrary) 5-second rolling average
    rolling_avg_power = calculate_rolling_averages(instantaneous_wattages, 5)

    # Raise the smoothed power values to the fourth power
    rolling_avg_power_4 = [p ** 4 for p in rolling_avg_power]

    # Calculate the average of these values
    mean_power_4 = safe_divide(sum(rolling_avg_power_4), len(rolling_avg_power_4))

    # Take the fourth root of the average
    normalized_watts = mean_power_4 ** 0.25

    return normalized_watts

def calculate_overall_average_speed_of_paceline_kph(exertions: DefaultDict[ZsunRiderItem, List[RiderExertionItem]]) -> float:
    """
    Calculate the average speed (km/h) for the rider is the paceline to whom 
    this list of paceline efforts belong.

    The average speed is calculated as the total distance covered divided by the total duration.
    Each effort should have a speed (km/h) and a duration (seconds).

    Args:
        efforts (List[RiderExertionItem]): The list of efforts.

    Returns:
        float: The average speed in km/h.
    """
    if not exertions:
        return 0.0

    # arbitrarily get the first RiderExertionItem in the exertions dict
    efforts = next(iter(exertions.values()))

    total_distance_km = sum(safe_divide((item.speed_kph * item.duration), 3600.0) for item in efforts)
    total_duration_sec = sum(item.duration for item in efforts)

    if total_duration_sec == 0:
        return 0.0

    average_speed_kph = safe_divide(total_distance_km, safe_divide(total_duration_sec, 3600.0))

    return average_speed_kph

def calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders: List[ZsunRiderItem]) -> float:

    _, _, lower_bound_pull_rider_speed   = calculate_lower_bound_paceline_speed(riders)
    _, _, lower_bound_1_hour_rider_speed = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)

    safe_lowest_bound_speed = round(min(truncate(lower_bound_pull_rider_speed, 0), truncate(lower_bound_1_hour_rider_speed, 0)), 1)

    return safe_lowest_bound_speed

def calculate_overall_intensity_factor_of_rider_contribution(rider: ZsunRiderItem, rider_contribution: RiderContributionItem) -> float:
    """
    Calculate the intensity factor for a given rider and their contribution plan.

    The intensity factor is defined as the ratio of the normalized watts for a rider's planned effort
    to their one-hour power (FTP). This metric is used to assess how hard a rider is working relative
    to their sustainable threshold.

    Args:
        rider (ZsunRiderItem): The rider for whom the intensity factor is being calculated.
        rider_contribution (RiderContributionItem): The contribution plan containing normalized watts for the rider.

    Returns:
        float: The calculated intensity factor. Returns 0.0 if the rider's one-hour watts is zero.

    """

    return  safe_divide(rider_contribution.normalized_watts, rider.get_one_hour_watts())


def calculate_upper_bound_paceline_speed(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
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
    fastest_duration = 30.0  # arbitrary short
    highest_speed = 0.0  # Arbitrarily low speed
    duration_functions = [
        (30.0, calculate_speed_at_standard_30sec_pull_watts),
        (60.0, calculate_speed_at_standard_1_minute_pull_watts),
        (120.0, calculate_speed_at_standard_2_minute_pull_watts),
        (180.0, calculate_speed_at_standard_3_minute_pull_watts),
        (240.0, calculate_speed_at_standard_4_minute_pull_watts),
    ]
    for rider in riders:
        for duration, func in duration_functions:
            speed = func(rider)
            if speed > highest_speed:
                highest_speed = speed
                fastest_rider = rider
                fastest_duration = duration
    return fastest_rider, fastest_duration, highest_speed

def calculate_lower_bound_paceline_speed(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
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
    slowest_duration = 30.0  # arbitrary short
    slowest_speed = 100.0  # Arbitrarily high speed

    duration_functions = [
        (30.0, calculate_speed_at_standard_30sec_pull_watts),
        (60.0, calculate_speed_at_standard_1_minute_pull_watts),
        (120.0, calculate_speed_at_standard_2_minute_pull_watts),
        (180.0, calculate_speed_at_standard_3_minute_pull_watts),
        (240.0, calculate_speed_at_standard_4_minute_pull_watts),
    ]

    for rider in riders:
        for duration, func in duration_functions:
            speed = func(rider)
            if speed < slowest_speed:
                slowest_speed = speed
                slowest_rider = rider
                slowest_duration = duration

    return slowest_rider, slowest_duration, slowest_speed

def calculate_lower_bound_paceline_speed_at_one_hour_watts(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    slowest_rider = riders[0]
    slowest_duration = 3600.0  # 1 hour in seconds
    slowest_speed = calculate_speed_at_one_hour_watts(slowest_rider)

    for rider in riders:
        speed = calculate_speed_at_one_hour_watts(rider)
        if speed < slowest_speed:
            slowest_speed = speed
            slowest_rider = rider
            # duration is always 1 hour for this function
            slowest_duration = 3600.0

    return slowest_rider, slowest_duration, slowest_speed

def calculate_upper_bound_paceline_speed_at_one_hour_watts(riders: List[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    fastest_rider = riders[0]
    fastest_duration = 3600.0  # 1 hour in seconds
    highest_speed = calculate_speed_at_one_hour_watts(fastest_rider)
    for rider in riders:
        speed = calculate_speed_at_one_hour_watts(rider)
        if speed > highest_speed:
            highest_speed = speed
            fastest_rider = rider
            # duration is always 1 hour for this function
            fastest_duration = 3600.0
    return fastest_rider, fastest_duration, highest_speed


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

def prune_the_scaffold_of_the_total_solution_space(
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




