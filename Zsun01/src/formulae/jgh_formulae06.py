from typing import  List, Dict, Tuple
from zsun_rider_item import ZsunRiderItem
from computation_classes import *

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


def populate_rider_answeritems(riders: Dict[ZsunRiderItem, List[RiderExertionItem]]) -> Dict[ZsunRiderItem, RiderAnswerItem]:

    def extract_watts_sequentially(exertions: List[RiderExertionItem]) -> Tuple[float, float, float, float, float]:
        if not exertions:
            return 0, 0, 0, 0, 0

        dict_wattages = {exertion.current_location_in_paceline: exertion.wattage for exertion in exertions}

        p1 = dict_wattages.get(1, 0)
        p2 = dict_wattages.get(2, 0)
        p3 = dict_wattages.get(3, 0)
        p4 = dict_wattages.get(4, 0)
        px = p4 # for locations 5 and beyond ad infinitum, riders have same benefit as p4

        return p1, p2, p3, p4, px

    def extract_pull_metrics(exertions: List[RiderExertionItem]) -> Tuple[float, float, float, float]:
        if not exertions:
            return 0, 0, 0, 0

        p1_speed_kph = 0
        pull_duration : float = 0
        pull_wkg : float = 0
        pull_w_over_ftp : float= 0

        dict_positions = {exertion.current_location_in_paceline: exertion for exertion in exertions}

        pull_exertion = dict_positions.get(1, None)

        if pull_exertion is None:
            return 0, 0, 0, 0

        p1_speed_kph = pull_exertion.speed_kph
        pull_duration = pull_exertion.duration
        pull_wkg = pull_exertion.wattage / rider.weight if rider.weight != 0 else 0
        pull_w_over_ftp = pull_exertion.wattage / rider.ftp if rider.ftp != 0 else 0

        return p1_speed_kph, pull_duration, pull_wkg, pull_w_over_ftp
 
    def calculate_ftp_intensity_factor(rider: ZsunRiderItem, items: List[RiderExertionItem]) -> float:
        if not items:
            return 0
        if rider.ftp == 0:
            return 0
        ftp_intensity_factor = calculate_normalized_watts(items)/rider.ftp if rider.ftp != 0 else 0
        return ftp_intensity_factor

        answer: Dict[ZsunRiderItem, RiderAnswerItem] = {}

    answer : Dict[ZsunRiderItem, RiderAnswerItem] = {}

    for rider, exertions in riders.items():
        p1w, p2w, p3w, p4w, p__w = extract_watts_sequentially(exertions)
        p1_speed_kph, pull_duration, pull_wkg, pull_w_over_ftp = extract_pull_metrics(exertions)
        rider_answer_item = RiderAnswerItem(
            cp_watts  = 0,
            anaerobic_work_capacity= 0,
            speed_kph = p1_speed_kph,
            pull_duration = pull_duration,
            pull_wkg = pull_wkg,
            pull_w_over_ftp = pull_w_over_ftp,
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


def add_zwift_cp_and_w_prime_to_rider_answer_items(rider_answer_items: Dict[ZsunRiderItem, RiderAnswerItem], zwiftriders_zwift_cp_data: Dict[str, ZwiftPower90DayBestPowerItem]
) -> Dict[ZsunRiderItem, RiderAnswerItem]:
    """
    Populate zwift critical power and W' in the the rider answer items.
    Args:
        rider_answer_items (Dict[ZsunRiderItem, RiderAnswerItem]): The rider answer items.
        zwiftriders_zwift_cp_data (Dict[str, ZwiftPower90DayBestPowerItem]): The critical power items. Key is str(zwiftid).
    Returns:
        Dict[ZsunRiderItem, RiderAnswerItem]: The updated rider answer items with critical power and W'.
    """
    for rider, answer_item in rider_answer_items.items():
        rider_id_str = str(rider.zwiftid).strip()
        # logging.debug(f"Looking for rider ID: {rider_id_str} in zwiftriders_zwift_cp_data")
        rider_cp_item = zwiftriders_zwift_cp_data.get(rider_id_str, None) # because keyed on zwiftid
        if rider_cp_item:
            # logging.debug(f"Found rider ID: {rider_id_str}")
            answer_item.cp_watts = rider_cp_item.cp_watts
            answer_item.critical_power_w_prime= rider_cp_item.anaerobic_work_capacity
        else:
            logging.debug(f"Rider ID: {rider_id_str} not found in zwiftriders_zwift_cp_data")
    return rider_answer_items



def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from zsun_rider_item import ZsunRiderItem
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions

    def log_results_answer_items(test_description: str, result: Dict[ZsunRiderItem, RiderAnswerItem], logger: logging.Logger) -> None:
        from tabulate import tabulate
        logger.info(test_description)
        table = []
        for rider, z in result.items():
            table.append([
                rider.name, 
                z.speed_kph,
                z.pull_duration,
                round(z.pull_wkg,1),
                round(z.p1_w), 
                round(z.p2_w), 
                round(z.p3_w), 
                round(z.p4_w), 
                round(z.p__w),
                round(z.pull_w_over_ftp,1),
                round(z.ftp_intensity_factor,2), 
                round(z.cp_watts), 
                round(z.anaerobic_work_capacity/1_000)
            ])
        headers = ["rider", 
            "kph",
            "pull(s)", 
            "pull(wkg)",
            "p1(W)", 
            "p2(W)", 
            "p3(W)", 
            "p4(W)", 
            "p+(W)", 
            "pull(%ftp)",
            "IF(np/ftp)", 
            "critical_power(W)", 
            "awc(kJ)",
        ]
        logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))

    from handy_utilities import read_dict_of_zwiftriders

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zwiftriders(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    CPDATA_FILE_NAME = "betel_cp_data.json"

    zwiftriders_zwift_cp_data = read_dict_of_90day_best_cp_data(CPDATA_FILE_NAME,ZSUN01_PROJECT_DATA_DIRPATH)

    davek : ZsunRiderItem = dict_of_zwiftrideritem['3147366'] # davek
    barryb : ZsunRiderItem = dict_of_zwiftrideritem['5490373'] # barryb
    scottm : ZsunRiderItem = dict_of_zwiftrideritem['11526'] # markb
    johnh : ZsunRiderItem = dict_of_zwiftrideritem['1884456'] # johnh
    lynseys : ZsunRiderItem = dict_of_zwiftrideritem['383480'] # lynseys
    joshn : ZsunRiderItem = dict_of_zwiftrideritem['2508033'] # joshn
    richardm : ZsunRiderItem = dict_of_zwiftrideritem['1193'] # richardm
    
    pull_speeds_kph = [39.0, 39.0,39.0, 39.0, 39.0, 39.0, 39.0]
    pull_durations = [120.0, 90.0, 60.0, 30.0, 30.0, 30.0, 30.0]
    riders : list[ZsunRiderItem] = [davek, scottm, barryb, johnh, lynseys, joshn, richardm]

    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    rider_answer_items_with_cp_and_w_prime = add_zwift_cp_and_w_prime_to_rider_answer_items(rider_answer_items, zwiftriders_zwift_cp_data)

    log_results_answer_items("7-riders @40kph", rider_answer_items_with_cp_and_w_prime, logger)


if __name__ == "__main__":
    main()
