from typing import Dict, List
from zsun_rider_item import ZsunRiderItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
from computation_classes import *

def populate_rider_exertions(rider_work_assignments: Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]]) -> Dict[ZsunRiderItem, List[RiderExertionItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the paceline.
        rider_work_assignments (Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]): The dictionary of rider workunits.

    Returns:
        Dict[ZsunRiderItem, List[RiderExertionItem]]: A dictionary of Zwift riders with
            their list of respective efforts including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of rider_exertions
    """
    rider_workloads: Dict[ZsunRiderItem, List[RiderExertionItem]] = {}
    
    for rider, work_assignments in rider_work_assignments.items():
        rider_exertions: List[RiderExertionItem] = []
        for assignment in work_assignments:
            wattage = rider.calculate_wattage_riding_in_the_peloton(assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            rider_exertions.append(RiderExertionItem(current_location_in_paceline=assignment.position, speed_kph=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_exertions
    
    return rider_workloads


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import populate_rider_work_assignments

    def log_results_exertions(test_description: str, result: Dict[ZsunRiderItem, List[RiderExertionItem]], logger: logging.Logger) -> None:
        from tabulate import tabulate
        logger.info(test_description)
        table = []
        for rider, efforts in result.items():
            for effort in efforts:
                table.append([
                    rider.name, 
                    effort.current_location_in_paceline, 
                    round(effort.speed_kph, 1), 
                    round(effort.duration), 
                    round(effort.wattage, 0), 
                    round(effort.kilojoules, 0)
                ])

        headers = [
            "rider", 
            "location", 
            "kph", 
            "seconds)", 
            "watts", 
            "kJ"
        ]
        logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

    from handy_utilities import read_dict_of_zsunriderItems

    RIDERDATA_FILE_NAME = "betel_ZsunRiderItems.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zsunriderItems(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    davek : ZsunRiderItem = dict_of_zwiftrideritem['3147366'] # davek
    barryb : ZsunRiderItem = dict_of_zwiftrideritem['5490373'] # barryb
    johnh : ZsunRiderItem = dict_of_zwiftrideritem['1884456'] # johnh
    lynseys : ZsunRiderItem = dict_of_zwiftrideritem['383480'] # lynseys
    joshn : ZsunRiderItem = dict_of_zwiftrideritem['2508033'] # joshn
    richardm : ZsunRiderItem = dict_of_zwiftrideritem['1193'] # richardm

    pull_speeds_kph = [40.0, 40.0, 40.0, 40.0, 40.0, 40.0]
    pull_durations = [120.0, 120.0, 60.0, 30.0, 30.0, 30.0]
    riders : list[ZsunRiderItem] = [davek, barryb, johnh, lynseys, joshn, richardm]

    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    log_results_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

if __name__ == "__main__":
    main()

