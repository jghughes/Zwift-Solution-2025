from typing import List, Tuple
from zsun_rider_item import ZsunRiderItem
from zsun_rider_dto import ZsunRiderDTO
from computation_classes import *


def deselect_weaker_riders(riders: List[ZsunRiderItem]) -> Tuple[List[ZsunRiderItem], List[ZsunRiderItem]]:
    """
    Splits a team of riders into two groups: strong and weak, based on their
    speed at 1 minute pull watts.

    The process is as follows:
      1. Calculate each rider's speed at one hour watts.
      2. Set the threshold as the maximum speed at one hour watts among all
         riders.
      3. Riders with speed at 1 minute pull watts >= threshold are initially
         classified as strong; others as weak.
      4. Both groups are sorted in descending order of speed at 1 minute pull
         watts.
      5. The threshold is then updated to the slowest speed in the strong
         group.
      6. Any riders in the weak group with speed at 1 minute pull watts
         greater than this updated threshold are promoted to the strong group.
      7. Both groups are re-sorted in descending order of speed at 1 minute
         pull watts.

    Args:
        riders (List[ZsunRiderItem]): The list of riders to be evaluated.

    Returns:
        Tuple[List[ZsunRiderItem], List[ZsunRiderItem]]:
            - The first list contains the strong riders, sorted by speed at
              1 minute pull watts (descending).
            - The second list contains the weak riders, sorted by speed at
              1 minute pull watts (descending).

    Notes:
        - If the input list is empty, both returned lists will be empty.
        - The selection/deselection is dominantly influenced by the strongest
          rider's one hour speed.
        - Riders may be promoted from weak to strong if their 1 minute pull
          speed exceeds the slowest strong rider.
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


    # Step 6: determine a threshold which is the slowest speed of the strong group, i.e. the last rider in the strong group 
    if strong_sorted:
        threshold = strong_sorted[-1].calculate_speed_at_1_minute_pull_watts()

    # Step 7: promote riders from the weak group to the strong group if they are faster than the slowest rider in the strong group
    for rider in weak_sorted:
        if rider.calculate_speed_at_1_minute_pull_watts() > threshold:
            strong_sorted.append(rider)
            weak_sorted.remove(rider) 

    # Step 8: Sort the strong group again after promotion
    strong_sorted = sorted(strong_sorted, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True)
    weak_sorted = sorted(weak_sorted, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True)

    return strong_sorted, weak_sorted

def calculate_target_speed_of_paceline(riders: List[ZsunRiderItem]) -> float:
    """
    Determines the target speed of the paceline based on the governing rider.

    The process is as follows:
      1. Calculate each rider's speed at 1 minute pull watts and sort the team
         in descending order.
      2. If the number of riders (n) is 4 or fewer, the governing rider is the
         last rider in the sorted list. If n > 4, the governing rider is the
         4th rider (index 3) in the sorted list.
      3. Divide the team into strong and weak groups using
         deselect_weaker_riders(...).
      4. Determine if the governing rider is a member of the strong or weak
         group.
      5. If the governing rider is in the strong group, the target speed is
         their speed at 1 minute pull watts.
      6. If the governing rider is in the weak group, the target speed is
         calculated using their one hour watts and their index in the sorted
         list via calculate_speed_riding_in_the_paceline.

    Args:
        riders (List[ZsunRiderItem]): The list of riders to be evaluated.

    Returns:
        float: The target speed of the paceline in km/h.

    Raises:
        ValueError: If the input list of riders is empty.

    Notes:
        - The governing rider is determined by team size and sorted 1min pull
          speed.
        - The strong/weak group split is performed using
          deselect_weaker_riders.
        - The calculation method for the target speed depends on the governing
          rider's group membership.
    """
    if not riders:
        raise ValueError("Rider list cannot be empty.")

    # Step 1: Sort riders by speed at 1min pull watts (descending)
    sorted_riders = sorted(
        riders, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True
    )

    n = len(sorted_riders)

    # Step 2 & 3: Determine governing rider index
    if n <= 4:
        governing_index = n - 1  # 0-based index, last rider
    else:
        governing_index = 3  # 4th rider, 0-based

    governing_rider = sorted_riders[governing_index]

    # Step 4: Divide into strong and weak groups
    strong, weak = deselect_weaker_riders(sorted_riders)

    # Step 5: Determine group membership
    if governing_rider in strong:
        # Step 6a: If in strong group, return their 1min pull speed
        return governing_rider.calculate_speed_at_1_minute_pull_watts()
    else:
        # Step 6b: If in weak group, calculate paceline speed
        # Find the governing rider's index in the sorted list
        governing_rider_index = sorted_riders.index(governing_rider)
        return governing_rider.calculate_speed_riding_in_the_paceline(
            governing_rider.get_one_hour_watts(), governing_rider_index
        )

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

def main3():
    import logging
    from jgh_logging import jgh_configure_logging
    from tabulate import tabulate
    from zsun_rider_item import ZsunRiderItem
    from zsun_rider_dto import ZsunRiderDTO
    from jgh_formulae03 import calculate_target_speed_of_paceline, deselect_weaker_riders

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

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

    # Step 1: Sort by 1min pull speed
    sorted_riders = sorted(
        riders, key=lambda r: r.calculate_speed_at_1_minute_pull_watts(), reverse=True
    )

    # Log the sorted list
    logger.info("\nTeam sorted by Speed@1min(w):")
    table = [
        [
            i + 1,
            rider.name,
            rider.calculate_strength(),
            rider.calculate_speed_at_one_hour_watts(),
            rider.calculate_speed_at_1_minute_pull_watts(),
        ]
        for i, rider in enumerate(sorted_riders)
    ]
    logger.info(
        "\n"
        + tabulate(
            table,
            headers=[
                "Rank",
                "Rider",
                "Strength",
                "Speed@1hr(w)",
                "Speed@1min(w)",
            ],
            tablefmt="simple",
        )
    )

    n = len(sorted_riders)
    if n <= 4:
        governing_index = n - 1
    else:
        governing_index = 3
    governing_rider = sorted_riders[governing_index]

    # Step 4: Divide into strong and weak groups
    strong, weak = deselect_weaker_riders(sorted_riders)

    # Step 5: Determine group membership
    group = "strong" if governing_rider in strong else "weak"
    logger.info(f"\nGoverning rider: {governing_rider.name} (Rank {governing_index+1}, Group: {group})")

    # Step 6: Calculate target speed
    target_speed = calculate_target_speed_of_paceline(riders)
    logger.info(f"\nTarget speed of paceline: {target_speed:.2f} km/h")

    # Optionally, show which group each rider is in
    logger.info("\nStrong group:")
    table = [
        [
            rider.name,
            rider.calculate_speed_at_1_minute_pull_watts(),
        ]
        for rider in strong
    ]
    logger.info(
        "\n"
        + tabulate(
            table,
            headers=["Rider", "Speed@1min(w)"],
            tablefmt="simple",
        )
    )

    logger.info("\nWeak group:")
    table = [
        [
            rider.name,
            rider.calculate_speed_at_1_minute_pull_watts(),
        ]
        for rider in weak
    ]
    logger.info(
        "\n"
        + tabulate(
            table,
            headers=["Rider", "Speed@1min(w)"],
            tablefmt="simple",
        )
    )







if __name__ == "__main__":
    # main()    
    # main2()
    main3()