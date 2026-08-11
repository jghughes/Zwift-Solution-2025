
from typing import Dict, List, Tuple

import numpy as np
from numpy.typing import NDArray
from jgh_number import safe_divide


from paceline_modelling_items import PacelineIngredientsItem, RiderContributionItem, RiderExertionItem
from constants import ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL, AERO_POSITION_FACTOR_DEFAULT, POWER_CURVE_IN_PACELINE
from jgh_formatting import truncate
from jgh_formulae01 import calculate_rider_kph_from_watts, calculate_rider_watts_from_kph
from jgh_formulae02 import solve_for_speed_at_standard_30sec_pull_watts, solve_for_speed_at_standard_1_minute_pull_watts, solve_for_speed_at_standard_2_minute_pull_watts, solve_for_speed_at_standard_3_minute_pull_watts, solve_for_speed_at_standard_4_minute_pull_watts, solve_for_speed_at_one_hour_watts
# from jgh_power_curve_fit_models import decay_model_numpy
# from jgh_rolling_average import calculate_rolling_averages
from rider_compute_item import RiderComputeItem

# All of these functions are called during parallel processing. Logging forbidden

def calculate_drag_ratio_in_paceline(position_in_paceline: int) -> float:
    """
    Calculate the power factor based on the rider's position 
    in the paceline. The leader's factor is 1.0. Followers in 
    the paceline are based on ZwiftInsider's power matrix. 
    Their factors are less than 1.0, diminishing as they are 
    further back.This function guards against index out of 
    range errors if POWER_CURVE_IN_PACELINE is shorter than 8.
    """
    denominator = POWER_CURVE_IN_PACELINE[0]
    max_index = len(POWER_CURVE_IN_PACELINE) - 1
    # Clamp position to valid range (1 to len(POWER_CURVE_IN_PACELINE)), else use last available value
    if 1 <= position_in_paceline <= len(POWER_CURVE_IN_PACELINE):
        numerator = POWER_CURVE_IN_PACELINE[position_in_paceline - 1]
    else:
        numerator = POWER_CURVE_IN_PACELINE[max_index]  # Use last available value
    return numerator / denominator

def calculate_power_riding_in_the_paceline(rider : RiderComputeItem, speed: float, position: int, slope_pc: float = 0.0) -> float:
    """
    Calculate required wattage (watts) for a rider at given speed
    (km/h), position, slope (%), weight (kg), and height (cm) in the
    paceline.
    """
    base_power = calculate_rider_watts_from_kph(speed, rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
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
    speed_kph = calculate_rider_kph_from_watts(adjusted_watts, rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
        
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

def calculate_rolling_averages(numbers: List[float], window_size: int) -> List[float]:
    """
    Calculate the rolling average of the given numbers with the specified window size.

    This function computes the rolling average for a list of numbers using a 
    specified window size. The window size determines the number of consecutive 
    numbers to include in each average calculation. We assume that the length of 
    the input list `numbers` is small, potentially as small as three items. Given 
    this assumption, the function is implemented in a straightforward manner 
    without complex optimizations.

    Args:
        numbers (List[float]): The list of numbers for which the rolling average 
        is to be calculated.
        window_size (int): The size of the rolling window, i.e., the number of 
        consecutive numbers to include in each average calculation.

    Returns:
        List[float]: The list of rolling average numbers. Each value in the 
        returned list represents the average of a subset of the input numbers, 
        with the subset size determined by the window size. The length of the 
        returned list will be `len(numbers) - window_size + 1`.

    Example:
        >>> numbers = [1, 2, 3, 4, 5]
        >>> window_size = 3
        >>> calculate_rolling_averages(numbers, window_size)
        [2.0, 3.0, 4.0]

    In this example, the rolling average is calculated for a window size of 3. 
    The first_name value in the returned list is the average of the first_name three numbers 
    in the input list (1, 2, 3), the second value is the average of the next 
    three numbers (2, 3, 4), and so on.

    Handling small input lists:
    - If the length of `numbers` is less than the `window_size`, the function will 
    return an empty list.
    - The function iterates over the input list and calculates the average for 
    each window of the specified size.
    """
    if not numbers or window_size <= 0:
        return []

    rolling_averages: List[float] = []
    for i in range(len(numbers) - window_size + 1):
        window = numbers[i:i + window_size]
        rolling_averages.append(sum(window) / window_size)

    return rolling_averages

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

def solve_for_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> float:
    return 1.0  # arbitrarily small 1 kph to ensure the binary search algorithm starts at a safe lower bound speed.

def calculate_overall_intensity_factor_of_rider_contribution(rider: RiderComputeItem, rider_contribution: RiderContributionItem) -> float:
    """
    Calculate intensity factor as the ratio of normalized watts to
    one-hour power (FTP).
    """
    return  safe_divide(rider_contribution.normalized_watts, rider.get_1_hour_curvefit_watts())

def solve_for_proxy_standard_30sec_pull_speed_for_all_riders(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> Dict[RiderComputeItem, float]:
    speeds: Dict[RiderComputeItem, float] = {}
    for rider in riders:
        speeds[rider] = solve_for_speed_at_standard_30sec_pull_watts(rider, slope_pc)
    return speeds

def solve_for_speed_at_one_hour_watts_for_all_riders(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> Dict[RiderComputeItem, float]:
    speeds: Dict[RiderComputeItem, float] = {}
    for rider in riders:
        speeds[rider] = solve_for_speed_at_one_hour_watts(rider, slope_pc)
    return speeds

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

def order_paceline_by_desired_order_of_riders(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    """
    Reorder the list of riders to match the desired order.
    """
    return _arrange_riders_by_zwiftracingapp_zpFTP_strength(riders=riders)

def _arrange_riders_by_zwiftracingapp_zpFTP_strength(riders: List[RiderComputeItem]) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.get_zwiftracingapp_zpFTP_wkg(), reverse=True)
    return sorted_riders

def _arrange_riders_by_1_minute_strength(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> List[RiderComputeItem]:
    sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_1_minute_wkg(), reverse=True)
    # sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_1_minute_pull_kph(slope_pc), reverse=True)
    return sorted_riders

def _arrange_riders_by_1_minute_strength_interleaved(riders: List[RiderComputeItem], slope_pc: float = 0.0) -> List[RiderComputeItem]:
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
    # sorted_riders = sorted(riders, key=lambda rider: rider.get_proxy_1_minute_pull_kph(slope_pc), reverse=True)

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

def select_n_riders_at_the_top_of_the_list(riders: List[RiderComputeItem], n : int) -> List[RiderComputeItem]:
    if not riders:
        return []

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
    Efficiently prunes a large set of paceline pull pull_duration sequences (pull pull_duration assignments) using empirical rules
    based on rider strength, to reduce the solution space for further computation.

    This function applies two main filters:
      1. No rider (except the second weakest) can have a pull pull_duration shorter than the weakest rider's pull pull_duration.
      2. For n in 1..12 (or up to the number of riders), no rider (except the top n-1 strongest) can have a pull
         pull_duration longer than the nth strongest rider's pull pull_duration.

    Filtering stops as soon as the number of remaining pull pull_duration sequences drops below the configured solution space constraint.

    Args:
        pull_period_sequences_being_pruned (NDArray[np.float_]):
            2D NumPy array of extended_seq paceline pull pull_duration sequences, where each row is a sequence of pull periods (seconds)
            for each rider.
        riders (List[RiderComputeItem]):
            List of rider objects, used to determine rider strength order for filtering.

    Returns:
        NDArray[np.float_]:
            The filtered 2D NumPy array of paceline pull pull_duration sequences, reduced according to empirical rules.

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
    for reorder_index in range(arr.shape[1]):
        if reorder_index == second_weakest_idx:
            continue
        mask &= arr[:, reorder_index] >= weakest_values[:, 0]
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
        for reorder_index in range(arr.shape[1]):
            if reorder_index in indices[:-1]:
                continue
            mask &= arr[:, reorder_index] <= nth_values[:, 0]
        arr = arr[mask]
        if len(arr) < ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL:
            return arr

    return arr

def generate_all_paceline_rotation_sequences_in_the_total_solution_space(num_riders: int, list_of_allowable_pull_durations_sec: List[float]
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
        num_riders (int): Number of riders in the paceline.
        list_of_allowable_pull_durations_sec (List[float]): Allowed pull durations (in seconds).

    Returns:
        NDArray[np.float64]: All possible paceline pull pull_duration sequences as a 2D NumPy array.
    """
    # Create a meshgrid for all possible pull pull_duration assignments
    grids: tuple[NDArray[np.float64], ...] = np.meshgrid(*([list_of_allowable_pull_durations_sec] * num_riders), indexing='ij')
    # Stack and reshape to get all combinations as rows
    complete_sequences: NDArray[np.float64] = np.stack(grids, axis=-1).reshape(-1, num_riders)

    return complete_sequences

def generate_all_suitable_paceline_rotation_sequences_in_the_solution_space(paceline_ingredients: PacelineIngredientsItem) -> NDArray[np.float64]:
    """
    This function constructs a NumPy array of all possible permutations of assignments of pull periods to 
    each and every rider in a paceline. The matrix is populated such that each rider is ultimately assigned every pull from the allowed 
    set e.g. 30s, 60s, 120s etc. Basically we are generating a cross-product of all possible pull durations for all riders. 
    Only those combinations are included where no riders do stronger pulls than riders who are 
    stronger than them. To put it another way, for an ordered set of riders, the pull durations are non-increasing in order 
    of diminishing rider strength. For this purpose, the input rider list is temporarily ordered by 
    descending 1-minute strength (strongest to weakest) so that each rider does not exceed 
    the pull duration of the preceding rider in the list. The rider list is restored to 
    its original input order before the final output is returned.
    
    Args:
        paceline_ingredients (PacelineIngredientsItem): 
            An object containing:
                - riders_list: List of RiderComputeItem, the riders in the paceline.
                - sequence_of_pull_periods_sec: List[float], allowed pull durations (in seconds).

    Returns:
        NDArray[np.float64]: 2D NumPy array of valid paceline pull duration sequences.
            Each row is a sequence of pull periods (length = number of riders), satisfying the
            non-increasing constraint and mapped to the ordered rider list.

    Notes:
        - The function ensures that the mapping between pull periods and riders is consistent,
          even if the input rider list is not ordered by strength.
        - Returns an empty array if input lists are empty or if no valid combinations exist.
    """
    num_riders = len(paceline_ingredients.riders_list)
    list_of_available_pull_durations_sec = paceline_ingredients.sequence_of_pull_periods_sec # this is the normally standard sequence, but modifiable by the user

    # Error handling: Check for empty lists
    if (num_riders == 0 or not list_of_available_pull_durations_sec):
        return np.empty((0, num_riders), dtype=np.float64)

    # Error handling: fn to check for non-unique riders
    def has_duplicates(riders_list: list[RiderComputeItem]) -> bool:
        return len(riders_list) != len(set(id(rider) for rider in riders_list))

    if has_duplicates(paceline_ingredients.riders_list):
        raise ValueError("Duplicate riders found in paceline_ingredients.riders_list. Please eliminate the duplicates and try again.")

    # Build up the universe of all sets of pulls, only including non-increasing sequences. 
    # This is done by building up the sets one pull at a time, and  
    # adding pulls one by one that are less than or equal to the last pull in the growing set. 
    # This ensures that the final sequence of pulls in a set is non-increasing.
    list_of_sequences_of_pull_periods_being_built: List[List[float]] = [[]]
    for _ in range(num_riders):
        extended_sequences: List[List[float]] = []
        for single_sequence_of_pull_durations_being_built in list_of_sequences_of_pull_periods_being_built:
            for pull_duration in list_of_available_pull_durations_sec:
                if single_sequence_of_pull_durations_being_built and pull_duration > single_sequence_of_pull_durations_being_built[-1]:
                    continue # enforce non-increasing constraint
                extended_seq = single_sequence_of_pull_durations_being_built + [pull_duration]
                extended_sequences.append(extended_seq)
        list_of_sequences_of_pull_periods_being_built = extended_sequences

    # --- transition: all sequences are now fully formed ---
    list_of_sequences_of_pull_periods: List[List[float]] = list_of_sequences_of_pull_periods_being_built

    # Error handling: Check for empty sets
    if not list_of_sequences_of_pull_periods:
        return np.empty((0, num_riders), dtype=np.float64)

    # Prepare rider lists
    input_list_of_riders = paceline_ingredients.riders_list
    riders_strongest_first = order_paceline_by_desired_order_of_riders(input_list_of_riders)

    # Error handling: Check for NaN or Inf in complete_sequences
    array_of_sequences_of_pull_periods = np.array(list_of_sequences_of_pull_periods, dtype=np.float64)
    if np.isnan(array_of_sequences_of_pull_periods).any() or np.isinf(array_of_sequences_of_pull_periods).any():
        raise ValueError("NaN or infinite value found in array_of_sequences_of_pull_periods.")

    # If the order is already the same, return as is (no-op)
    riders_are_already_ordered_by_strength = all(
        ordered_rider is original_rider for ordered_rider, original_rider in zip(riders_strongest_first, input_list_of_riders)
    )
    if riders_are_already_ordered_by_strength:
        return array_of_sequences_of_pull_periods

    # Build index map for reordering
    try:
        reorder_indices = [riders_strongest_first.index(rider) for rider in input_list_of_riders]
    except ValueError as e:
        raise ValueError(
            "A rider in paceline_ingredients.riders_list was not found in riders_strongest_first."
        ) from e
    
    # For each sequence of pull durations, reorder the sequence to match the original input order of riders
    sequences_in_original_order = [[single_sequence_of_pull_periods[reorder_index] for reorder_index in reorder_indices] for single_sequence_of_pull_periods in array_of_sequences_of_pull_periods]
    return np.array(sequences_in_original_order, dtype=np.float64)

