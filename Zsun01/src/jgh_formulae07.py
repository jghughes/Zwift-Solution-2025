from typing import Dict, List
from dataclasses import dataclass
from zwiftrider_item import ZwiftRiderItem
from zwiftrider_related_items import RiderWorkItem, RiderAggregateWorkItem
from jgh_formulae06 import calculate_normalized_watts
import logging


def calculate_rider_aggregate_efforts(rider_scenario: Dict[ZwiftRiderItem, List[RiderWorkItem]]) -> Dict[ZwiftRiderItem, RiderAggregateWorkItem]:
    """
    Calculates aggregate_effort metrics for each rider across all his positions in a complete orbit of a paceline.

    Args:
        rider_scenario (Dict[ZwiftRiderItem, List[RiderWorkItem]]): The dictionary of rider_scenario with their aggregate_effort workload line items.

    Returns:
        Dict[ZwiftRiderItem, RiderAggregateWorkItem]: A dictionary of rider_scenario with their aggregate_effort workload metrics.
    """
    rider_aggregates: Dict[ZwiftRiderItem, RiderAggregateWorkItem] = {}

    for rider, efforts in rider_scenario.items():

        if not efforts:
            # Handle case where there are no workload line items
            rider_aggregates[rider] = RiderAggregateWorkItem()
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
        position_at_peak_wattage = next((i for i, item in enumerate(efforts) if item.wattage == instantaneous_peak_wattage), 0)
        total_kilojoules_at_normalized_watts = normalized_average_watts * total_duration / 1_000

        rider_aggregates[rider] = RiderAggregateWorkItem(
            total_duration=total_duration,
            average_speed=average_speed,
            total_distance=total_distance,
            weighted_average_watts=weighted_average_watts,
            normalized_average_watts= normalized_average_watts,
            instantaneous_peak_wattage=instantaneous_peak_wattage,
            position_at_peak_wattage=position_at_peak_wattage,
            total_kilojoules_at_weighted_watts=total_kilojoules_at_weighted_watts,
            total_kilojoules_at_normalized_watts = total_kilojoules_at_normalized_watts
        )

    return rider_aggregates

@dataclass(frozen=True, eq=True) # immutable and hashable
class RiderStressItem():
    peak_watts_divided_by_ftp_watts: float = 0
    position_at_peak_wattage : int = 0
    total_normalized_kilojoules_divided_by_ftp_kilojoules: float = 0


def calculate_rider_stress_metrics(rider_scenario: Dict[ZwiftRiderItem, RiderAggregateWorkItem]) -> Dict[ZwiftRiderItem, RiderStressItem]:
    """
    Calculates stress metrics for each rider across all his positions in a complete orbit of a paceline.

    Args:
        rider_scenario (Dict[ZwiftRiderItem, RiderAggregateWorkItem]): The dictionary of rider_scenario with their aggregate_effort workload metrics.
    Returns:
        Dict[ZwiftRiderItem, RiderStressItem]: A dictionary of rider_scenario with their stress metrics.
    """
    rider_performance: Dict[ZwiftRiderItem, RiderStressItem] = {}
    for rider, aggregate_effort in rider_scenario.items():

        if rider.ftp == 0:
            # Handle case where rider has no FTP
            rider_performance[rider] = RiderStressItem()
            continue

        power_factor = aggregate_effort.instantaneous_peak_wattage / rider.ftp if rider.ftp != 0 else 0
        energy_intensity = aggregate_effort.total_kilojoules_at_normalized_watts / (rider.ftp * aggregate_effort.total_duration/1_000 )

        rider_performance[rider] = RiderStressItem(
            peak_watts_divided_by_ftp_watts = power_factor,
            position_at_peak_wattage= aggregate_effort.position_at_peak_wattage,
            total_normalized_kilojoules_divided_by_ftp_kilojoules= energy_intensity
        )
    return rider_performance


def log_rider_aggregate_efforts(test_description: str, result: Dict[ZwiftRiderItem, RiderAggregateWorkItem], logger: logging.Logger) -> None:
    from tabulate import tabulate
    table = []
    for rider, aggregate_effort in result.items():
        table.append([
            rider.name,
            # aggregate_effort.total_duration,
            # aggregate_effort.average_speed,
            # round(aggregate_effort.total_distance,3),
            aggregate_effort.position_at_peak_wattage,
            round(aggregate_effort.instantaneous_peak_wattage),
            round(aggregate_effort.normalized_average_watts),
            round(aggregate_effort.weighted_average_watts),
            round(aggregate_effort.total_kilojoules_at_normalized_watts)
        ])
    if test_description:
            logger.info(test_description)
    headers = ["Rider", "Peak watts position", "Peak Watts", "Norm. Watts",  "Av Watts",  "Norm. kJ"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


def log_rider_stress_metrics(test_description: str, result: Dict[ZwiftRiderItem, RiderStressItem], logger: logging.Logger) -> None:
    from tabulate import tabulate
    table = []
    for rider, performance in result.items():
        table.append([
            rider.name,
            round(performance.peak_watts_divided_by_ftp_watts, 1),
            performance.position_at_peak_wattage,
            round(performance.total_normalized_kilojoules_divided_by_ftp_kilojoules, 1)
        ])
    if test_description:
            logger.info(test_description)    
    headers = ["Rider", "Peak W/FTP", "Position when Peak W ", "Energy Intensity"]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

# Example usage in the main function
def main() -> None:

    # Configure logging

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_efforts
    from handy_utilities import get_all_zwiftriders

    # Define constituents of one or more scenarios (4 pull speed scenarios in this case))

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    joshn : ZwiftRiderItem = dict_of_zwiftrideritem['joshn']
    richardm : ZwiftRiderItem = dict_of_zwiftrideritem['richardm']
    
    rider_scenario : list[ZwiftRiderItem] = [barryb, johnh, joshn, richardm]
    pull_duration_scenario = [120.0, 30.0, 30.0, 30.0]
    pull_speed_scenarios = [
        # [37.5, 37.5, 37.5, 37.5],
        [40.0, 40.0, 40.0, 40.0],
        # [42.5, 42.5, 42.5, 42.5],
        # [45.0, 45.0, 45.0, 45.0]
    ]

    # Compose the rider work_assignments, then work_efforts, then aggregate_efforts, and then stress_metrics for each scenario

    for i, scenario in enumerate(pull_speed_scenarios):
        work_assignments = populate_rider_work_assignments(rider_scenario, pull_duration_scenario, scenario)
        rider_efforts = populate_rider_efforts(work_assignments)
        rider_aggregate_efforts = calculate_rider_aggregate_efforts(rider_efforts)
        rider_stress_metrics = calculate_rider_stress_metrics(rider_aggregate_efforts)

        total_duration = next(iter(rider_aggregate_efforts.values())).total_duration
        average_speed = next(iter(rider_aggregate_efforts.values())).average_speed #careful. formula only valid when speed is constant, as it is in this case
        total_distance = next(iter(rider_aggregate_efforts.values())).total_distance

        table_heading= f"\nPull durations={pull_duration_scenario}sec\nPull speeds={pull_speed_scenarios[i]}km/h\nTotal_duration={total_duration}  Ave_speed={average_speed}  Total_dist={total_distance}"
        log_rider_aggregate_efforts(table_heading, rider_aggregate_efforts, logger)

        log_rider_stress_metrics(f"", rider_stress_metrics, logger)
        
if __name__ == "__main__":
    main()

