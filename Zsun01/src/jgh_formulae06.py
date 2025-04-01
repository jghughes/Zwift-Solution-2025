from typing import  List, Dict, Tuple
from handy_utilities import get_all_zwiftriders
from zwiftrider_related_items import ZwiftRiderItem, RiderExertionItem, RiderAnswerItem
from rolling_average import calculate_rolling_averages
import logging

# currenty unsused
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

def populate_rider_answeritems(riders: Dict[ZwiftRiderItem, List[RiderExertionItem]]) -> Dict[ZwiftRiderItem, RiderAnswerItem]:

    def extract_watts_sequentially(exertions: List[RiderExertionItem]) -> Tuple[float, float, float, float, float]:
        if not exertions:
            return 0, 0, 0, 0, 0

        dict_wattages = {exertion.current_location_in_paceline: exertion.wattage for exertion in exertions}

        p1 = dict_wattages.get(1, 0)
        p2 = dict_wattages.get(2, 0)
        p3 = dict_wattages.get(3, 0)
        p4 = dict_wattages.get(4, 0)
        p_ = p4 # for locations 5 and beyond ad infinitum, riders have same benefit as p4

        return p1, p2, p3, p4, p_

    def extract_pull_metrics(exertions: List[RiderExertionItem]) -> Tuple[float, float, float, float]:
        if not exertions:
            return 0, 0, 0, 0

        p1_speed_kph = 0
        p1_duration : float = 0
        p1_wkg : float = 0
        p1_slash_ftp : float= 0

        dict_positions = {exertion.current_location_in_paceline: exertion for exertion in exertions}

        pull_exertion = dict_positions.get(1, None)

        if pull_exertion is None:
            return 0, 0, 0, 0

        p1_speed_kph = pull_exertion.speed_kph
        p1_duration = pull_exertion.duration
        p1_wkg = pull_exertion.wattage / rider.weight if rider.weight != 0 else 0
        p1_slash_ftp = pull_exertion.wattage / rider.ftp if rider.ftp != 0 else 0

        return p1_speed_kph, p1_duration, p1_wkg, p1_slash_ftp
 
    def calculate_ftp_intensity_factor(rider: ZwiftRiderItem, items: List[RiderExertionItem]) -> float:
        if not items:
            return 0
        if rider.ftp == 0:
            return 0
        ftp_intensity_factor = calculate_normalized_watts(items)/rider.ftp if rider.ftp != 0 else 0
        return ftp_intensity_factor

        answer: Dict[ZwiftRiderItem, RiderAnswerItem] = {}

    answer : Dict[ZwiftRiderItem, RiderAnswerItem] = {}

    for rider, exertions in riders.items():
        p1w, p2w, p3w, p4w, p__w = extract_watts_sequentially(exertions)
        p1_speed_kph, p1_duration, p1_wkg, p1_slash_ftp = extract_pull_metrics(exertions)
        rider_answer_item = RiderAnswerItem(
            cp  = 0,
            w_prime= 0,
            speed_kph = p1_speed_kph,
            p1_duration = p1_duration,
            p1_wkg = p1_wkg,
            p1_slash_ftp = p1_slash_ftp,
            p1_w = p1w,
            p2_w = p2w,
            p3_w = p3w,
            p4_w = p4w,
            p__w = p__w,
            ftp_intensity_factor = calculate_ftp_intensity_factor(rider, exertions),
            cp_intensity_factor = 0
        )
        answer[rider] = rider_answer_item

    return answer

def log_results_answer_items(test_description: str, result: Dict[ZwiftRiderItem, RiderAnswerItem], logger: logging.Logger) -> None:
    from tabulate import tabulate
    logger.info(test_description)
    table = []
    for rider, z in result.items():
        table.append([
            rider.name, 
            z.speed_kph,
            z.p1_duration,
            z.p1_wkg,
            z.p1_w, 
            z.p2_w, 
            z.p3_w, 
            z.p4_w, 
            z.p__w,
            z.cp, 
            z.w_prime,
            z.p1_slash_ftp,
            z.ftp_intensity_factor, 
            z.cp_intensity_factor
        ])
    headers = [
        "rider", 
        "speed"
        "pull(s)", 
        "pull(wkg)",
        "p1", 
        "p2", 
        "p3", 
        "p4", 
        "p+", 
        "cp", 
        "W_prime",
        "pull(%ftp)",
        "IF(ftp)", 
        "IF(cp)"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from zwiftrider_related_items import ZwiftRiderItem
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']
    joshn : ZwiftRiderItem = dict_of_zwiftrideritem['joshn']
    richardm : ZwiftRiderItem = dict_of_zwiftrideritem['richardm']

    pull_speeds_kph = [42.0, 42.0, 42.0, 42.0, 42.0]
    pull_durations_sec = [30.0, 30.0, 30.0, 30.0, 30.0]
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys, joshn, richardm]

    work_assignments = populate_rider_work_assignments(riders, pull_durations_sec, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    log_results_answer_items("Comparative rider wattage metrics based on single loop of the paceline (as far as the TTT Calculator goes) [RiderAnswerItem]:", rider_answer_items, logger)

if __name__ == "__main__":
    main()
