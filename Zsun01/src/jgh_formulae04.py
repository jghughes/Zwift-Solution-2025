from typing import Dict, List
from zwiftrider_item import ZwiftRiderItem
from pydantic import BaseModel
import logging


class RiderWorkAssignmentItem(BaseModel):
    position: int = 1
    duration: float = 0
    speed: float = 0

def compose_map_of_rider_work_assignments(riders: List[ZwiftRiderItem], pull_durations: List[float], pull_speeds: List[float]) -> Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]]:
    """
    Generates a mapping for a team of riders in a Team Time Trial race to their workloads. 
    Riders circulate in a cyclical pattern in a pace line, with each rider taking a turn 
    at the front (a pull) and then rotating to the back sequentially. The sequence
    of pulls is according to pull_durations and pull_speeds lists. Each rider has as many 
    workunits as there are position/riders in the circulating pace line. Each workunit 
    is an instance of RiderWorkAssignmentItem with the prevailing position of the rider 
    in the pace line, with the duration and speed being that of the prevailing leader at 
    the front of the pace line.

    Args:
        riders (List[ZwiftRiderItem]): The list of Zwift riders.
        pull_durations (List[float]): The list of pull durations.
        pull_speeds (List[float]): The list of pull speeds.

    Returns:
        Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]]: A dictionary of Zwift riders with
            their list of respective workunit parameters. Each workunit is an instance of 
            RiderWorkAssignmentItem.
    """
    n = len(riders)
    if n == 0:
        return {}

    if len(pull_durations) == 0 or len(pull_speeds) == 0:
        return {rider: [RiderWorkAssignmentItem()] for rider in riders}

    min_length = min(len(pull_durations), len(pull_speeds))

    rider_workunits: Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]] = {}
    for k in range(1, n + 1):
        workunits: List[RiderWorkAssignmentItem] = []
        for j in range(n):
            # The formula ensures that each rider's position is calculated in a way that 
            # they rotate through the pace line in a cyclical manner. The modulo operation 
            # handles the wrap-around, and the addition of 1 converts the result to a 1-based index.
            position = (k + n - j - 1) % n + 1
            if j < min_length:
                duration = pull_durations[j]
                speed = pull_speeds[j]
                workunit = RiderWorkAssignmentItem(position=position, duration=duration, speed=speed)
            else:
                workunit = RiderWorkAssignmentItem(position=position)
            workunits.append(workunit)
        rider_workunits[riders[k - 1]] = workunits
    return rider_workunits


def log_results(test_description: str, result: Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]], logger: logging.Logger) -> None:
    from tabulate import tabulate

    table = []
    for rider, assignments in result.items():
        for assignment in assignments:
            table.append([rider.name, assignment.position, assignment.duration, assignment.speed])

    headers = ["Rider", "Position", "Duration(s)", "Speed(kph)"]
    logger.info(f"{test_description}:\n" + tabulate(table, headers=headers, tablefmt="plain"))

# Example usage:
def main() -> None:
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from handy_utilities import get_all_zwiftriders

    dict_of_zwiftrideritem = get_all_zwiftriders()

    # Instantiate ZwiftRiderItem objects for barryb, johnh, and lynseys
    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    # Create a list of the selected riders
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    # Example riders, pull durations, and pull speeds
    pull_durations = [90.0, 60.0, 30.0]
    pull_speeds = [40.0, 38.0, 36.0]

    # Generate the rider-workunit mapping
    assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)

    log_results("Example riders",assignments, logger)

# # test_compose_map_of_rider_work_assignments() for handling of lists of inconsistent length:
# def main() -> None:
#     from zwiftrider_item import ZwiftRiderItem

#     # Configure logging
#     import logging
#     from jgh_logging import jgh_configure_logging
#     jgh_configure_logging("appsettings.json")
#     logger = logging.getLogger(__name__)



#     # Create mock ZwiftRiderItem objects
#     rider1 = ZwiftRiderItem(name="Rider1")
#     rider2 = ZwiftRiderItem(name="Rider2")
#     rider3 = ZwiftRiderItem(name="Rider3")

#     riders = [rider1, rider2, rider3]

#    # Test case 1: All lists have the same length
#     pull_durations = [90.0, 60.0, 30.0]
#     pull_speeds = [40.0, 38.0, 36.0]
#     assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     log_results("Test case 1: All lists have the same length", assignments, logger)

#     # Test case 2: Empty riders list
#     assignments = compose_map_of_rider_work_assignments([], pull_durations, pull_speeds)
#     log_results("Test case 2: Empty riders list", assignments, logger)

#     # Test case 3: Empty pull_durations list
#     assignments = compose_map_of_rider_work_assignments(riders, [], pull_speeds)
#     log_results("Test case 3: Empty pull_durations list", assignments, logger)

#     # Test case 4: Empty pull_speeds list
#     assignments = compose_map_of_rider_work_assignments(riders, pull_durations, [])
#     log_results("Test case 4: Empty pull_speeds list", assignments, logger)

#     # Test case 5: pull_durations shorter than riders
#     pull_durations = [90.0]
#     pull_speeds = [40.0, 38.0, 36.0]
#     assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     log_results("Test case 5: pull_durations shorter than riders", assignments, logger)

#     # Test case 6: pull_speeds shorter than riders
#     pull_durations = [90.0, 60.0, 30.0]
#     pull_speeds = [40.0]
#     assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     log_results("Test case 6: pull_speeds shorter than riders", assignments, logger)

#     # Test case 7: pull_durations and pull_speeds shorter than riders
#     pull_durations = [90.0]
#     pull_speeds = [40.0]
#     assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     log_results("Test case 7: pull_durations and pull_speeds shorter than riders", assignments, logger)

#     # Test case 8: pull_durations and pull_speeds longer than riders
#     pull_durations = [90.0, 60.0, 30.0, 20.0]
#     pull_speeds = [40.0, 38.0, 36.0, 34.0]
#     assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     log_results("Test case 8: pull_durations and pull_speeds longer than riders", assignments, logger)


if __name__ == "__main__":
    main()


