from typing import Dict, List
from zsun_rider_item import ZsunRiderItem
from computation_classes import *
from jgh_formulae03 import *
def populate_rider_work_assignments(riders: List[ZsunRiderItem], pull_durations: List[float], pull_speeds_kph: List[float]) -> Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]]:
    """
    Generates a mapping for a team of riders in a Team Time Trial race to their workloads. 
    Riders circulate in a cyclical pattern in a paceline, with each rider taking a turn 
    at the head (a pull) and then rotating to the tail sequentially. The sequence
    of pulls is according to pull_durations and pull_speeds_kph lists. Each rider has as many 
    workunits as there are positions/riders in the circulating paceline. Each workunit 
    is an instance of RiderWorkAssignmentItem according to position of the rider 
    in the paceline, and his duration and speed in that position as dictated 
    by the duarion and speed of the prevailing leader at that point in time.

    Args:
        riders (List[ZsunRiderItem]): The list of Zwift riders from head to tail.
        pull_durations (List[float]): The list of pull durations from head to tail.
        pull_speeds_kph (List[float]): The list of pull speeds from head to tail.

    Returns:
        Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]]: A dictionary of Zwift riders 
            with their list of respective assignments, being how fast they must go for 
            how long in which position. 
    """
    n = len(riders)
    if n == 0:
        return {}

    if len(pull_durations) == 0 or len(pull_speeds_kph) == 0:
        return {rider: [RiderWorkAssignmentItem()] for rider in riders}

    min_length = min(len(pull_durations), len(pull_speeds_kph))

    rider_workunits: Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]] = {}
    for k in range(1, n + 1):
        workunits: List[RiderWorkAssignmentItem] = []
        for j in range(n):
            # The formula ensures that each rider's position is calculated in a way that 
            # they rotate through the pace line in a cyclical manner. The modulo operation 
            # handles the wrap-around, and the addition of 1 converts the result to a 1-based index.
            position = (k + n - j - 1) % n + 1
            if j < min_length:
                duration = pull_durations[j]
                speed = pull_speeds_kph[j]
                workunit = RiderWorkAssignmentItem(position=position, duration=duration, speed=speed)
            else:
                workunit = RiderWorkAssignmentItem(position=position)
            workunits.append(workunit)
        rider_workunits[riders[k - 1]] = workunits
    return rider_workunits


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    def log_results_work_assignments(test_description: str, result: Dict[ZsunRiderItem, List[RiderWorkAssignmentItem]], logger: logging.Logger) -> None:
        from tabulate import tabulate

        table = []
        for rider, assignments in result.items():
            for assignment in assignments:
                table.append([
                    rider.name, 
                    assignment.position, 
                    assignment.duration, 
                    assignment.speed
                ])

        headers = [
            "Rider", 
            "Position", 
            "Duration (sec)", 
            "Speed (kph)"
        ]
        logger.info(f"{test_description}:\n" + tabulate(table, headers=headers, tablefmt="plain"))

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

    log_results_work_assignments("Example riders",work_assignments, logger)

if __name__ == "__main__":
    main()


