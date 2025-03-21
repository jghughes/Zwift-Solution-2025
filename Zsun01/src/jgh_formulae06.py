from typing import Dict, List
from zwiftrider_item import ZwiftRiderItem
from pydantic import BaseModel
from jgh_formulae05 import RiderWorkloadLineItem

class RiderAggregateWorkloadItem(BaseModel):
    total_duration: float = 0
    average_speed: float = 0
    total_distance: float = 0
    total_joules: float = 0
    ratio_of_joules_to_ftp: float = 0

def calculate_rider_aggregate_workload(riders: Dict[ZwiftRiderItem, List[RiderWorkloadLineItem]]) -> Dict[ZwiftRiderItem, RiderAggregateWorkloadItem]:
    """
    Calculates aggregate workload metrics for each rider.

    Args:
        riders (Dict[ZwiftRiderItem, List[RiderWorkloadLineItem]]): The dictionary of riders with their aggregate workload line items.

    Returns:
        Dict[ZwiftRiderItem, RiderAggregateWorkloadItem]: A dictionary of riders with their aggregate workload metrics.
    """
    rider_aggregates: Dict[ZwiftRiderItem, RiderAggregateWorkloadItem] = {}

    for rider, workload_items in riders.items():
        total_duration = sum(item.duration for item in workload_items) # measured in seconds
        total_distance = sum(item.speed * item.duration / 3600 for item in workload_items)  # convert to km
        average_speed = total_distance / (total_duration / 3600) if total_duration != 0 else 0  # convert to km/h
        total_joules = sum(item.joules for item in workload_items) / 1000  # convert to kJ

        joules_alone_at_ftp = rider.calculate_wattage_riding_alone(average_speed) * total_duration / 1000  # convert to kJ
        ratio_of_joules_to_ftp = total_joules / joules_alone_at_ftp if joules_alone_at_ftp != 0 else 0

        rider_aggregates[rider] = RiderAggregateWorkloadItem(
            total_duration=total_duration,
            average_speed=average_speed,
            total_distance=total_distance,
            total_joules=total_joules,
            ratio_of_joules_to_ftp=ratio_of_joules_to_ftp,
        )

    return rider_aggregates

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

    # Calculate the aggregate workloads
    aggregate_workloads = calculate_rider_aggregate_workload(workloads)

    # Display the outcome using tabulate
    table = []
    for rider, aggregate in aggregate_workloads.items():
        table.append([
            rider.name,
            aggregate.total_duration,
            aggregate.average_speed,
            aggregate.total_distance,
            aggregate.total_joules,
            aggregate.ratio_of_joules_to_ftp
        ])

    headers = ["Rider", "Total Duration (s)", "Average Speed (km/h)", "Total Distance (km)", "Total Joules (kJ)", "Ratio of Joules to FTP"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
