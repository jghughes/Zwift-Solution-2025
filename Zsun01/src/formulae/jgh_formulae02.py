from typing import  List, DefaultDict, Tuple
import time
from typing import List
import numpy as np
from numpy.typing import NDArray

# from numpy import ndarray  # optional, for explicit ndarray type hints
from constants import SOLUTION_FILTERING_THRESHOLD
from jgh_number import safe_divide
from rolling_average import calculate_rolling_averages
from jgh_formatting import truncate 
from jgh_formulae01 import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_drag_ratio_in_paceline
from zsun_rider_item import ZsunItem
from computation_classes import RiderContributionItem, RiderExertionItem

import logging
from jgh_logging import jgh_configure_logging

# All of these functions are called during parallel processing. Logging forbidden

def calculate_kph_riding_alone(rider : ZsunItem, power: float) -> float:
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

def calculate_wattage_riding_alone(rider : ZsunItem, speed: float) -> float:
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

def calculate_wattage_riding_in_the_paceline(rider : ZsunItem, speed: float, position: int
) -> float:
    """
    Calculate the wattage required for a rider given their speed and position 
    in the peloton.

    Args:
    rider (ZsunItem): The rider object.
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

    return adjusted_power

def calculate_speed_riding_in_the_paceline(rider : ZsunItem, power: float, position: int
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
        
    return speed_kph

def calculate_speed_at_standard_00sec_pull_watts(rider : ZsunItem) -> float:
      
    return calculate_speed_at_standard_30sec_pull_watts(rider)

def calculate_speed_at_standard_30sec_pull_watts(rider : ZsunItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_30sec_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return speed_kph

def calculate_speed_at_standard_1_minute_pull_watts(rider : ZsunItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_1_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return speed_kph

def calculate_speed_at_standard_2_minute_pull_watts(rider : ZsunItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_2_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return speed_kph

def calculate_speed_at_standard_3_minute_pull_watts(rider : ZsunItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_3_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return speed_kph

def calculate_speed_at_standard_4_minute_pull_watts(rider : ZsunItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_4_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return speed_kph

def calculate_speed_at_n_second_watts(rider : ZsunItem, seconds: float) -> float:
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
        
    return speed_kph

def calculate_speed_at_one_hour_watts(rider : ZsunItem) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_one_hour_watts(), rider.weight_kg, rider.height_cm)
        
    return speed_kph

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

def calculate_overall_average_speed_of_paceline_kph(exertions: DefaultDict[ZsunItem, List[RiderExertionItem]]) -> float:
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

def calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders: List[ZsunItem]) -> float:

    _, _, lower_bound_pull_rider_speed   = calculate_lower_bound_paceline_speed(riders)
    _, _, lower_bound_1_hour_rider_speed = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)

    safe_lowest_bound_speed = min(truncate(lower_bound_pull_rider_speed, 0), truncate(lower_bound_1_hour_rider_speed, 0))

    return safe_lowest_bound_speed

def calculate_overall_intensity_factor_of_rider_contribution(rider: ZsunItem, rider_contribution: RiderContributionItem) -> float:
    """
    Calculate the intensity factor for a given rider and their contribution plan.

    The intensity factor is defined as the ratio of the normalized watts for a rider's planned effort
    to their one-hour power (FTP). This metric is used to assess how hard a rider is working relative
    to their sustainable threshold.

    Args:
        rider (ZsunItem): The rider for whom the intensity factor is being calculated.
        rider_contribution (RiderContributionItem): The contribution plan containing normalized watts for the rider.

    Returns:
        float: The calculated intensity factor. Returns 0.0 if the rider's one-hour watts is zero.

    """

    return  safe_divide(rider_contribution.normalized_watts, rider.get_one_hour_watts())

def calculate_upper_bound_paceline_speed(riders: List[ZsunItem]) -> Tuple[ZsunItem, float, float]:
    """
    Determines the maxima of permitted pull speed among all standard pull durations of all riders.
    For each rider and each permitted pull duration (30s, 60s, 120s, 180s, 240s), this function calculates the speed
    the rider goes at their permitted pull watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall fastest speed found.
    Args:
        riders (list[ZsunItem]): List of ZsunItem objects representing the riders.
    Returns:
        Tuple[ZsunItem, float, float]: A tuple containing:
            - The ZsunItem with the highest speed,
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

def calculate_lower_bound_paceline_speed(riders: List[ZsunItem]) -> Tuple[ZsunItem, float, float]:
    """
    Determines the minima permitted pull speed among all standard pull durations of all riders.

    For each rider and each permitted pull duration (30s, 60s, 120s, 180s, 240s), this function calculates the speed
    the rider goes at their permitted pull watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall slowest speed found.

    Args:
        riders (list[ZsunItem]): List of ZsunItem objects representing the riders.

    Returns:
        Tuple[ZsunItem, float, float]: A tuple containing:
            - The ZsunItem with the lowest speed,
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

def calculate_lower_bound_paceline_speed_at_one_hour_watts(riders: List[ZsunItem]) -> Tuple[ZsunItem, float, float]:
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

def calculate_upper_bound_paceline_speed_at_one_hour_watts(riders: List[ZsunItem]) -> Tuple[ZsunItem, float, float]:
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

def calculate_dispersion_of_intensity_of_effort(rider_contributions: DefaultDict[ZsunItem, RiderContributionItem]) -> float:
    """
    Calculate the dispersion (standard deviation) of intensity factors among all riders who performed a pull.

    This function computes the standard deviation of the intensity factors for all riders whose
    primary pull duration (`p1_duration`) is not zero. Riders with `p1_duration == 0` are excluded
    from the calculation, as they did not perform a pull.

    Args:
        rider_contributions (DefaultDict[ZsunItem, RiderContributionItem]):
            A mapping of riders to their contribution data, including intensity factor and pull duration.

    Returns:
        float: The standard deviation of intensity factors among all pullers.
               Returns 100 if there are no valid pullers or if the result is not finite.
    """

    array_of_rider_effort_intensity_factors = [
        contribution.intensity_factor
        for _, contribution in rider_contributions.items()
        if contribution.p1_duration != 0
    ]
    if not array_of_rider_effort_intensity_factors:
        return 100  # arbitrarily big
    std_deviation_of_intensity_factors = float(np.std(array_of_rider_effort_intensity_factors))
    if not np.isfinite(std_deviation_of_intensity_factors):
        return 100  # arbitrarily big

    return std_deviation_of_intensity_factors

def arrange_riders_in_optimal_order(riders: List[ZsunItem]) -> List[ZsunItem]:
    """
    Arrange the riders in an optimal order based on their strength metric.

    Riders are ranked according to their strength, from strongest to weakest. 
    The strongest rider is ranked 1, and the weakest rider is ranked n. 
    The strength of a rider is determined by the value returned from the 
    `ZsunItem.get_strength_wkg()` method.

    To arrange the riders in optimal order, the riders are interleaved as follows:
    - The strongest rider is placed at the front (position 1).
    - The second strongest rider is placed at the back (position n).
    - The third strongest rider is placed behind the front (position 2).
    - The fourth strongest rider is placed ahead of the second strongest (position n-1).
    - This pattern continues until all riders are placed.

    Args:
        riders (List[ZsunItem]): The list of riders to be arranged.

    Returns:
        List[ZsunItem]: The list of riders arranged in the optimal interleaved order.
    """
    # Step 1: Calculate the strength of each rider and sort them in descending order
    sorted_riders = sorted(riders, key=lambda rider: rider.get_strength_wkg(), reverse=True)

    # Step 2: Create an empty list to hold the optimal order
    n = len(sorted_riders)
    optimal_order: List[ZsunItem] = [None] * n  # type: ignore

    # Step 3: Fill front, 2nd, 3rd, ... (odd positions) with 1st, 3rd, 5th, ...
    front_idx = 0
    for i in range(0, n, 2):
        optimal_order[front_idx] = sorted_riders[i]
        front_idx += 1

    # Step 4: Fill back, 2nd last, ... (even positions from end) with 2nd, 4th, 6th, ... in reverse
    back_idx = n - 1
    for i in range(1, n, 2):
        optimal_order[back_idx] = sorted_riders[i]
        back_idx -= 1

    return optimal_order

def select_n_strongest_riders(riders: List[ZsunItem], n : int) -> List[ZsunItem]:
    if not riders:
        return []

    #sort riders according to 1 minute pull speed
    riders.sort(key=lambda r: r.get_strength_wkg(), reverse=True)

    strong_riders: List[ZsunItem] = []

    if len(riders) <= n:
        return riders
    else:
        # select the four strongest riders only 

        strong_riders = riders[:n]

    return strong_riders

def prune_all_sequences_of_pull_periods_in_the_total_solution_space(
    pull_period_sequences_being_pruned: NDArray[np.float64],
    riders: List[ZsunItem]
) -> NDArray[np.float64]:
    """
    Efficiently prunes a large set of paceline pull period sequences (pull period assignments) using empirical rules
    based on rider strength, to reduce the solution space for further computation.

    This function applies two main filters:
      1. No rider (except the second weakest) can have a pull period shorter than the weakest rider's pull period.
      2. For n in 1..12 (or up to the number of riders), no rider (except the top n-1 strongest) can have a pull
         period longer than the nth strongest rider's pull period.

    Filtering stops as soon as the number of remaining pull period sequences drops below the configured solution space constraint.

    Args:
        pull_period_sequences_being_pruned (NDArray[np.float_]):
            2D NumPy array of candidate paceline pull period sequences, where each row is a sequence of pull periods (seconds)
            for each rider.
        riders (List[ZsunItem]):
            List of rider objects, used to determine rider strength order for filtering.

    Returns:
        NDArray[np.float_]:
            The filtered 2D NumPy array of paceline pull period sequences, reduced according to empirical rules.

    Notes:
        - Filtering is only applied if the number of input sequences exceeds the solution space size constraint.
        - Uses NumPy for efficient vectorized filtering.
        - Intended to improve computational performance by discarding unlikely or suboptimal sequences before
          more expensive computations are performed.
    """
    if len(pull_period_sequences_being_pruned) < SOLUTION_FILTERING_THRESHOLD + 1:
        return pull_period_sequences_being_pruned

    arr = pull_period_sequences_being_pruned
    strengths = np.array([r.get_strength_wkg() for r in riders])
    sorted_indices = np.argsort(strengths)
    weakest_idx = sorted_indices[0]
    second_weakest_idx = sorted_indices[1] if len(sorted_indices) > 1 else None

    # Filter 1: No rider (except 2nd weakest) can have a pull shorter than the weakest
    weakest_values = arr[:, weakest_idx][:, np.newaxis]
    mask = np.ones(arr.shape[0], dtype=bool)
    for idx in range(arr.shape[1]):
        if idx == second_weakest_idx:
            continue
        mask &= arr[:, idx] >= weakest_values[:, 0]
    arr = arr[mask]
    if len(arr) < SOLUTION_FILTERING_THRESHOLD:
        return arr

    # Filter 2: For n in 1..12, no rider (except top n-1) can have a pull longer than the nth strongest
    strengths_desc = np.argsort(-strengths)
    for n in range(1, min(13, len(riders) + 1)):
        indices = strengths_desc[:n]
        nth_strongest_idx = strengths_desc[n-1]
        nth_values = arr[:, nth_strongest_idx][:, np.newaxis]
        mask = np.ones(arr.shape[0], dtype=bool)
        for idx in range(arr.shape[1]):
            if idx in indices[:-1]:
                continue
            mask &= arr[:, idx] <= nth_values[:, 0]
        arr = arr[mask]
        if len(arr) < SOLUTION_FILTERING_THRESHOLD:
            return arr

    return arr

def generate_all_sequences_of_pull_periods_in_the_total_solution_space(
    length_of_paceline: int,
    standard_pull_periods_seconds: List[float]
) -> NDArray[np.float64]:
    """
    Generate all possible assignments of pull periods to a paceline as a NumPy array.

    This function produces the Cartesian product of the allowed pull periods for each rider.
    For n riders and k allowed pull periods, it generates k^n possible sequences.
    Each row in the returned array is a sequence of pull periods for the paceline.

    For n riders and k allowed pull periods, it generates k^n possible sequences. 
    Six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. 
    This is a large number, but it is manageable for the algorithm to process within 
    a reasonable time frame, especially with the filtering applied later in the process.

    Args:
        length_of_paceline (int): Number of riders in the paceline.
        standard_pull_periods_seconds (List[float]): Allowed pull durations (in seconds).

    Returns:
        NDArray[np.float64]: All possible paceline pull period sequences as a 2D NumPy array.
    """
    # Create a meshgrid for all possible pull period assignments
    grids: tuple[NDArray[np.float64], ...] = np.meshgrid(*([standard_pull_periods_seconds] * length_of_paceline), indexing='ij')
    # Stack and reshape to get all combinations as rows
    all_combinations: NDArray[np.float64] = np.stack(grids, axis=-1).reshape(-1, length_of_paceline)

    return all_combinations

def main():
    from handy_utilities import read_json_dict_of_ZsunDTO
    from repository_of_teams import get_team_riderIDs
    from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST
    # from computation_classes import PacelineIngredientsItem

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems_2025_07_08.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_ZsunItems = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs = get_team_riderIDs("test")
    riders = [dict_of_ZsunItems[rid] for rid in riderIDs]

    start_time = time.perf_counter()

    universe_of_sequences = generate_all_sequences_of_pull_periods_in_the_total_solution_space(len(riders), STANDARD_PULL_PERIODS_SEC_AS_LIST)
    
    elapsed_time = time.perf_counter() - start_time

    logger.debug(f"Generated universe_of_sequences of {len(universe_of_sequences)} paceline rotation sequences in {elapsed_time} seconds.")

    start_time = time.perf_counter()

    pruned_sequences = prune_all_sequences_of_pull_periods_in_the_total_solution_space(universe_of_sequences, riders)

    elapsed_time = time.perf_counter() - start_time

    for sequence in pruned_sequences:
        logger.debug(sequence)

    logger.debug(f"Generated pruned_sequences of {len(pruned_sequences)} paceline rotation sequences in {elapsed_time} seconds..")

if __name__ == "__main__":
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger("numba").setLevel(logging.ERROR)

    main()
