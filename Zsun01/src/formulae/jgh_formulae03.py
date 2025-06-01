from typing import List, Tuple
from zsun_rider_item import ZsunRiderItem
from jgh_formulae02 import calculate_speed_at_one_hour_watts, calculate_speed_at_standard_1_minute_pull_watts, calculate_speed_at_standard_2_minute_pull_watts
from jgh_formulae02 import calculate_speed_at_n_second_watts


def allocate_riders_to_groups(riders: List[ZsunRiderItem]) -> Tuple[List[ZsunRiderItem], List[ZsunRiderItem]]:
    if not riders:
        return [], []

    #sort riders according to 1 minute pull speed
    riders.sort(key=lambda r: calculate_speed_at_standard_2_minute_pull_watts(r), reverse=True)

    strong_riders: List[ZsunRiderItem] = []
    weak_riders: List[ZsunRiderItem] = []

    def allocate_to_appropriate_group(rider : ZsunRiderItem, current_size_of_strong_group : int)-> None:

        def calculate_fatigue_adjusted_pull_speed(rider : ZsunRiderItem, n_riders : int) -> float:
            if n_riders == 0:
                candidate_answer_kph = 0
            elif n_riders == 1:
                candidate_answer_kph = calculate_speed_at_n_second_watts(rider,3600)
            elif n_riders == 2:
                candidate_answer_kph = calculate_speed_at_n_second_watts(rider,1800)
            elif n_riders == 3:
                candidate_answer_kph = calculate_speed_at_n_second_watts(rider,1200)
            else:
                candidate_answer_kph = calculate_speed_at_n_second_watts(rider,900)

            return candidate_answer_kph

        if calculate_speed_at_standard_2_minute_pull_watts(rider) > calculate_fatigue_adjusted_pull_speed(riders[0], current_size_of_strong_group + 1):
            strong_riders.append(rider)
        else:
            weak_riders.append(rider)

    # allocate_to_group(rider, i) for rider in riders
    for i, rider in enumerate(riders):
        allocate_to_appropriate_group(rider, i)

    return strong_riders, weak_riders

def arrange_riders_in_optimal_order(riders: List[ZsunRiderItem]) -> List[ZsunRiderItem]:
    """
    Arrange the riders in an optimal order based on their strength metric.

    Riders are ranked according to their strength, from strongest to weakest. 
    The strongest rider is ranked 1, and the weakest rider is ranked n. 
    The strength of a rider is determined by the value returned from the 
    `ZsunRiderItem.get_strength_wkg()` method.

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
    sorted_riders = sorted(riders, key=lambda rider: rider.get_strength_wkg(), reverse=True)

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

def calculate_everything(riders: List[ZsunRiderItem]) -> Tuple[float, List[ZsunRiderItem], List[ZsunRiderItem]]:
    if not riders:
        return 0, [], []

    floor_speed_kph = min(calculate_speed_at_one_hour_watts(rider) for rider in riders) - 2.0 # arbitrary cushion. slowest rider of all

    group_of_pullers, group_of_not_pullers = allocate_riders_to_groups(riders)

    group_of_pullers = arrange_riders_in_optimal_order(group_of_pullers)
    group_of_not_pullers = arrange_riders_in_optimal_order(group_of_not_pullers)

    return floor_speed_kph, group_of_pullers, group_of_not_pullers 

def main():
    import logging
    from jgh_logging import jgh_configure_logging
    from tabulate import tabulate
    from zsun_rider_item import ZsunRiderItem
    from jgh_formulae03 import arrange_riders_in_optimal_order
    from zsun_rider_dto import ZsunRiderDTO


    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)


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
    table = [[rider.name, rider.get_strength_wkg()] for rider in riders]
    logger.info("\n" + tabulate(table, headers=["Rider", "Strength"], tablefmt="simple"))

    # Arrange riders in optimal order
    optimal_order = arrange_riders_in_optimal_order(riders)

    # Log the arranged list of riders
    logger.info("\nRiders arranged in optimal order:")
    table = [[i + 1, rider.name, rider.get_strength_wkg()] for i, rider in enumerate(optimal_order)]
    logger.info("\n" + tabulate(table, headers=["Position", "Rider", "Strength"], tablefmt="simple",disable_numparse=True))

def main2():
    import logging
    from jgh_logging import jgh_configure_logging
    from tabulate import tabulate
    from zsun_rider_item import ZsunRiderItem
    from zsun_rider_dto import ZsunRiderDTO
    from jgh_formulae03 import allocate_riders_to_groups

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)


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

    from zsun_rider_dto import ZsunRiderDTO

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
            rider.get_strength_wkg(),
            calculate_speed_at_one_hour_watts(rider),
            calculate_speed_at_standard_1_minute_pull_watts(rider),
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
    strong, weak = allocate_riders_to_groups(riders)

    # Log the strong group
    logger.info("\nStrong group:")
    table = [
        [
            rider.name,
            rider.get_strength_wkg(),
            calculate_speed_at_one_hour_watts(rider),
            calculate_speed_at_standard_1_minute_pull_watts(rider),
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
            rider.get_strength_wkg(),
            calculate_speed_at_one_hour_watts(rider),
            calculate_speed_at_standard_1_minute_pull_watts(rider),
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
    from jgh_formulae03 import calculate_everything

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)


    # Example: Instantiate riders using the Config class
    example_riders_data = [
        ZsunRiderItem.Config.json_schema_extra["meridithl"],
        ZsunRiderItem.Config.json_schema_extra["melissaw"],
        # ZsunRiderItem.Config.json_schema_extra["richardm"],
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

    def format_number_2sig(x):
        return f"{x:.3g}"

    # Table 1: All riders ranked by 2-minute speed
    riders_sorted = sorted(
        riders, key=lambda r: calculate_speed_at_standard_2_minute_pull_watts(r), reverse=True
    )
    table = [
        [
            rider.name,
            format_number_2sig(calculate_speed_at_standard_2_minute_pull_watts(rider)),
            format_number_2sig(rider.get_1_hour_watts() / rider.weight_kg),
            format_number_2sig(rider.get_standard_2_minute_pull_watts() / rider.weight_kg),
        ]
        for rider in riders_sorted
    ]
    logger.info(
        "\nAll riders ranked by 2-minute speed:\n"
        + tabulate(
            table,
            headers=[
                "Rider",
                "2-min Speed (kph)",
                "1hr Power/kg",
                "2min Power/kg",
            ],
            tablefmt="simple",
        )
    )

    # Use calculate_everything to get groups and floor speed
    floor_speed_kph, strong, weak = calculate_everything(riders)

    # Table 2: Strong group
    table = [
        [
            rider.name,
            format_number_2sig(calculate_speed_at_standard_2_minute_pull_watts(rider)),
            format_number_2sig(rider.get_1_hour_watts() / rider.weight_kg),
            format_number_2sig(rider.get_standard_2_minute_pull_watts() / rider.weight_kg),
        ]
        for rider in strong
    ]
    logger.info(
        "\nStrong group (by 2-min speed):\n"
        + tabulate(
            table,
            headers=[
                "Rider",
                "2-min Speed (kph)",
                "1hr Power/kg",
                "2min Power/kg",
            ],
            tablefmt="simple",
        )
    )

    # Table 3: Weak group
    table = [
        [
            rider.name,
            format_number_2sig(calculate_speed_at_standard_2_minute_pull_watts(rider)),
            format_number_2sig(rider.get_1_hour_watts() / rider.weight_kg),
            format_number_2sig(rider.get_standard_2_minute_pull_watts() / rider.weight_kg),
        ]
        for rider in weak
    ]
    logger.info(
        "\nWeak group (by 2-min speed):\n"
        + tabulate(
            table,
            headers=[
                "Rider",
                "2-min Speed (kph)",
                "1hr Power/kg",
                "2min Power/kg",
            ],
            tablefmt="simple",
        )
    )

    # Display the calculated floor_speed_kph
    logger.info(f"\nCalculated floor_speed_kph: {format_number_2sig(floor_speed_kph)} kph")

if __name__ == "__main__":
    main()    
    main2()
    main3()