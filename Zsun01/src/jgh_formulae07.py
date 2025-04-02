from typing import  List, Dict, Tuple
from zwiftrider_related_items import ZwiftRiderItem, RiderExertionItem, RiderAnswerItem, RiderAnswerDisplayObject
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

def populate_rider_answer_dispayobjects(riders: Dict[ZwiftRiderItem, RiderAnswerItem]) -> Dict[ZwiftRiderItem, RiderAnswerDisplayObject]:

    answer: Dict[ZwiftRiderItem, RiderAnswerDisplayObject] = {}

    def calculate_zwift_zrs_cat(rider: ZwiftRiderItem) -> str:
        if rider.zwift_racing_score < 180:
            return "E"
        elif rider.zwift_racing_score < 350:
            return "D"
        elif rider.zwift_racing_score < 520:
            return "C"
        elif rider.zwift_racing_score < 690:
            return "B"
        else:
            return "A"

    def calculate_zwift_ftp_cat(rider: ZwiftRiderItem)-> str:

        wkg = rider.ftp/rider.weight if rider.weight != 0 else 0

        if wkg < 2.5:
            return "D"
        elif wkg < 3.2:
            return "C"
        elif wkg < 4.0:
            return "B"
        else:
            return "A"

    def calculate_wkg(watts: float, weight : float)-> float:
        return rider.ftp/rider.weight if rider.weight != 0 else 0

    def make_pretty_velo_cat(rider: ZwiftRiderItem) -> str:

        def calculate_velo_cat(rider: ZwiftRiderItem) -> Tuple[int, str]:
            if rider.gender == "f":
                if rider.velo_rating >= 1450:
                    return 1, "Diamond"
                elif rider.velo_rating >= 1250:
                    return 2, "Ruby"
                elif rider.velo_rating >= 1100:
                    return 3, "Emerald"
                elif rider.velo_rating >= 950:
                    return 4, "Sapphire"
                elif rider.velo_rating >= 850:
                    return 5, "Amethyst"
                elif rider.velo_rating >= 750:
                    return 6, "Platinum"
                elif rider.velo_rating >= 650:
                    return 7, "Gold"
                elif rider.velo_rating >= 550:
                    return 8, "Silver"
                elif rider.velo_rating >= 400:
                    return 9, "Bronze"
                else:
                    return 10, "Copper"
            else:
                if rider.velo_rating >= 2200:
                    return 1, "Diamond"
                elif rider.velo_rating >= 1900:
                    return 2, "Ruby"
                elif rider.velo_rating >= 1650:
                    return 3, "Emerald"
                elif rider.velo_rating >= 1450:
                    return 4, "Sapphire"
                elif rider.velo_rating >= 1300:
                    return 5, "Amethyst"
                elif rider.velo_rating >= 1150:
                    return 6, "Platinum"
                elif rider.velo_rating >= 1000:
                    return 7, "Gold"
                elif rider.velo_rating >= 850:
                    return 8, "Silver"
                elif rider.velo_rating >= 650:
                    return 9, "Bronze"
                else:
                    return 10, "Copper"

        velo_rank, velo_name = calculate_velo_cat(rider)
        return f"{velo_rank}-{velo_name}"

    def make_pretty_cat_descriptor(rider: ZwiftRiderItem) -> str:
        answer = f"{rider.zwift_racing_score} {round(calculate_wkg(rider.ftp, rider.weight), 2)} {calculate_zwift_ftp_cat(rider)} {make_pretty_velo_cat(rider)}"
        # answer = f"zrs={rider.zwift_racing_score} ftp={round(calculate_wkg(rider.ftp, rider.weight), 2)} cat={calculate_zwift_ftp_cat(rider)} cat={make_pretty_velo_cat(rider)}"
        # answer = f"{rider.zwift_racing_score}({calculate_zwift_zrs_cat(rider)}) {round(calculate_wkg(rider.ftp, rider.weight), 1)}({calculate_zwift_ftp_cat(rider)}) {make_pretty_velo_cat(rider)}"
        return answer

    def make_pretty_p1_p4(answer: RiderAnswerItem) -> str:
        return f"{round(answer.p1_w)} {round(answer.p2_w)} {round(answer.p3_w)} {round(answer.p4_w)}"

    for rider, item in riders.items():
        rider_display_object = RiderAnswerDisplayObject(
            name                  = rider.name,
            pretty_cat_descriptor = make_pretty_cat_descriptor(rider),
            zrs_score             = rider.zwift_racing_score,
            zrs_cat               = calculate_zwift_zrs_cat(rider),
            zwiftftp_cat          = calculate_zwift_ftp_cat(rider),
            velo_cat              = make_pretty_velo_cat(rider),
            cp_5_min_wkg          = 0,
            cp                    = 0,
            ftp                   = rider.ftp,
            ftp_wkg               = round(calculate_wkg(rider.ftp, rider.weight),1),
            speed_kph             = round(item.speed_kph, 1),
            pull_duration          = item.pull_duration,
            pull_wkg               = round(calculate_wkg(item.p1_w, rider.weight), 1),
            pull_w_over_ftp        = f"{round(item.p1_w / rider.ftp*100 if rider.ftp != 0 else 0)}%",
            p1_4                  = make_pretty_p1_p4(item),
            ftp_intensity_factor  = round(item.ftp_intensity_factor, 2),
            cp_intensity_factor   = round(0, 2)
        )
        answer[rider] = rider_display_object

    return answer

def log_results_answer_displayobjects(test_description: str, result: Dict[ZwiftRiderItem, RiderAnswerDisplayObject], logger: logging.Logger) -> None:
    
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, z in result.items():
        table.append([
            z.name,
            z.pretty_cat_descriptor,
            # z.zrs_score, 
            # z.zrs_cat, 
            # z.zwiftftp_cat, 
            # z.velo_cat, 
            # z.ftp, 
            # z.ftp_wkg, 
            z.speed_kph,
            z.pull_duration, 
            z.pull_wkg, 
            z.p1_4, 
            z.pull_w_over_ftp, 
            z.ftp_intensity_factor, 
            z.cp_intensity_factor,
            z.cp_5_min_wkg, 
            z.cp, 

        ])

    headers = ["Rider",
        "Categories",
        # "ZRS", 
        # "ZRS Cat", 
        # "FTP Cat", 
        # "Velo Cat", 
        # "FTP", 
        # "FTP w/kg",
        "kph", 
        "pull(s)", 
        "w/kg", 
        "P1-4", 
        "ftp(%)", 
        "IF(ftp)", 
        "IF(cp)",
        "CP 5 min", 
        "CP" 
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae06 import populate_rider_answeritems

    from handy_utilities import get_all_zwiftriders, get_all_zwiftriders_cp_data


    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    pull_speeds_kph = [42.0, 42.0, 42.0]
    pull_durations_sec = [30.0, 30.0, 30.0]
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    work_assignments = populate_rider_work_assignments(riders, pull_durations_sec, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    rider_answer_displayobjects = populate_rider_answer_dispayobjects(rider_answer_items)

    log_results_answer_displayobjects("Rider print-out:", rider_answer_displayobjects, logger)

    dict_of_zwiftrider_cp_item = get_all_zwiftriders_cp_data()

    johnh_cp : ZwiftRiderCriticalPowerItem = dict_of_zwiftrider_cp_item['johnh']
    joshn_cp : ZwiftRiderCriticalPowerItem = dict_of_zwiftrider_cp_item['joshn']


if __name__ == "__main__":
    main()
