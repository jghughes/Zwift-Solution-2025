from typing import Dict, List
from jgh_formulae04 import RiderWorkAssignmentItem
from zwiftrider_item import ZwiftRiderItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
from pydantic import BaseModel
import logging


class RiderEffortItem(BaseModel):
    position: int = 0
    speed: float = 0
    duration: float = 0
    wattage: float = 0
    kilojoules: float = 0


def populate_map_of_rider_efforts(rider_work_assignments: Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]]) -> Dict[ZwiftRiderItem, List[RiderEffortItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the peloton.
        rider_work_assignments (Dict[ZwiftRiderItem, List[Tuple[int, float]]]): The dictionary of rider workunits.

    Returns:
        Dict[ZwiftRiderItem, List[RiderEffortItem]]: A dictionary of Zwift riders with
            their list of respective workload parameters including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of rider_efforts
    """
    rider_workloads: Dict[ZwiftRiderItem, List[RiderEffortItem]] = {}
    
    for rider, work_assignments in rider_work_assignments.items():
        rider_efforts: List[RiderEffortItem] = []
        for assignment in work_assignments:
            wattage = rider.calculate_wattage_riding_in_the_peloton(assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            rider_efforts.append(RiderEffortItem(position=assignment.position, speed=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_efforts
    
    return rider_workloads

def log_results(test_description: str, result: Dict[ZwiftRiderItem, List[RiderEffortItem]], logger: logging.Logger) -> None:
    from tabulate import tabulate
    # Display the outcome using tabulate
    table = []

    for rider, efforts in result.items():
        for effort in efforts:
            table.append([rider.name, effort.position, round(effort.speed, 1), round(effort.duration), round(effort.wattage,0), round(effort.kilojoules, 0)])

    headers = ["Rider", "Position", "Speed", "Duration of effort", "Wattage", "kJ expended"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

# Example usage in the main function
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
    from jgh_formulae04 import compose_map_of_rider_work_assignments

    # Load rider data from JSON
    inputjson = read_text("C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/", "rider_dictionary.json")
    dict_of_zwiftrider_dto= JghSerialization.validate(inputjson, Dict[str, ZwiftRiderDataTransferObject])

    # for the benfit of type inference: explicitly cast the return value of the serialisation to expected generic Type
    dict_of_zwiftrider_dto = cast(Dict[str, ZwiftRiderDataTransferObject], dict_of_zwiftrider_dto)

    #transform to ZwiftRiderItem dict
    dict_of_zwiftrideritem = ZwiftRiderItem.from_dataTransferObject_dict(dict_of_zwiftrider_dto)

    # Instantiate ZwiftRiderItem objects for barryb, johnh, and lynseys
    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    # Create a list of the selected riders
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    # Example riders and pull durations
    pull_durations = [90.0, 60.0, 30.0]
    pull_speeds = [40.0, 40.0, 40.0]
    # Compose the rider work_assignments
    work_assignments = compose_map_of_rider_work_assignments(riders, pull_durations, pull_speeds)

    # Calculate rider efforts
    rider_efforts = populate_map_of_rider_efforts(work_assignments)

    # Display the outcome using tabulate
    log_results("Calculated rider efforts:", rider_efforts, logger)


if __name__ == "__main__":
    main()

