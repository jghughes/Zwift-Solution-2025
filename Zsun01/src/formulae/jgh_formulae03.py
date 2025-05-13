from typing import List, Tuple
from zsun_rider_item import ZsunRiderItem
from zsun_rider_dto import ZsunRiderDTO
from computation_classes import *


def deselect_weaker_riders(riders: List[ZsunRiderItem]) -> Tuple[List[ZsunRiderItem], List[ZsunRiderItem]]:
    """
    Filter the team into two groups: stronger and weaker riders.
    The threshold is the max speed at one hour watts among all riders.
    Riders with speed at 1 minute pull watts >= threshold are strong, others are weak.
    Both lists are sorted in descending order of strength.
    """
    if not riders:
        return [], []

    # Step 1: Calculate speed at one hour watts for each rider
    speeds_one_hour: List[float] = [rider.calculate_speed_at_one_hour_watts() for rider in riders]

    # Step 2: Determine the threshold (max speed at one hour watts)
    threshold: float = max(speeds_one_hour)

    # Step 3: Calculate speed at 1minute pull watts for each rider
    speed_1min: List[Tuple[ZsunRiderItem, float]] = [
        (rider, rider.calculate_speed_at_1_minute_pull_watts()) for rider in riders
    ]

    # Step 4: Filter into strong and weak groups
    strong: List[ZsunRiderItem] = [rider for rider, s in speed_1min if s >= threshold]
    weak: List[ZsunRiderItem] = [rider for rider, s in speed_1min if s < threshold]

    # Step 5: Sort both lists in descending order of speed
    strong_sorted: List[ZsunRiderItem] = sorted(strong, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True)
    weak_sorted: List[ZsunRiderItem] = sorted(weak, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True)


    # # Step 6: determine a threshold which is the slowest speed of the strong group, i.e. the last rider in the strong group 
    # if strong_sorted:
    #     threshold = strong_sorted[-1].calculate_speed_at_1_minute_pull_watts()

    # # Step 7: promote riders from the weak group to the strong group if they are faster than the slowest rider in the strong group
    # for rider in weak_sorted:
    #     if rider.calculate_speed_at_1_minute_pull_watts() > threshold:
    #         strong_sorted.append(rider)
    #         weak_sorted.remove(rider)

    # # Step 8: Sort the strong group again after promotion
    # strong_sorted = sorted(strong_sorted, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True)
    # weak_sorted = sorted(weak_sorted, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True)

    return strong_sorted, weak_sorted


def arrange_riders_in_optimal_order(riders: List[ZsunRiderItem]) -> List[ZsunRiderItem]:
    """
    Arrange the riders in an optimal order based on their strength metric.

    Riders are ranked according to their strength, from strongest to weakest. 
    The strongest rider is ranked 1, and the weakest rider is ranked n. 
    The strength of a rider is determined by the value returned from the 
    `ZsunRiderItem.calculate_strength()` method.

    To arrange the riders in optimal order, the riders are interleaved as follows:
    - The strongest rider is placed at the front (position 1).
    - The second strongest rider is placed at the back (position n).
    - The third strongest rider is placed behind the front (position 2).
    - The fourth strongest rider is placed ahead of the second strongest (position n-1).
    - This pattern continues until all riders are placed.

    Args:
        riders (List[ZsunRiderItem]): The list of riders to be arranged.

    Returns:
        List[ZsunRiderItem]: The list of riders arranged in the optimal interleaved order.
    """
    # Step 1: Calculate the strength of each rider and sort them in descending order
    sorted_riders = sorted(riders, key=lambda rider: rider.calculate_strength(), reverse=True)

    # Step 2: Create an empty list to hold the optimal order
    n = len(sorted_riders)
    optimal_order: List[ZsunRiderItem] = [None] * n  # type: ignore

    # Step 3: Fill front, 2nd, 3rd, ... (odd positions) with 1st, 3rd, 5th, ...
    front_idx = 0
    for i in range(0, n, 2):
        optimal_order[front_idx] = sorted_riders[i]
        front_idx += 1

    # Step 4: Fill back, 2nd last, ... (even positions from end) with 2nd, 4th, 6th, ... in reverse
    back_idx = n - 1
    for i in range(1, n, 2):
        optimal_order[back_idx] = sorted_riders[i]
        back_idx -= 1

    return optimal_order

def main():
    import logging
    from jgh_logging import jgh_configure_logging
    from tabulate import tabulate
    from zsun_rider_item import ZsunRiderItem
    from jgh_formulae03 import arrange_riders_in_optimal_order

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Example: Instantiate riders using the Config class
    example_riders_data = [
        # ZsunRiderItem.Config.json_schema_extra["davek"],
        ZsunRiderItem.Config.json_schema_extra["huskyc"],
        ZsunRiderItem.Config.json_schema_extra["scottm"],
        ZsunRiderItem.Config.json_schema_extra["johnh"],
        ZsunRiderItem.Config.json_schema_extra["joshn"],
        ZsunRiderItem.Config.json_schema_extra["brent"],
        ZsunRiderItem.Config.json_schema_extra["coryc"],
    ]


    # Convert example data to ZsunRiderItem instances
    riders = [
        ZsunRiderItem.from_dataTransferObject(ZsunRiderDTO.model_validate(data))
        for data in example_riders_data
    ]

    # Log the original list of riders
    logger.info("\nOriginal list of riders:")
    table = [[rider.name, rider.calculate_strength()] for rider in riders]
    logger.info("\n" + tabulate(table, headers=["Rider", "Strength"], tablefmt="simple"))

    # Arrange riders in optimal order
    optimal_order = arrange_riders_in_optimal_order(riders)

    # Log the arranged list of riders
    logger.info("\nRiders arranged in optimal order:")
    table = [[i + 1, rider.name, rider.calculate_strength()] for i, rider in enumerate(optimal_order)]
    logger.info("\n" + tabulate(table, headers=["Position", "Rider", "Strength"], tablefmt="simple"))

def main2():
    import logging
    from jgh_logging import jgh_configure_logging
    from tabulate import tabulate
    from zsun_rider_item import ZsunRiderItem
    from zsun_rider_dto import ZsunRiderDTO
    from jgh_formulae03 import deselect_weaker_riders

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Example: Instantiate riders using the Config class
    example_riders_data = [
        ZsunRiderItem.Config.json_schema_extra["meridithl"],
        ZsunRiderItem.Config.json_schema_extra["melissaw"],
        ZsunRiderItem.Config.json_schema_extra["richardm"],
        # ZsunRiderItem.Config.json_schema_extra["timr"],
        ZsunRiderItem.Config.json_schema_extra["davek"],
        ZsunRiderItem.Config.json_schema_extra["huskyc"],
        ZsunRiderItem.Config.json_schema_extra["scottm"],
        ZsunRiderItem.Config.json_schema_extra["johnh"],
        ZsunRiderItem.Config.json_schema_extra["joshn"],
        ZsunRiderItem.Config.json_schema_extra["brent"],
        ZsunRiderItem.Config.json_schema_extra["coryc"],
        ZsunRiderItem.Config.json_schema_extra["davide"],
    ]
    # Convert example data to ZsunRiderItem instances
    riders = [
        ZsunRiderItem.from_dataTransferObject(ZsunRiderDTO.model_validate(data))
        for data in example_riders_data
    ]

    # Log the original list of riders
    logger.info("\nOriginal list of riders:")
    table = [
        [
            rider.name,
            rider.calculate_strength(),
            rider.calculate_speed_at_one_hour_watts(),
            rider.calculate_speed_at_1_minute_pull_watts(),
        ]
        for rider in riders
    ]
    logger.info(
        "\n"
        + tabulate(
            table,
            headers=[
                "Rider",
                "Strength",
                "Speed@1hr(w)",
                "Speed@1min(w)",
            ],
            tablefmt="simple",
        )
    )

    # Deselect weaker riders
    strong, weak = deselect_weaker_riders(riders)

    # Log the strong group
    logger.info("\nStrong group:")
    table = [
        [
            rider.name,
            rider.calculate_strength(),
            rider.calculate_speed_at_one_hour_watts(),
            rider.calculate_speed_at_1_minute_pull_watts(),
        ]
        for rider in strong
    ]
    logger.info(
        "\n"
        + tabulate(
            table,
            headers=[
                "Rider",
                "Strength",
                "Speed@1hr(w)",
                "Speed@1min(w)",
            ],
            tablefmt="simple",
        )
    )
    # Log the weak group
    logger.info("\nWeak group:")
    table = [
        [
            rider.name,
            rider.calculate_strength(),
            rider.calculate_speed_at_one_hour_watts(),
            rider.calculate_speed_at_1_minute_pull_watts(),
        ]
        for rider in weak
    ]
    logger.info(
        "\n"
        + tabulate(
            table,
            headers=[
                "Rider",
                "Strength",
                "Speed@1hr(w)",
                "Speed@1min(w)",
            ],
            tablefmt="simple",
        )
    )



if __name__ == "__main__":
    # main()    
    main2()