from typing import Dict, List
from zwiftrider_item import ZwiftRiderItem
from zwiftrider_related_items import RiderWorkItem, RiderWorkAssignmentItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
import logging



def populate_rider_efforts(rider_work_assignments: Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]]) -> Dict[ZwiftRiderItem, List[RiderWorkItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the paceline.
        rider_work_assignments (Dict[ZwiftRiderItem, List[RiderWorkAssignmentItem]): The dictionary of rider workunits.

    Returns:
        Dict[ZwiftRiderItem, List[RiderWorkItem]]: A dictionary of Zwift riders with
            their list of respective efforts including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of rider_efforts
    """
    rider_workloads: Dict[ZwiftRiderItem, List[RiderWorkItem]] = {}
    
    for rider, work_assignments in rider_work_assignments.items():
        rider_efforts: List[RiderWorkItem] = []
        for assignment in work_assignments:
            wattage = rider.calculate_wattage_riding_in_the_peloton(assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            rider_efforts.append(RiderWorkItem(position=assignment.position, speed=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_efforts
    
    return rider_workloads

def log_results(test_description: str, result: Dict[ZwiftRiderItem, List[RiderWorkItem]], logger: logging.Logger) -> None:
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

    from jgh_formulae04 import populate_rider_work_assignments
    from handy_utilities import get_all_zwiftriders

    dict_of_zwiftrideritem = get_all_zwiftriders()

    # Instantiate ZwiftRiderItem objects for barryb, johnh, and lynseys
    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    # Create a list of the selected riders
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    # Example riders and pull durations
    pull_durations = [90.0, 60.0, 30.0]
    pull_speeds = [42.0, 38.0, 36.0]
    # Compose the rider work_assignments
    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds)

    # Calculate rider efforts
    rider_efforts = populate_rider_efforts(work_assignments)

    # Display the outcome using tabulate
    log_results("Calculated rider efforts:", rider_efforts, logger)


if __name__ == "__main__":
    main()

