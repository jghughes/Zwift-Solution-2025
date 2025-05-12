from typing import List
from zsun_rider_item import ZsunRiderItem
from computation_classes import *

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

    The resulting pattern for n riders is as follows:

        pos     strength
        1       1 (strongest)
        2       3
        3       5
        ...     ...
        n-2     6
        n-1     4
        n       2 (second strongest)

    Args:
        riders (List[ZsunRiderItem]): The list of riders to be arranged.

    Returns:
        List[ZsunRiderItem]: The list of riders arranged in the optimal interleaved order.
    """
    # Step 1: Calculate the strength of each rider and sort them in descending order
    sorted_riders = sorted(riders, key=lambda rider: rider.calculate_strength(), reverse=True)

    # Step 2: Interleave the riders
    optimal_order : List[ZsunRiderItem] = []
    left = 0  # Pointer for the front of the list
    right = len(sorted_riders) - 1  # Pointer for the back of the list

    while left <= right:
        if left == right:
            # If there's only one rider left, add them to the list
            optimal_order.append(sorted_riders[left])
        else:
            # Add the strongest remaining rider to the front
            optimal_order.append(sorted_riders[left])
            # Add the next strongest remaining rider to the back
            optimal_order.append(sorted_riders[right])
        left += 1
        right -= 1

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
        ZsunRiderItem.Config.json_schema_extra["davek"],
        ZsunRiderItem.Config.json_schema_extra["huskyc"],
        ZsunRiderItem.Config.json_schema_extra["scottm"],
        ZsunRiderItem.Config.json_schema_extra["johnh"],
        ZsunRiderItem.Config.json_schema_extra["joshn"],
    ]

    # Convert example data to ZsunRiderItem instances
    riders = [
        ZsunRiderItem.from_dataTransferObject(ZsunRiderItem.create(**data))
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


if __name__ == "__main__":
    main()