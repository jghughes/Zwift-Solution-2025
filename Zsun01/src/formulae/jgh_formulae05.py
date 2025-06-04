from typing import List, DefaultDict
from collections import defaultdict
from zsun_rider_dto import ZsunRiderDTO
from zsun_rider_item import ZsunRiderItem
from jgh_formulae01 import estimate_kilojoules_from_wattage_and_time
from jgh_formulae02 import calculate_wattage_riding_in_the_paceline 
from computation_classes import RiderWorkAssignmentItem, RiderExertionItem
from jgh_formulae04 import populate_rider_work_assignments

import logging

def populate_rider_exertions(rider_work_assignments: DefaultDict[ZsunRiderItem, List[RiderWorkAssignmentItem]]) -> DefaultDict[ZsunRiderItem, List[RiderExertionItem]]:
    """
    Projects the rider_work_assignments dict to a new dict of rider_workloads with additional wattage calculation.
    
    Args:
        speed (float): The speed of the paceline.
        rider_work_assignments (Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]): The dictionary of rider workunits.

    Returns:
        Dict[ZsunRiderItem, List[RiderExertionItem]]: A dictionary of Zwift riders with
            their list of respective efforts including wattage. The Tuple representing 
            a single workload is (position, speed, duration, wattage). Each rider has a list of rider_exertions
    """
    rider_workloads: DefaultDict[ZsunRiderItem, List[RiderExertionItem]] = defaultdict(list)
    
    for rider, work_assignments in rider_work_assignments.items():
        rider_exertions: List[RiderExertionItem] = []
        for assignment in work_assignments:
            wattage = calculate_wattage_riding_in_the_paceline(rider, assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            rider_exertions.append(RiderExertionItem(current_location_in_paceline=assignment.position, speed_kph=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_exertions
    
    return rider_workloads

def log_rider_exertions(test_description: str, result: DefaultDict[ZsunRiderItem, List[RiderExertionItem]], logger: logging.Logger) -> None:
    from tabulate import tabulate
    logger.info(test_description)
    table = []
    for rider, efforts in result.items():
        for effort in efforts:
            table.append([
                rider.name, 
                effort.current_location_in_paceline, 
                round(effort.speed_kph, 1), 
                round(effort.duration), 
                round(effort.wattage, 0), 
                round(effort.kilojoules, 0)
            ])

    headers = [
        "rider", 
        "location", 
        "kph", 
        "seconds", 
        "watts", 
        "kJ"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain",disable_numparse=True))

def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)



    # Example: Instantiate riders using the Config class
    example_riders_data = [
        # ZsunRiderItem.Config.json_schema_extra["meridithl"],
        # ZsunRiderItem.Config.json_schema_extra["melissaw"],
        ZsunRiderItem.Config.json_schema_extra["richardm"],
        # ZsunRiderItem.Config.json_schema_extra["davek"],
        # ZsunRiderItem.Config.json_schema_extra["huskyc"],
        # ZsunRiderItem.Config.json_schema_extra["scottm"],
        # ZsunRiderItem.Config.json_schema_extra["johnh"],
        ZsunRiderItem.Config.json_schema_extra["joshn"],
        # ZsunRiderItem.Config.json_schema_extra["brent"],
        # ZsunRiderItem.Config.json_schema_extra["coryc"],
        # ZsunRiderItem.Config.json_schema_extra["davide"],
    ]

    # Convert example data to ZsunRiderItem instances
    riders = [
        ZsunRiderItem.from_dataTransferObject(ZsunRiderDTO.model_validate(data))
        for data in example_riders_data
    ]

    pull_durations = [60.0] * len(riders)
    pull_speeds_kph = [40.0] * len(riders)

    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

if __name__ == "__main__":
    main()

