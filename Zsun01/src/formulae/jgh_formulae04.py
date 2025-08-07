from typing import List, DefaultDict
from collections import defaultdict
from zsun_rider_item import ZsunItem
from computation_classes import RiderWorkAssignmentItem
import logging
logger = logging.getLogger(__name__)

# This function called during parallel processing. Logging forbidden
def populate_rider_work_assignments(riders: List[ZsunItem], pull_durations: List[float], pull_speeds_kph: List[float]) -> DefaultDict[ZsunItem, List[RiderWorkAssignmentItem]]:
    """
    Generates a mapping for a team of riders in a Team Time Trial race to their workloads. 
    Riders circulate in a cyclical pattern in a paceline, with each rider taking a turn 
    at the head (a pull) and then rotating to the tail sequentially. The sequence
    of pulls is according to pull_durations and pull_speeds_kph lists. Each rider has as many 
    workunits as there are positions/riders in the circulating paceline. Each workunit 
    is an instance of RiderWorkAssignmentItem according to position of the rider 
    in the paceline, and his duration and speed in that position as dictated 
    by the duarion and speed of the prevailing leader at that point in time.

    Args:
        riders (List[ZsunItem]): The list of Zwift riders from head to tail.
        pull_durations (List[float]): The list of pull durations from head to tail.
        pull_speeds_kph (List[float]): The list of pull speeds from head to tail.

    Returns:
        Dict[ZsunItem, List[RiderWorkAssignmentItem]]: A dictionary of Zwift riders 
            with their list of respective assignments, being how fast they must go for 
            how long in which position. 
    """
    n = len(riders)

    if n == 0:
        return defaultdict(list)

    if len(pull_durations) == 0 or len(pull_speeds_kph) == 0:
        dd = defaultdict(list)
        for rider in riders:
            dd[rider] = [RiderWorkAssignmentItem()]
        return dd

    min_length = min(len(pull_durations), len(pull_speeds_kph))

    rider_workunits: DefaultDict[ZsunItem, List[RiderWorkAssignmentItem]] = defaultdict(list)
    for k in range(1, n + 1):
        workunits: List[RiderWorkAssignmentItem] = []
        for j in range(n):
            # The formula ensures that each rider's position is calculated in a way that 
            # they rotate through the pace line in a cyclical manner. The modulo operation 
            # handles the wrap-around, and the addition of 1 converts the result to a 1-based index.
            position = (k + n - j - 1) % n + 1
            if j < min_length:
                duration = pull_durations[j]
                speed = pull_speeds_kph[j]
                workunit = RiderWorkAssignmentItem(position=position, duration=duration, speed=speed)
            else:
                workunit = RiderWorkAssignmentItem(position=position)
            workunits.append(workunit)
        rider_workunits[riders[k - 1]] = workunits
    return rider_workunits

def log_rider_work_assignments(test_description: str, result: DefaultDict[ZsunItem, List[RiderWorkAssignmentItem]]) -> None:
    from tabulate import tabulate

    table = []
    for rider, assignments in result.items():
        for assignment in assignments:
            table.append([
                rider.name, 
                assignment.position, 
                assignment.duration, 
                assignment.speed
            ])

    headers = [
        "Rider", 
        "Position", 
        "Duration (sec)", 
        "Speed (kph)"
    ]
    logger.info(f"{test_description}:\n" + tabulate(table, headers=headers, tablefmt="plain",disable_numparse=True))

def main() -> None:

    dict_of_ZsunItems = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)
    team_name = "test"
    riderIDs = get_riderIDs_on_team_roster(team_name)
    riders: List[ZsunItem] = get_recognised_ZsunItems_only(riderIDs, dict_of_ZsunItems)

    pull_durations = [120.0, 0.0, 120.0, 120.0] # in this demo, duration array MUST be same len as riders (or longer), and the sequence MUST match the rider order in the paceline
    pull_speeds_kph = [40.0] * len(riders)

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    log_rider_work_assignments("Example riders",dict_of_rider_work_assignments)

if __name__ == "__main__":
    from handy_utilities import read_json_dict_of_ZsunDTO, get_recognised_ZsunItems_only
    from repository_of_team_rosters import get_riderIDs_on_team_roster
    from filenames import RIDERS_FILE_NAME
    from dirpaths import DATA_DIRPATH
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")

    main()


