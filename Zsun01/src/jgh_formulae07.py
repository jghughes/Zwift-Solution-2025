from typing import Dict, List
from zwiftrider_item import ZwiftRiderItem
from pydantic import BaseModel
from jgh_formulae05 import RiderEffortItem
from jgh_formulae06 import calculate_normalized_watts

class RiderAggregateEffortItem(BaseModel):
    total_duration: float = 0
    average_speed: float = 0
    total_distance: float = 0
    weighted_average_watts : float = 0
    normalized_average_watts : float = 0
    instantaneous_peak_wattage: float = 0
    total_kilojoules_at_weighted_watts: float = 0
    total_kilojoules_at_normalized_watts: float = 0


def calculate_rider_aggregate_efforts(riders: Dict[ZwiftRiderItem, List[RiderEffortItem]]) -> Dict[ZwiftRiderItem, RiderAggregateEffortItem]:
    """
    Calculates aggregate_effort workload metrics for each rider.

    Args:
        riders (Dict[ZwiftRiderItem, List[RiderEffortItem]]): The dictionary of riders with their aggregate_effort workload line items.

    Returns:
        Dict[ZwiftRiderItem, RiderAggregateEffortItem]: A dictionary of riders with their aggregate_effort workload metrics.
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
        total_kilojoules_at_weighted_watts = sum(item.kilojoules for item in efforts)


        # Calculate average wattage
        total_wattage_duration = sum(item.wattage * item.duration for item in efforts)
        weighted_average_watts = total_wattage_duration / total_duration if total_duration != 0 else 0
        normalized_average_watts = calculate_normalized_watts(efforts)
        instantaneous_peak_wattage = max(item.wattage for item in efforts)
        total_kilojoules_at_normalized_watts = normalized_average_watts * total_duration / 1_000

        rider_aggregates[rider] = RiderAggregateEffortItem(
            total_duration=total_duration,
            average_speed=average_speed,
            total_distance=total_distance,
            weighted_average_watts=weighted_average_watts,
            normalized_average_watts= normalized_average_watts,
            instantaneous_peak_wattage=instantaneous_peak_wattage,
            total_kilojoules_at_weighted_watts=total_kilojoules_at_weighted_watts,
            total_kilojoules_at_normalized_watts = total_kilojoules_at_normalized_watts
        )

    return rider_aggregates


class RiderPerformanceItem(BaseModel):
    peak_wattage_over_ftp: float = 0
    total_normalized_kilojoules_over_ftp_kilojoules: float = 0

def calculate_rider_performances(riders: Dict[ZwiftRiderItem, RiderAggregateEffortItem]) -> Dict[ZwiftRiderItem, RiderPerformanceItem]:
    """
    Calculates performance metrics for each rider.
    Args:
        riders (Dict[ZwiftRiderItem, RiderAggregateEffortItem]): The dictionary of riders with their aggregate_effort workload metrics.
    Returns:
        Dict[ZwiftRiderItem, RiderPerformanceItem]: A dictionary of riders with their performance metrics.
    """
    rider_performance: Dict[ZwiftRiderItem, RiderPerformanceItem] = {}
    for rider, aggregate_effort in riders.items():

        if rider.ftp == 0:
            # Handle case where rider has no FTP
            rider_performance[rider] = RiderPerformanceItem()
            continue

        power_factor = aggregate_effort.instantaneous_peak_wattage / rider.ftp if rider.ftp != 0 else 0
        energy_intensity = aggregate_effort.total_kilojoules_at_normalized_watts / (rider.ftp * aggregate_effort.total_duration/1_000 )

        rider_performance[rider] = RiderPerformanceItem(
            peak_wattage_over_ftp = power_factor,
            total_normalized_kilojoules_over_ftp_kilojoules= energy_intensity
        )
    return rider_performance

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
    davek : ZwiftRiderItem = dict_of_zwiftrideritem['davek']
    scottm : ZwiftRiderItem = dict_of_zwiftrideritem['scottm']
    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']
    joshn : ZwiftRiderItem = dict_of_zwiftrideritem['joshn']
    edh : ZwiftRiderItem = dict_of_zwiftrideritem['edh']
    richardm : ZwiftRiderItem = dict_of_zwiftrideritem['richardm']

    # Create a list of the selected riders
    riders : list[ZwiftRiderItem] = [davek, scottm, barryb, johnh, lynseys, joshn, edh, richardm]

    # Example riders and pull durations
    pull_durations = [90.0, 60.0, 30.0, 30.0, 30.0, 30.0, 15.0, 15.0]

    # Compose the rider work_assignments
    work_assignments = compose_map_of_rider_work_assignments(riders, pull_durations)

    speeds = [37.5, 40.0, 42.5, 45.0]
    for speed in speeds:
        # Calculate rider efforts
        rider_efforts = populate_map_of_rider_efforts(speed, work_assignments)

        # Calculate the aggregate_effort workloads
        rider_aggregate_efforts = calculate_rider_aggregate_efforts(rider_efforts)


        # Display the outcome using tabulate
        table = []
        for rider, aggregate_effort in rider_aggregate_efforts.items():
            table.append([
                rider.name,
                aggregate_effort.total_duration,
                aggregate_effort.average_speed,
                aggregate_effort.total_distance,
                round(aggregate_effort.weighted_average_watts),
                round(aggregate_effort.normalized_average_watts),
                round(aggregate_effort.instantaneous_peak_wattage),
                round(aggregate_effort.total_kilojoules_at_normalized_watts)
            ])
        logger.info(f"\nSpeed={speed}km/h")
        headers = ["Rider", "Duration (s)", "Av Speed (km/h)", "Dist(km)", "Av power (W)", "NPower (W)", "Peak power (W)", "Energy (kJ)"]
        logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

        #calculate rider performances
        rider_performances = calculate_rider_performances(rider_aggregate_efforts)

        # Display the outcome using tabulate
        table = []
        for rider, performance in rider_performances.items():
            table.append([
                rider.name,
                round(performance.peak_wattage_over_ftp, 1),
                round(performance.total_normalized_kilojoules_over_ftp_kilojoules, 1)
            ])
        logger.info(f"\nSpeed={speed}km/h")
        headers = ["Rider", "Peak W/FTP", "Energy Intensity"]
        logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))



if __name__ == "__main__":
    main()

            # total_duration=total_duration,
            # average_speed=average_speed,
            # total_distance=total_distance,
            # weighted_average_watts=weighted_average_watts,
            # normalized_average_watts= normalized_average_watts,
            # instantaneous_peak_wattage=instantaneous_peak_wattage,
            # total_kilojoules_at_weighted_watts=total_kilojoules_at_weighted_watts,
            # total_kilojoules_at_normalized_watts = total_kilojoules_at_normalized_watts

