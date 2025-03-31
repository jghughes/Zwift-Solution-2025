from typing import  List, Dict
from handy_utilities import get_all_zwiftriders
from zwiftrider_related_items import ZwiftRiderItem, RiderExertionItem, RiderAnswerDisplayObject
from jgh_formulae05 import calculate_average_watts, calculate_normalized_watts
import logging

def calculate_zwift_zrs_cat(rider: ZwiftRiderItem)-> str:

    if rider.zwift_racing_score < 1.0:
        return "D"
    elif rider.zwift_racing_score < 2.0:
        return "C"
    elif rider.zwift_racing_score < 3.0:
        return "B"
    elif rider.zwift_racing_score < 4.0:
        return "A"
    else:
        return "A+"

def calculate_zwift_ftp_cat(rider: ZwiftRiderItem)-> str:
    if rider.ftp < 2.0:
        return "D"
    elif rider.ftp < 3.2:
        return "C"
    elif rider.ftp < 4.0:
        return "B"
    elif rider.ftp < 5.0:
        return "A"
    else:
        return "A+"

def calculate_velo_cat(rider: ZwiftRiderItem)-> int:
    if rider.ftp < 2.0:
        return "5"
    elif rider.ftp < 3.2:
        return "4"
    elif rider.ftp < 4.0:
        return "3"
    elif rider.ftp < 5.0:
        return "2"
    else:
        return "1"

def calculate_ftp_wkg(rider: ZwiftRiderItem)-> float:
    return round(rider.ftp/rider.weight,2)

def calculate_cp_intensity_factor(rider: ZwiftRiderItem, items: List[RiderExertionItem]) -> float:
    pass

def calculate_ftp_intensity_factor(rider: ZwiftRiderItem, items: List[RiderExertionItem]) -> float:
    if not items:
        return 0
    if rider.ftp == 0:
        return 0
    ftp_intensity_factor = round(calculate_normalized_watts(items)/rider.ftp,2)
    return ftp_intensity_factor


def populate_rider_display_objects(riders: Dict[ZwiftRiderItem, List[RiderExertionItem]]) -> Dict[ZwiftRiderItem, RiderAnswerDisplayObject]:

    answer: Dict[ZwiftRiderItem, RiderAnswerDisplayObject] = {}

    for rider, items in riders.items():









        rider_display_object = RiderAnswerDisplayObject(
            name = rider.name,
            zrs = rider.zwift_racing_score,
            zwiftftp_cat = calculate_zwift_ftp_cat(rider),
            velo_cat = calculate_velo_cat(rider),
            cp_5_min_wkg = 0,
            cp  = 0,
            ftp = rider.ftp,
            ftp_wkg  = calculate_ftp_wkg(rider),
            p1_duration = 0,
            p1_wkg = 0,
            p1_div_ftp = 0,
            p1_w = 0,
            p2_w = 0,
            p3_w = 0,
            p4_w = 0,
            ftp_intensity_factor = calculate_ftp_intensity_factor(rider, items),
            cp_intensity_factor = calculate_cp_intensity_factor(rider, items)
        )
        answer[rider] = rider_display_object

    return answer


def log_results(test_description: str, result: Dict[ZwiftRiderItem, List[RiderExertionItem]], logger: logging.Logger) -> None:
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, items in result.items():
        avg_watts = calculate_average_watts(items)
        normalized_watts = calculate_normalized_watts(items)
        table.append([rider.name, rider.ftp, round(avg_watts), round(normalized_watts), round(normalized_watts/rider.ftp,2)])

    headers = ["Rider", "FTP (w)", "Average (w)", "NP (w)", "Intensity factor"]
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

    pull_speeds_kph = [42.0, 42.0, 42.0]
    pull_durations_sec = [30.0, 30.0, 30.0]
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    work_assignments = populate_rider_work_assignments(riders, pull_durations_sec, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    log_results("Comparative rider wattage metrics based on single loop of the paceline (this is as far as the TTT Calculator goes I suspect):", rider_exertions, logger)


if __name__ == "__main__":
    main()
