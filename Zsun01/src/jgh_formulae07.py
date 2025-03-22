from typing import Dict, List
from zwiftrider_item import ZwiftRiderItem
from pydantic import BaseModel
from jgh_formulae05 import RiderEffortItem
from jgh_formulae06 import calculate_normalized_watts

class RiderAggregateEffortItem(BaseModel):
    total_duration: float = 0
    average_speed: float = 0
    total_distance: float = 0
    total_kilojoules: float = 0
    weighted_average_watts : float = 0
    normalized_watts : float = 0
    instantaneous_peak_wattage: float = 0

def calculate_rider_aggregate_efforts(riders: Dict[ZwiftRiderItem, List[RiderEffortItem]]) -> Dict[ZwiftRiderItem, RiderAggregateEffortItem]:
    """
    Calculates aggregate workload metrics for each rider.

    Args:
        riders (Dict[ZwiftRiderItem, List[RiderEffortItem]]): The dictionary of riders with their aggregate workload line items.

    Returns:
        Dict[ZwiftRiderItem, RiderAggregateEffortItem]: A dictionary of riders with their aggregate workload metrics.
    """
    rider_aggregates: Dict[ZwiftRiderItem, RiderAggregateEffortItem] = {}

    for rider, efforts in riders.items():

        if not efforts:
            # Handle case where there are no workload line items
            rider_aggregates[rider] = RiderAggregateEffortItem()
            continue
        total_duration = sum(item.duration for item in efforts) # measured in seconds
        total_distance = sum(item.speed * item.duration / 3600 for item in efforts)  # convert to km
        average_speed = total_distance / (total_duration / 3600) if total_duration != 0 else 0  # convert to km/h
        total_kilojoules = sum(item.kilojoules for item in efforts)


        # Calculate average wattage
        total_wattage_duration = sum(item.wattage * item.duration for item in efforts)
        weighted_average_watts = total_wattage_duration / total_duration if total_duration != 0 else 0
        normalized_watts = calculate_normalized_watts(efforts)
        instantaneous_peak_wattage = max(item.wattage for item in efforts)

        rider_aggregates[rider] = RiderAggregateEffortItem(
            total_duration=total_duration,
            average_speed=average_speed,
            total_distance=total_distance,
            total_kilojoules=total_kilojoules,
            weighted_average_watts=weighted_average_watts,
            normalized_watts= normalized_watts,
            instantaneous_peak_wattage=instantaneous_peak_wattage
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
    from jgh_formulae04 import compose_map_of_rider_work_assignments
    from jgh_formulae05 import populate_map_of_rider_efforts

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

    # Calculate the aggregate workloads
    rider_aggregate_efforts = calculate_rider_aggregate_efforts(rider_efforts)

    # Display the outcome using tabulate
    table = []
    for rider, aggregate in rider_aggregate_efforts.items():
        table.append([
            rider.name,
            aggregate.total_duration,
            aggregate.average_speed,
            aggregate.total_distance,
            round(aggregate.total_kilojoules,1),
            round(aggregate.instantaneous_peak_wattage)
        ])

    headers = ["Rider", "Total Duration (s)", "Average Speed (km/h)", "Total Distance (km)", "Total energy (kJ)", "Peak power (W)"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

if __name__ == "__main__":
    main()
