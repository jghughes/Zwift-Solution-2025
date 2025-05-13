from typing import Dict, List
from zsun_rider_item import ZsunRiderItem
from jgh_formulae import estimate_kilojoules_from_wattage_and_time
from computation_classes import *
from jgh_formulae03 import *


def populate_rider_exertions(rider_work_assignments: Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]]) -> Dict[ZsunRiderItem, List[RiderExertionItem]]:
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
    rider_workloads: Dict[ZsunRiderItem, List[RiderExertionItem]] = {}
    
    for rider, work_assignments in rider_work_assignments.items():
        rider_exertions: List[RiderExertionItem] = []
        for assignment in work_assignments:
            wattage = rider.calculate_wattage_riding_in_the_paceline(assignment.speed, assignment.position)
            kilojoules = estimate_kilojoules_from_wattage_and_time(wattage, assignment.duration)

            rider_exertions.append(RiderExertionItem(current_location_in_paceline=assignment.position, speed_kph=assignment.speed, duration=assignment.duration, wattage=wattage, kilojoules=kilojoules))
        rider_workloads[rider] = rider_exertions
    
    return rider_workloads


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import populate_rider_work_assignments

    def log_results_exertions(test_description: str, result: Dict[ZsunRiderItem, List[RiderExertionItem]], logger: logging.Logger) -> None:
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
            "seconds)", 
            "watts", 
            "kJ"
        ]
        logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

    # Example: Instantiate riders using the Config class
    example_riders_data = [
        # ZsunRiderItem.Config.json_schema_extra["meridithl"],
        ZsunRiderItem.Config.json_schema_extra["melissaw"],
        ZsunRiderItem.Config.json_schema_extra["richardm"],
        ZsunRiderItem.Config.json_schema_extra["davek"],
        # ZsunRiderItem.Config.json_schema_extra["huskyc"],
        ZsunRiderItem.Config.json_schema_extra["scottm"],
        # ZsunRiderItem.Config.json_schema_extra["johnh"],
        # ZsunRiderItem.Config.json_schema_extra["joshn"],
        # ZsunRiderItem.Config.json_schema_extra["brent"],
        # ZsunRiderItem.Config.json_schema_extra["coryc"],
        # ZsunRiderItem.Config.json_schema_extra["davide"],
    ]

    # Convert example data to ZsunRiderItem instances
    riders = [
        ZsunRiderItem.from_dataTransferObject(ZsunRiderDTO.model_validate(data))
        for data in example_riders_data
    ]
    target_speed_kph = calculate_target_speed_of_paceline(riders)

    strong_riders, weak_riders = deselect_weaker_riders(riders) # from here on we ignore weak riders - for now

    # the pull durations for all strong_riders is the same, 60 seconds
    # the pull speeds are the same for all strong_riders, = target_speed_kph

    pull_durations = [60.0] * len(strong_riders)
    pull_speeds_kph = [target_speed_kph] * len(strong_riders)

    work_assignments = populate_rider_work_assignments(strong_riders, pull_durations, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    log_results_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

if __name__ == "__main__":
    main()

