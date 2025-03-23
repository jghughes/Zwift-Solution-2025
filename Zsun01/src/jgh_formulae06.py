from typing import  List
from jgh_formulae05 import RiderEffortItem

def calculate_weighted_average_watts(efforts: List[RiderEffortItem]) -> float:
    """
    Calculate the average power for a list of efforts.
    The average power is calculated as the total work done (in kilojoules) divided by 
    the total duration (in seconds). The function sums the kilojoules for each workload 
    item and divides by the total duration to obtain the average power.

    Args:
        efforts (List[RiderEffortItem]): The list of efforts.
    Returns:
        float: The average power.
    """
    if not efforts:
        return 0

    total_kilojoules = sum(item.kilojoules for item in efforts)
    total_duration = sum(item.duration for item in efforts)
    average_watts = 1_000 * total_kilojoules / total_duration if total_duration != 0 else 0
    return average_watts

def calculate_smoothed_numbers(numbers: List[float], window_size: int) -> List[float]:
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
        >>> calculate_smoothed_numbers(numbers, window_size)
        [2.0, 3.0, 4.0]

    In this example, the rolling average is calculated for a window size of 3. 
    The first value in the returned list is the average of the first three numbers 
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

def calculate_normalized_watts(efforts: List[RiderEffortItem]) -> float:
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
        efforts (List[RiderEffortItem]): The list of efforts. 
        Each item contains the wattage and duration for a specific segment of the 
        workout.

    Returns:
        float: The normalized power.

    Example:
        >>> efforts = [
        ...     RiderEffortItem(position=1, speed=35, duration=60, wattage=200, wattage_ftp_ratio=0.8, kilojoules=12000),
        ...     RiderEffortItem(position=2, speed=30, duration=30, wattage=180, wattage_ftp_ratio=0.72, kilojoules=5400)
        ... ]
        >>> calculate_normalized_watts(efforts)
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
    # Our pulls are 30, 60, and 90 seconds long, so we'll use a (arbitrary) 10-second rolling average
    rolling_avg_power = calculate_smoothed_numbers(instantaneous_wattages, 10)

    # Raise the smoothed power values to the fourth power
    rolling_avg_power_4 = [p ** 4 for p in rolling_avg_power]

    # Calculate the average of these values
    mean_power_4 = sum(rolling_avg_power_4) / len(rolling_avg_power_4)

    # Take the fourth root of the average
    normalized_watts = mean_power_4 ** 0.25

    return normalized_watts


# Example usage 
def main() -> None:
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from typing import Dict, cast
    from jgh_read_write import read_text
    from jgh_serialization import JghSerialization
    from zwiftrider_item import ZwiftRiderItem
    from zwiftrider_dto import ZwiftRiderDataTransferObject
    from tabulate import tabulate
    from jgh_formulae04 import compose_map_of_rider_work_assignments
    from jgh_formulae05 import populate_map_of_rider_efforts

    # Load rider data from JSON
    inputjson = read_text("C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/", "rider_dictionary.json")
    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    # for the benfit of type inference: explicitly cast the return value of the serialisation to expected generic Type
    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto)

    #transform to ZwiftRiderItem dict
    dict_of_zwiftrideritem = ZwiftRiderItem.from_dataTransferObject_dict(dict_of_zwiftrider_dto)

    # Instantiate ZwiftRiderItem objects for barryb, johnh, and lynseys
    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    # Create a list of the selected riders
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    # Example riders and pull durations
    pull_durations = [90.0, 60.0, 30.0]
    pull_speeds = [40.0, 40.0, 40.0]
    # Compose the rider work_assignments
    work_assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)

    # Calculate rider efforts
    rider_efforts = populate_map_of_rider_efforts(work_assignments)

    # Calculate and compare weighted average power and normalized power for each rider
    table = []
    for rider, items in rider_efforts.items():
        weighted_avg_watts = calculate_weighted_average_watts(items)
        normalized_watts = calculate_normalized_watts(items)
        table.append([rider.name, weighted_avg_watts, normalized_watts])

    headers = ["Rider", "Weighted Average watts", "Normalized watts"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


if __name__ == "__main__":
    main()
