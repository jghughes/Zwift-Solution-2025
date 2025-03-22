from typing import Dict, List, Tuple
from zwiftrider_item import ZwiftRiderItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
from pydantic import BaseModel

class RiderEffortItem(BaseModel):
    position: int = 0
    speed: float = 0
    duration: float = 0
    wattage: float = 0
    kilojoules: float = 0


def populate_map_of_rider_efforts(speed: float, rider_workunits: Dict[ZwiftRiderItem, List[Tuple[int, float]]]) -> Dict[ZwiftRiderItem, List[RiderEffortItem]]:
    """
    Projects the rider_workunits dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the peloton.
        rider_workunits (Dict[ZwiftRiderItem, List[Tuple[int, float]]]): The dictionary of rider workunits.

    Returns:
        Dict[ZwiftRiderItem, List[RiderEffortItem]]: A dictionary of Zwift riders with
            their list of respective workload parameters including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of rider_efforts
    """
    rider_workloads: Dict[ZwiftRiderItem, List[RiderEffortItem]] = {}
    
    for rider, workunits in rider_workunits.items():
        rider_efforts: List[RiderEffortItem] = []
        for position, duration in workunits:
            wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, duration)

            rider_efforts.append(RiderEffortItem(position=position, speed=speed, duration=duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_efforts
    
    return rider_workloads

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

    # Compose the rider work_assignments
    work_assignments = compose_map_of_rider_work_assignments(riders, pull_durations)

    # Calculate rider efforts
    speed = 40.0  # Example speed
    rider_efforts = populate_map_of_rider_efforts(speed, work_assignments)

    # Display the outcome using tabulate
    table = []

    for rider, efforts in rider_efforts.items():
        for effort in efforts:
            table.append([rider.name, effort.position, round(effort.speed, 1), round(effort.duration), round(effort.wattage), round(effort.kilojoules, 1)])

    headers = ["Rider", "Position", "Speed", "Duration of effort", "Wattage", "kJ expended"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

if __name__ == "__main__":
    main()

