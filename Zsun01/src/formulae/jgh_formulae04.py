from typing import Dict, List
from zsun_rider_item import ZsunRiderItem
from computation_classes import *

def populate_rider_work_assignments(riders: List[ZsunRiderItem], pull_durations: List[float], pull_speeds_kph: List[float]) -> Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]]:
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
        riders (List[ZsunRiderItem]): The list of Zwift riders from head to tail.
        pull_durations (List[float]): The list of pull durations from head to tail.
        pull_speeds_kph (List[float]): The list of pull speeds from head to tail.

    Returns:
        Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]]: A dictionary of Zwift riders 
            with their list of respective assignments, being how fast they must go for 
            how long in which position. 
    """
    n = len(riders)
    if n == 0:
        return {}

    if len(pull_durations) == 0 or len(pull_speeds_kph) == 0:
        return {rider: [RiderWorkAssignmentItem()] for rider in riders}

    min_length = min(len(pull_durations), len(pull_speeds_kph))

    rider_workunits: Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]] = {}
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


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    def log_results_work_assignments(test_description: str, result: Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]], logger: logging.Logger) -> None:
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
        logger.info(f"{test_description}:\n" + tabulate(table, headers=headers, tablefmt="plain"))

    from handy_utilities import read_dict_of_zsunrider_items

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zsunrider_items(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)


    davek : ZsunRiderItem = dict_of_zwiftrideritem['3147366'] # davek
    barryb : ZsunRiderItem = dict_of_zwiftrideritem['5490373'] # barryb
    johnh : ZsunRiderItem = dict_of_zwiftrideritem['1884456'] # johnh 1884456
    lynseys : ZsunRiderItem = dict_of_zwiftrideritem['383480'] # lynseys

    pull_speeds_kph = [44.0, 40.0, 38.0, 36.0]
    pull_durations = [120.0, 60.0, 30.0, 10.0]
    riders : list[ZsunRiderItem] = [davek, barryb, johnh, lynseys]

    assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    log_results_work_assignments("Example riders",assignments, logger)

if __name__ == "__main__":
    main()


