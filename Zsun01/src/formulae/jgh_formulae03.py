
from typing import Dict, List, Tuple

import numpy as np
from numpy.typing import NDArray
from jgh_number import safe_divide


from paceline_modelling_items import PacelineIngredientsItem, RiderContributionItem, RiderExertionItem
from constants import ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL
from jgh_formatting import truncate
from jgh_formulae00 import calculate_drag_ratio_in_paceline, calculate_watts_from_speed
from jgh_formulae01 import solve_for_speed_from_wattage_using_binary_search
from jgh_formulae02 import solve_for_speed_at_standard_30sec_pull_watts, solve_for_speed_at_standard_1_minute_pull_watts, solve_for_speed_at_standard_2_minute_pull_watts, solve_for_speed_at_standard_3_minute_pull_watts, solve_for_speed_at_standard_4_minute_pull_watts, solve_for_speed_at_n_second_watts, solve_for_speed_at_one_hour_watts, solve_for_speed_at_one_hour_watts
from jgh_power_curve_fit_models import decay_model_numpy
from calc_rolling_average import calculate_rolling_averages
from rider_compute_item import RiderComputeItem

# All of these functions are called during parallel processing. Logging forbidden
def calculate_power_riding_in_the_paceline(rider : RiderComputeItem, speed: float, position: int, slope_pc: float = 0.0) -> float:
    """
    Calculate required wattage (watts) for a rider at given speed
    (km/h), position, slope (%), weight (kg), and height (cm) in the
    paceline.
    """
    base_power = calculate_watts_from_speed(speed, rider.weight_kg, rider.height_cm, slope_pc)
    power_factor = calculate_drag_ratio_in_paceline(position)
    adjusted_power = base_power * power_factor

    return adjusted_power

def solve_for_speed_riding_in_the_paceline(rider : RiderComputeItem, power: float, position: int, slope_pc: float = 0.0) -> float:
    """
    Calculate speed (km/h) for a rider at given power (watts),
    position, slope (%), weight (kg), and height (cm) in the paceline.
    """
    power_factor = calculate_drag_ratio_in_paceline(position)
    adjusted_watts = safe_divide(power, power_factor)
    speed_kph = solve_for_speed_from_wattage_using_binary_search(adjusted_watts, rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def calculate_overall_average_watts(efforts: List[RiderExertionItem]) -> float:
    """
    Calculate average wattage (watts) from a list of rider efforts with
    given wattage and duration (seconds).
    """
    if not efforts:
        return 0

    total_kilojoules = sum(item.kilojoules for item in efforts)
    total_duration = sum(item.duration for item in efforts)
    average_watts = safe_divide(1_000 * total_kilojoules, total_duration)
    return average_watts

def calculate_overall_normalized_watts(efforts: List[RiderExertionItem]) -> float:
    """
    Calculate normalized power (watts) for a list of efforts accounting
    for variability in power output. Creates instantaneous wattages for
    each second, applies a 5-second rolling average, raises to the fourth
    power, averages, and takes the fourth root.
    """

    if not efforts:
        return 0

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

def calculate_overall_average_speed_of_paceline_kph(exertions: Dict[RiderComputeItem, List[RiderExertionItem]]) -> float:
    """
    Calculate average paceline speed (km/h) as total distance covered
    divided by total duration (seconds) from rider exertions.
    """
    if not exertions:
        return 0.0

    # arbitrarily get the first_name RiderExertionItem in the exertions dict
    efforts = next(iter(exertions.values()))

    total_distance_km = sum(safe_divide((item.speed_kph * item.duration), 3600.0) for item in efforts)
    total_duration_sec = sum(item.duration for item in efforts)

    if total_duration_sec == 0:
        return 0.0

    average_speed_kph = safe_divide(total_distance_km, safe_divide(total_duration_sec, 3600.0))

    return average_speed_kph

def solve_for_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders: List[RiderComputeItem], slope: float = 0.0) -> float:

    _, _, lower_bound_pull_rider_speed   = solve_for_lower_bound_paceline_speed(riders, slope)
    _, _, lower_bound_1_hour_rider_speed = solve_for_lower_bound_paceline_speed_at_one_hour_watts(riders, slope)

    safe_lowest_bound_speed = min(truncate(lower_bound_pull_rider_speed, 0), truncate(lower_bound_1_hour_rider_speed, 0))

    return safe_lowest_bound_speed

def calculate_overall_intensity_factor_of_rider_contribution(rider: RiderComputeItem, rider_contribution: RiderContributionItem) -> float:
    """
    Calculate intensity factor as the ratio of normalized watts to
    one-hour power (FTP).
    """
    return  safe_divide(rider_contribution.normalized_watts, rider.get_1_hour_curvefit_watts())

def solve_for_upper_bound_paceline_speed(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> Tuple[RiderComputeItem, float, float]:
    """
    Find maximum permitted pull speed across all riders and standard
    durations (30s-240s). This function calculates the speed the rider 
    can go given their permitted pull watts for that duration. 
    Returns: (RiderComputeItem, duration in seconds, speed in kph).
    """
    fastest_rider = riders[0]
    fastest_duration = 30.0  # arbitrary short
    highest_speed = 0.0  # Arbitrarily low speed
    duration_functions = [
        (30.0, solve_for_speed_at_standard_30sec_pull_watts),
        (60.0, solve_for_speed_at_standard_1_minute_pull_watts),
        (120.0, solve_for_speed_at_standard_2_minute_pull_watts),
        (180.0, solve_for_speed_at_standard_3_minute_pull_watts),
        (240.0, solve_for_speed_at_standard_4_minute_pull_watts),
    ]
    for rider in riders:
        for duration, func in duration_functions:
            speed = func(rider, slope_pc)
            if speed > highest_speed:
                highest_speed = speed
                fastest_rider = rider
                fastest_duration = duration
    return fastest_rider, fastest_duration, highest_speed

def solve_for_lower_bound_paceline_speed(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> Tuple[RiderComputeItem, float, float]:
    """
    Determines the minima permitted pull speed among all standard 
    pull durations of all riders. For each rider and each permitted
    pull duration (30s, 60s, 120s, 180s, 240s), this function 
    calculates the speed the rider goes at their permitted pull 
    watts for that duration. It returns the rider, duration, and speed
    corresponding to the overall slowest speed found. Returns a tuple 
    of (RiderComputeItem, duration in seconds, speed in kph) 
    for the slowest rider and duration.
    """
    slowest_rider = riders[0]
    slowest_duration = 30.0  # arbitrary short
    slowest_speed = 100.0  # Arbitrarily high speed

    duration_functions = [
        (30.0, solve_for_speed_at_standard_30sec_pull_watts),
        (60.0, solve_for_speed_at_standard_1_minute_pull_watts),
        (120.0, solve_for_speed_at_standard_2_minute_pull_watts),
        (180.0, solve_for_speed_at_standard_2_minute_pull_watts),
        (240.0, solve_for_speed_at_standard_4_minute_pull_watts),
    ]

    for rider in riders:
        for duration, func in duration_functions:
            speed = func(rider, slope_pc)
            if speed < slowest_speed:
                slowest_speed = speed
                slowest_rider = rider
                slowest_duration = duration

    return slowest_rider, slowest_duration, slowest_speed

def solve_for_lower_bound_paceline_speed_at_one_hour_watts(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> Tuple[RiderComputeItem, float, float]:
    # (rider, duration_sec, speed_kph)
    slowest_rider = riders[0]
    slowest_duration = 3600.0  # 1 hour in seconds
    slowest_speed = solve_for_speed_at_one_hour_watts(slowest_rider, slope_pc)

    for rider in riders:
        speed = solve_for_speed_at_one_hour_watts(rider, slope_pc)
        if speed < slowest_speed:
            slowest_speed = speed
            slowest_rider = rider
            # duration is always 1 hour for this function
            slowest_duration = 3600.0

    return slowest_rider, slowest_duration, slowest_speed

def solve_for_upper_bound_paceline_speed_at_one_hour_watts(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> Tuple[RiderComputeItem, float, float]:
    # (rider, duration_sec, speed_kph)
    fastest_rider = riders[0]
    fastest_duration = 3600.0  # 1 hour in seconds
    highest_speed = solve_for_speed_at_one_hour_watts(fastest_rider, slope_pc)
    for rider in riders:
        speed = solve_for_speed_at_one_hour_watts(rider, slope_pc)
        if speed > highest_speed:
            highest_speed = speed
            fastest_rider = rider
            # duration is always 1 hour for this function
            fastest_duration = 3600.0
    return fastest_rider, fastest_duration, highest_speed

def calculate_dispersion_of_intensity_of_effort(rider_contributions: Dict[RiderComputeItem, RiderContributionItem]) -> float:
    """
    Calculate the dispersion (standard deviation) of 
    intensity factors among all riders who performed a pull.

    This function computes the standard deviation of 
    the intensity factors for all riders whose primary pull 
    duration (`p1_duration`) is not zero. Riders with 
    `p1_duration == 0` are excluded from the calculation, as 
    they did not perform a pull.Returns the standard 
    deviation of intensity factors among all pullers.
    Returns 100 if there are no valid pullers or if the 
    result is not finite.
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

def arrange_riders_by_30_sec_strength(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_30sec_wkg(), reverse=True)
    return sorted_riders

def arrange_riders_by_1_minute_strength(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_1_minute_wkg(), reverse=True)
    return sorted_riders

def arrange_riders_by_40_minute_strength(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_40_minute_wkg(), reverse=True)
    return sorted_riders

def arrange_riders_by_zwiftracingapp_zpFTP_strength(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.get_zwiftracingapp_zpFTP_wkg(), reverse=True)
    return sorted_riders

def arrange_riders_by_velo_rating(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.velo_rating_30_days, reverse=True)
    return sorted_riders

def arrange_riders_interleaved_by_1_minute_strength(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    """
    Arrange the riders in an optimal order based on their strength metric.

    Riders are ranked according to their strength, from strongest to weakest. 
    The strongest rider is ranked 1, and the weakest rider is ranked n. 
    The strength of a rider is determined by the value returned from the 
    `RiderComputeItem.get_proxy_1_minute_wkg()` method.

    To arrange the riders in optimal order, the riders are interleaved as follows:
    - The strongest rider is placed at the front (position 1).
    - The second strongest rider is placed at the back (position n).
    - The third strongest rider is placed behind the front (position 2).
    - The fourth strongest rider is placed ahead of the second strongest (position n-1).
    - This pattern continues until all riders are placed.

    Returns:
        List[RiderComputeItem]: The list of riders arranged in the optimal interleaved order.
    """
    # Step 1: Calculate the strength of each rider and sort them in descending order
    sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_1_minute_wkg(), reverse=True)

    # Step 2: Create an empty list to hold the optimal order
    n = len(sorted_riders)
    optimal_order: List[RiderComputeItem] = [None] * n  # type: ignore

    # Step 3: Fill front, 2nd, 3rd, ... (odd positions) with 1st, 3rd, 5th, ...
    front_idx = 0
    for i in range(0, n, 2):
        optimal_order[front_idx] = sorted_riders[i]
        front_idx += 1

    # Step 4: Fill back, 2nd last_name, ... (even positions from end) with 2nd, 4th, 6th, ... in reverse
    back_idx = n - 1
    for i in range(1, n, 2):
        optimal_order[back_idx] = sorted_riders[i]
        back_idx -= 1

    return optimal_order

def arrange_riders_by_name(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    """
    Arrange the riders alphabetically. Returns the List[RiderComputeItem] 
    of sorted riders.
    """
    sorted_riders = sorted(riders, key=lambda rider: rider.name, reverse=False)

    return sorted_riders

def select_n_riders_at_the_top_of_the_list(riders: List[RiderComputeItem], n : int) -> List[RiderComputeItem]:
    if not riders:
        return []

    # riders.sort(key=lambda r: r.get_proxy_1_minute_wkg(), reverse=True)

    topmost_riders: List[RiderComputeItem] = []

    if len(riders) <= n:
        return riders
    else:
        # we assume the riders have already been sorted from best to worst. we just take the top n
        topmost_riders = riders[:n]

    return topmost_riders

def prune_all_sequences_of_pull_periods_in_the_total_solution_space(pull_period_sequences_being_pruned: NDArray[np.float64],
    riders: List[RiderComputeItem]
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
        riders (List[RiderComputeItem]):
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
    if len(pull_period_sequences_being_pruned) < ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL + 1:
        return pull_period_sequences_being_pruned

    arr = pull_period_sequences_being_pruned
    strengths = np.array([r.get_proxy_1_minute_wkg() for r in riders])
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
    if len(arr) < ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL:
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
        if len(arr) < ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL:
            return arr

    return arr

def generate_all_paceline_rotation_sequences_in_the_total_solution_space(length_of_paceline: int,
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

def generate_all_suitable_paceline_rotation_sequences_in_the_solution_space(
    paceline_ingredients: PacelineIngredientsItem
) -> NDArray[np.float64]:
    """
    Generate all valid paceline pull period sequences as a NumPy array, enforcing a non-increasing
    constraint on successive pull periods, with riders ordered by decreasing 1-minute strength.

    This function constructs all possible assignments of pull periods to a paceline, where each rider
    is assigned a pull period from the allowed set. Only those combinations are included where no
    successive pull period is longer than the previous one (i.e., the sequence is non-increasing).
    The rider list is reordered by 1-minute strength (strongest to weakest) to ensure the mapping
    between pull periods and rider strength is correct.

    Args:
        paceline_ingredients (PacelineIngredientsItem): 
            An object containing:
                - riders_list: List of RiderComputeItem, the riders in the paceline.
                - sequence_of_pull_periods_sec: List[float], allowed pull durations (in seconds).

    Returns:
        NDArray[np.float64]: 2D NumPy array of valid paceline pull period sequences.
            Each row is a sequence of pull periods (length = number of riders), satisfying the
            non-increasing constraint and mapped to the ordered rider list.

    Notes:
        - The function ensures that the mapping between pull periods and riders is consistent,
          even if the input rider list is not ordered by strength.
        - Returns an empty array if input lists are empty or if no valid combinations exist.
    """
    length_of_paceline = len(paceline_ingredients.riders_list)
    standard_pull_periods_seconds = paceline_ingredients.sequence_of_pull_periods_sec # this is the normally standard sequence, but modifiable by the user

    # Error handling: Check for empty lists
    if (
        length_of_paceline == 0 or
        not standard_pull_periods_seconds or
        len(standard_pull_periods_seconds) == 0
    ):
        return np.empty((0, length_of_paceline), dtype=np.float64)

    # Error handling: fn to check for non-unique riders
    def has_duplicates(riders_list: list[RiderComputeItem]) -> bool:
        return len(riders_list) != len(set(id(r) for r in riders_list))

    if has_duplicates(paceline_ingredients.riders_list):
        raise ValueError("Duplicate riders found in paceline_ingredients.riders_list. Please eliminate the duplicates and try again.")

    # Generate all valid combinations of pull period sequences (non-increasing sequences)
    all_combinations: List[List[float]] = [[]]
    for _ in range(length_of_paceline):
        next_combinations: List[List[float]] = []
        for seq in all_combinations:
            for period in standard_pull_periods_seconds:
                if seq and period > seq[-1]:
                    continue # enforce non-increasing constraint
                candidate = seq + [period]
                next_combinations.append(candidate)
        all_combinations = next_combinations

    # Only keep fully-formed combinations
    valid_combinations = [seq for seq in all_combinations if len(seq) == length_of_paceline]

    # Error handling: Check for empty valid_combinations
    if not valid_combinations:
        return np.empty((0, length_of_paceline), dtype=np.float64)

    # Prepare rider lists
    riders_list = paceline_ingredients.riders_list
    ordered_rider_list = arrange_riders_by_1_minute_strength(riders_list) # order by strength decreasing i.e. non-increasing pull-periods

    # Error handling: Check for inconsistent sequence lengths
    expected_length = len(ordered_rider_list)
    for i, seq in enumerate(valid_combinations):
        if len(seq) != expected_length:
            raise ValueError(
                f"Sequence at index {i} in valid_combinations has length {len(seq)}, "
                f"but expected {expected_length} (matches number of riders)."
            )

    # Error handling: Check for NaN or Inf in valid_combinations
    arr_valid_combinations = np.array(valid_combinations, dtype=np.float64)
    if np.isnan(arr_valid_combinations).any() or np.isinf(arr_valid_combinations).any():
        raise ValueError("NaN or infinite value found in valid_combinations.")

    # If the order is already the same, return as is (no-op)
    is_same_order = all(
        a is b for a, b in zip(ordered_rider_list, riders_list)
    )
    if is_same_order:
        return arr_valid_combinations
    # Build index map for reordering
    try:
        index_map = [ordered_rider_list.index(rider) for rider in riders_list]
    except ValueError as e:
        raise ValueError(
            "A rider in paceline_ingredients.riders_list was not found in ordered_rider_list."
        ) from e
    # Reorder each sequence
    reordered_combinations = [
        [seq[idx] for idx in index_map] for seq in arr_valid_combinations
    ]
    return np.array(reordered_combinations, dtype=np.float64)

