from typing import Dict, List, Tuple
from zwiftrider_item import ZwiftRiderItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
from pydantic import BaseModel

class RiderWorkloadLineItem(BaseModel):
    position: int = 0
    speed: float = 0
    duration: float = 0
    wattage: float = 0
    wattage_ftp_ratio: float = 0
    joules: float = 0


def calculate_rider_workload_lineitems(speed: float, rider_workunits: Dict[ZwiftRiderItem, List[Tuple[int, float]]]) -> Dict[ZwiftRiderItem, List[RiderWorkloadLineItem]]:
    """
    Projects the rider_workunits dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the peloton.
        rider_workunits (Dict[ZwiftRiderItem, List[Tuple[int, float]]]): The dictionary of rider workunits.

    Returns:
        Dict[ZwiftRiderItem, List[RiderWorkloadLineItem]]: A dictionary of Zwift riders with
            their list of respective workload parameters including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of workloads
    """
    rider_workloads: Dict[ZwiftRiderItem, List[RiderWorkloadLineItem]] = {}
    
    for rider, workunits in rider_workunits.items():
        workloads: List[RiderWorkloadLineItem] = []
        for position, duration in workunits:
            wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position)
            wattage_ftp_ratio: float = wattage / rider.ftp if rider.ftp != 0 else 0
            joules = estimate_kilojoules_from_wattage_and_time(wattage, duration)

            workloads.append(RiderWorkloadLineItem(position=position, speed=speed, duration=duration, wattage=wattage, wattage_ftp_ratio=wattage_ftp_ratio, joules=joules))
        rider_workloads[rider] = workloads
    
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

    # Generate the rider-workunit mapping
    mapping = generate_rider_workunit_mapping(riders, pull_durations)

    # Calculate the rider workloads
    speed = 40.0  # Example speed
    workloads = calculate_rider_workload_lineitems(speed, mapping)

    # Display the outcome using tabulate
    table = []
    for rider, tasks in workloads.items():
        for position, speed, duration, wattage in tasks:
            table.append([rider.name, position, speed, duration, wattage])

    headers = ["Rider", "Position", "Speed", "Pull Duration", "Wattage"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
