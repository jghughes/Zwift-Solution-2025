from typing import List, Tuple, DefaultDict
from collections import defaultdict
from jgh_number import safe_divide
from zsun_rider_dto import ZsunRiderDTO
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderExertionItem, RiderContributionItem
from jgh_formulae02 import calculate_overall_average_watts, calculate_overall_normalized_watts

import logging



def populate_rider_contributions(riders: DefaultDict[ZsunRiderItem, List[RiderExertionItem]], max_exertion_intensity_factor : float ) -> DefaultDict[ZsunRiderItem, RiderContributionItem]:

    def extract_watts_sequentially(exertions: List[RiderExertionItem]) -> Tuple[float, float, float, float, float, float, float, float]:
        if not exertions:
            return 0, 0, 0, 0, 0,0,0,0

        dict_wattages = {exertion.current_location_in_paceline: exertion.wattage for exertion in exertions}

        p1 = dict_wattages.get(1, 0)
        p2 = dict_wattages.get(2, 0)
        p3 = dict_wattages.get(3, 0)
        p4 = dict_wattages.get(4, 0)
        p5 = dict_wattages.get(5, 0)
        p6 = dict_wattages.get(6, 0)
        p7 = dict_wattages.get(7, 0)
        p8 = dict_wattages.get(8, 0)

        return p1, p2, p3, p4, p5, p6, p7, p8

    def extract_pull_metrics(exertions: List[RiderExertionItem]) -> Tuple[float, float]:
        if not exertions:
            return 0, 0

        p1_speed_kph = 0
        p1_duration : float = 0

        dict_positions = {exertion.current_location_in_paceline: exertion for exertion in exertions}

        pull_exertion = dict_positions.get(1, None)

        if pull_exertion is None:
            return 0, 0

        p1_speed_kph = pull_exertion.speed_kph
        p1_duration = pull_exertion.duration

        return p1_speed_kph, p1_duration
 
    answer : DefaultDict[ZsunRiderItem, RiderContributionItem] = defaultdict(RiderContributionItem)

    for rider, exertions in riders.items():
        p1w, p2w, p3w, p4w, p5w, p6w, p7w, p8w = extract_watts_sequentially(exertions)
        p1_speed_kph, p1_duration = extract_pull_metrics(exertions)
        rider_contribution = RiderContributionItem(
            speed_kph           = p1_speed_kph,
            p1_duration         = p1_duration,
            p1_w                = p1w,
            p2_w                = p2w,
            p3_w                = p3w,
            p4_w                = p4w,
            p5_w                = p5w,
            p6_w                = p6w,
            p7_w                = p7w,
            p8_w                = p8w,
            average_watts       = calculate_overall_average_watts(exertions),
            normalized_watts    = calculate_overall_normalized_watts(exertions),
        )
        rider_contribution.intensity_factor = safe_divide(rider_contribution.normalized_watts,rider.get_one_hour_watts())

        if rider_contribution.p1_duration != 0.0:
            msg = ""
            if rider_contribution.intensity_factor >= max_exertion_intensity_factor:
                msg += f" IF>{round(100*max_exertion_intensity_factor)}%"

            if rider_contribution.p1_w >= rider.get_standard_pull_watts(rider_contribution.p1_duration):
                msg += " pull>max W"

            rider_contribution.effort_constraint_violation_reason = msg

        answer[rider] = rider_contribution

    return answer


def log_rider_contributions(test_description: str, result: DefaultDict[ZsunRiderItem, RiderContributionItem], logger: logging.Logger) -> None:
    from tabulate import tabulate
    logger.info(test_description)
    table = []
    for rider, z in result.items():
        table.append([
            rider.name, 
            z.p1_duration,
            round(z.p1_w), 
            round(z.p2_w), 
            round(z.p3_w), 
            round(z.p4_w), 
            round(z.p5_w), 
            # round(z.p6_w), 
            # round(z.p7_w), 
            # round(z.p8_w), 
            round(z.average_watts), 
            round(z.normalized_watts), 
            z.effort_constraint_violation_reason
        ])
    headers = [
        "name", 
        "p1_sec", 
        "p1_w", 
        "p2", 
        "p3", 
        "p4", 
        "p5", 
        "ave_w", 
        "NP_w", 
        "limit"
    ]
    logger.info(tabulate(table, headers=headers, tablefmt="simple", disable_numparse=True))


def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions

    # Example: Instantiate riders using the Config class
    example_riders_data = [
        # ZsunRiderItem.Config.json_schema_extra["meridithl"],
        ZsunRiderItem.Config.json_schema_extra["melissaw"],
        ZsunRiderItem.Config.json_schema_extra["richardm"],
        # ZsunRiderItem.Config.json_schema_extra["davek"],
        # ZsunRiderItem.Config.json_schema_extra["huskyc"],
        # ZsunRiderItem.Config.json_schema_extra["scottm"],
        ZsunRiderItem.Config.json_schema_extra["johnh"],
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


    pull_durations = [120.0, 0.0, 30.0] # duration array MUST be same len as riders (or longer), and the sequence MUST match the rider order in the paceline
    pull_speeds_kph = [40.0] * len(riders)
    pull_speed = 40.0  # Example speed in kph
    pull_speeds_kph = [pull_speed] * len(riders)

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    rider_contributions = populate_rider_contributions(dict_of_rider_exertions, 0.95)

    log_rider_contributions(f"{len(riders)} riders @ {pull_speed}kph\n", rider_contributions, logger)


if __name__ == "__main__":
    main()
