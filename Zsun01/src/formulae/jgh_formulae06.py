from typing import List, Tuple, DefaultDict
from collections import defaultdict
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
        rider_contribution.intensity_factor = rider_contribution.normalized_watts / rider.get_one_hour_watts() if rider.get_one_hour_watts() > 0 else 0.0

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
            round(z.p6_w), 
            round(z.p7_w), 
            round(z.p8_w), 
            round(z.average_watts), 
            round(z.normalized_watts), 
            z.effort_constraint_violation_reason if z.effort_constraint_violation_reason else ""
        ])
    headers = [
        "name", 
        "sec", 
        "p1", 
        "2", 
        "3", 
        "4", 
        "ave", 
        "NP", 
        "limit"
    ]
    logger.info(tabulate(table, headers=headers, tablefmt="simple", disable_numparse=True))


def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)
    from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae08 import insert_ex_post_facto_message_about_cause_of_top_speed_limit


    from handy_utilities import read_dict_of_zsunriderItems
    dict_of_zwiftrideritem = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    meredith_leubner : ZsunRiderItem = dict_of_zwiftrideritem['1707548'] # davek
    johnh : ZsunRiderItem = dict_of_zwiftrideritem['1884456'] # barryb
    matt_steeve : ZsunRiderItem = dict_of_zwiftrideritem['1024413'] # markb
    roland_segal : ZsunRiderItem = dict_of_zwiftrideritem['384442'] # richardm
    lynsey_segal : ZsunRiderItem = dict_of_zwiftrideritem['383480'] # lynseys
    melissa_warwick : ZsunRiderItem = dict_of_zwiftrideritem['1657744'] # joshn
    
    riders : list[ZsunRiderItem] = [meredith_leubner, johnh, matt_steeve, roland_segal, lynsey_segal, melissa_warwick]

    pull_speeds_kph = [38.8, 38.8,38.8, 38.8, 38.8, 38.8, 38.8, 38.8]
    pull_durations = [240.0, 120.0, 60.0, 30.0, 60.0, 180.0]

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    rider_contributions = populate_rider_contributions(dict_of_rider_exertions)


    log_rider_contributions(f"{len(riders)}-riders @38,8kph.", rider_contributions, logger)


if __name__ == "__main__":
    main()
