from typing import Dict, List
from zwiftrider_item import ZwiftRiderItem
from pydantic import BaseModel

class RiderWorkAssignmentItem(BaseModel):
    position: int = 1
    duration: float = 0
    speed: float = 0

def compose_map_of_rider_work_assignments(riders: List[ZwiftRiderItem], pull_durations: List[float], pull_speeds: List[float]) -> Dict[ZwiftRiderItem, List["RiderWorkAssignmentItem"]]:
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

# Example usage:
def main() -> None:
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from typing import Dict, cast
    from jgh_read_write import read_text
    from jgh_serialization import JghSerialization
    from zwiftrider_dto import ZwiftRiderDataTransferObject
    from tabulate import tabulate

    # Load rider data from JSON
    inputjson = read_text("C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/", "rider_dictionary.json")
    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    # for the benefit of type inference: explicitly cast the return value of the serialization to expected generic Type
    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto)

    # transform to ZwiftRiderItem dict
    dict_of_zwiftrideritem = ZwiftRiderItem.from_dataTransferObject_dict(dict_of_zwiftrider_dto)

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
    mapping = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)

    # Display the outcome using tabulate
    table = []
    for rider, tasks in mapping.items():
        for task in tasks:
            table.append([rider.name, task.position, task.duration, task.speed])

    headers = ["Rider", "Position", "Pull Duration", "Pull Speed"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

# test_compose_map_of_rider_work_assignments() with lists of inconsistent length:
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

#     # Test case 1: All lists have the same length
#     pull_durations = [90.0, 60.0, 30.0]
#     pull_speeds = [40.0, 38.0, 36.0]
#     result = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     logger.info("Test case 1:", result)

#     # Test case 2: Empty riders list
#     result = compose_map_of_rider_work_assignments([], pull_durations, pull_speeds)
#     logger.info("Test case 2:", result)

#     # Test case 3: Empty pull_durations list
#     result = compose_map_of_rider_work_assignments(riders, [], pull_speeds)
#     logger.info("Test case 3:", result)

#     # Test case 4: Empty pull_speeds list
#     result = compose_map_of_rider_work_assignments(riders, pull_durations, [])
#     logger.info("Test case 4:", result)

#     # Test case 5: pull_durations shorter than riders
#     pull_durations = [90.0]
#     pull_speeds = [40.0, 38.0, 36.0]
#     result = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     logger.info("Test case 5:", result)

#     # Test case 6: pull_speeds shorter than riders
#     pull_durations = [90.0, 60.0, 30.0]
#     pull_speeds = [40.0]
#     result = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     logger.info("Test case 6:", result)

#     # Test case 7: pull_durations and pull_speeds shorter than riders
#     pull_durations = [90.0]
#     pull_speeds = [40.0]
#     result = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     logger.info("Test case 7:", result)

#     # Test case 8: pull_durations and pull_speeds longer than riders
#     pull_durations = [90.0, 60.0, 30.0, 20.0]
#     pull_speeds = [40.0, 38.0, 36.0, 34.0]
#     result = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)
#     logger.info("Test case 8:", result)
if __name__ == "__main__":
    main()


