from typing import Dict, List
from zwiftrider_related_items import ZwiftRiderItem, RiderExertionItem, RiderWorkAssignmentItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
from rolling_average import calculate_rolling_averages
import logging


def populate_rider_exertions(rider_work_assignments: Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]]) -> Dict[ZwiftRiderItem, List[RiderExertionItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the paceline.
        rider_work_assignments (Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]): The dictionary of rider workunits.

    Returns:
        Dict[ZwiftRiderItem, List[RiderExertionItem]]: A dictionary of Zwift riders with
            their list of respective efforts including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of rider_exertions
    """
    rider_workloads: Dict[ZwiftRiderItem, List[RiderExertionItem]] = {}
    
    for rider, work_assignments in rider_work_assignments.items():
        rider_exertions: List[RiderExertionItem] = []
        for assignment in work_assignments:
            wattage = rider.calculate_wattage_riding_in_the_peloton(assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            rider_exertions.append(RiderExertionItem(position=assignment.position, speed=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_exertions
    
    return rider_workloads

def calculate_average_watts(efforts: List[RiderExertionItem]) -> float:
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
    average_watts = 1_000 * total_kilojoules / total_duration if total_duration != 0 else 0
    return average_watts


def calculate_normalized_watts(efforts: List[RiderExertionItem]) -> float:
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
    # Our pulls are 30, 60, and 90 seconds long, so we'll use a (arbitrary) 5-second rolling average
    rolling_avg_power = calculate_rolling_averages(instantaneous_wattages, 5)

    # Raise the smoothed power values to the fourth power
    rolling_avg_power_4 = [p ** 4 for p in rolling_avg_power]

    # Calculate the average of these values
    mean_power_4 = sum(rolling_avg_power_4) / len(rolling_avg_power_4)

    # Take the fourth root of the average
    normalized_watts = mean_power_4 ** 0.25

    return normalized_watts


def log_results(test_description: str, result: Dict[ZwiftRiderItem, List[RiderExertionItem]], logger: logging.Logger) -> None:
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []

    for rider, efforts in result.items():
        for effort in efforts:
            table.append([rider.name, effort.position, round(effort.speed, 1), round(effort.duration), round(effort.wattage,0), round(effort.kilojoules, 0)])

    headers = ["Rider", "Position", "Speed", "Duration of effort", "Wattage", "kJ expended"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import populate_rider_work_assignments
    from handy_utilities import get_all_zwiftriders

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    pull_speeds_kph = [40.0, 38.0, 36.0]
    pull_durations_sec = [60.0, 30.0, 10.0]
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    work_assignments = populate_rider_work_assignments(riders, pull_durations_sec, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    log_results("Calculated rider watts and kJ:", rider_exertions, logger)


if __name__ == "__main__":
    main()

