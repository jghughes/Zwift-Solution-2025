from typing import List, DefaultDict
from collections import defaultdict
from zsun_rider_item import ZsunItem
from jgh_formulae01 import estimate_kilojoules_from_wattage_and_time
from jgh_formulae02 import calculate_wattage_riding_in_the_paceline 
from jgh_formulae04 import log_rider_work_assignments
from computation_classes import RiderWorkAssignmentItem, RiderExertionItem
from jgh_formulae04 import populate_rider_work_assignments
import logging
logger = logging.getLogger(__name__)

# This function called during parallel processing. Logging forbidden
def populate_rider_exertions(rider_work_assignments: DefaultDict[ZsunItem, List[RiderWorkAssignmentItem]]) -> DefaultDict[ZsunItem, List[RiderExertionItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the paceline.
        rider_work_assignments (Dict[ZsunItem, List[RiderWorkAssignmentItem]): The dictionary of rider workunits.

    Returns:
        Dict[ZsunItem, List[RiderExertionItem]]: A dictionary of Zwift riders with
            their list of respective efforts including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of dict_of_rider_exertions
    """
    rider_workloads: DefaultDict[ZsunItem, List[RiderExertionItem]] = defaultdict(list)
    
    for rider, dict_of_rider_work_assignments in rider_work_assignments.items():
        dict_of_rider_exertions: List[RiderExertionItem] = []
        for assignment in dict_of_rider_work_assignments:
            wattage = calculate_wattage_riding_in_the_paceline(rider, assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            dict_of_rider_exertions.append(RiderExertionItem(current_location_in_paceline=assignment.position, speed_kph=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = dict_of_rider_exertions
    
    return rider_workloads

def log_rider_exertions(test_description: str, result: DefaultDict[ZsunItem, List[RiderExertionItem]]) -> None:
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
        "seconds", 
        "watts", 
        "kJ"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain",disable_numparse=True))

def main() -> None:

    dict_of_ZsunItems = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)
    team_name = "test_sample"
    riderIDs = RepositoryOfTeams.get_IDs_of_riders_on_a_team(team_name)
    riders: List[ZsunItem] = get_recognised_ZsunItems_only(riderIDs, dict_of_ZsunItems)

    pull_durations = [120.0, 0.0, 30.0] # in this demo, duration array MUST be same len as riders (or longer), and the sequence MUST match the rider order in the paceline

    pull_speeds_kph = [40.0] * len(riders)

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    log_rider_work_assignments("Calculated rider work assignments during paceline rotation [RiderWorkAssignmentItem]:", dict_of_rider_work_assignments)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", dict_of_rider_exertions)

if __name__ == "__main__":
    from handy_utilities import read_json_dict_of_ZsunDTO, get_recognised_ZsunItems_only
    from team_rosters import RepositoryOfTeams
    from filenames import RIDERS_FILE_NAME
    from dirpaths import DATA_DIRPATH
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")


    main()

