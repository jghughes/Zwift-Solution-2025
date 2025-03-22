from typing import  List
from jgh_formulae05 import RiderWorkloadLineItem

def calculate_rolling_average(values: List[float], window_size: int) -> List[float]:
    """
    Calculate the rolling average of the given values with the specified window size.

    This function computes the rolling average for a list of values using a 
    specified window size. The window size determines the number of consecutive 
    values to include in each average calculation. We assume that the length of 
    the input list `values` is small, potentially as small as three items. Given 
    this assumption, the function is implemented in a straightforward manner 
    without complex optimizations.

    Args:
        values (List[float]): The list of values for which the rolling average 
        is to be calculated.
        window_size (int): The size of the rolling window, i.e., the number of 
        consecutive values to include in each average calculation.

    Returns:
        List[float]: The list of rolling average values. Each value in the 
        returned list represents the average of a subset of the input values, 
        with the subset size determined by the window size. The length of the 
        returned list will be `len(values) - window_size + 1`.

    Example:
        >>> values = [1, 2, 3, 4, 5]
        >>> window_size = 3
        >>> calculate_rolling_average(values, window_size)
        [2.0, 3.0, 4.0]

    In this example, the rolling average is calculated for a window size of 3. 
    The first value in the returned list is the average of the first three values 
    in the input list (1, 2, 3), the second value is the average of the next 
    three values (2, 3, 4), and so on.

    Handling small input lists:
    - If the length of `values` is less than the `window_size`, the function will 
    return an empty list.
    - The function iterates over the input list and calculates the average for 
    each window of the specified size.
    """
    if not values or window_size <= 0:
        return []

    rolling_averages: List[float] = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        rolling_averages.append(sum(window) / window_size)

    return rolling_averages


def calculate_normalized_power(workload_items: List[RiderWorkloadLineItem]) -> float:
    """
    Calculate the normalized power for a list of workload items.

    Normalized Power (NP) is a metric used to better quantify the physiological 
    demands of a workout compared to average power. It accounts for the variability 
    in power output and provides a more accurate representation of the effort 
    required. The calculation involves several steps:

    1. Create a list of instantaneous wattages for every second of the durations 
       of all workload items.
    2. Calculate the 30-second rolling average power.
    3. Raise the smoothed power values to the fourth power.
    4. Calculate the average of these values.
    5. Take the fourth root of the average.

    Args:
        workload_items (List[RiderWorkloadLineItem]): The list of workload items. 
        Each item contains the wattage and duration for a specific segment of the 
        workout.

    Returns:
        float: The normalized power.

    Example:
        >>> workload_items = [
        ...     RiderWorkloadLineItem(position=1, speed=35, duration=60, wattage=200, wattage_ftp_ratio=0.8, joules=12000),
        ...     RiderWorkloadLineItem(position=2, speed=30, duration=30, wattage=180, wattage_ftp_ratio=0.72, joules=5400)
        ... ]
        >>> calculate_normalized_power(workload_items)
        192.0

    In this example, the normalized power is calculated for two workload items. 
    The first item has a duration of 60 seconds and a wattage of 200, and the 
    second item has a duration of 30 seconds and a wattage of 180. The function 
    computes the normalized power based on these values.
    """
    if not workload_items:
        return 0

    # Create a list of instantaneous wattages for every second of the durations of all workload items
    instantaneous_wattages: List[float] = []
    for item in workload_items:
        instantaneous_wattages.extend([item.wattage] * int(item.duration))

    # Calculate the 30-second rolling average power
    rolling_avg_power = calculate_rolling_average(instantaneous_wattages, 30)

    # Raise the smoothed power values to the fourth power
    rolling_avg_power_4 = [p ** 4 for p in rolling_avg_power]

    # Calculate the average of these values
    mean_power_4 = sum(rolling_avg_power_4) / len(rolling_avg_power_4)

    # Take the fourth root of the average
    normalized_power = mean_power_4 ** 0.25

    return normalized_power