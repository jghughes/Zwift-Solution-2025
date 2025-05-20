from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunriderItems
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae06 import log_pull_plan
from jgh_formulae08 import fmtc, format_hms,  truncate, calculate_lower_bound_pull_speed, calculate_lower_bound_speed_at_one_hour_watts, calculate_upper_bound_pull_speed, calculate_upper_bound_speed_at_one_hour_watts, make_a_pull_plan_with_a_sensible_top_speed, search_for_optimal_pull_plans, permitted_pull_durations
from repository_of_teams import get_team_IDs

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

ZSUN01_BETEL_PROFILES_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"


def main():
    dict_of_zsunrideritems = read_dict_of_zsunriderItems(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    riderIDs = get_team_IDs("betel")

    riders : list[ZsunRiderItem] = []
    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    logger.info(f"\nPACELINE SPEED: upper and lower bounds: -\n")

    r01,r01_duration,r01_speed = calculate_upper_bound_pull_speed(riders)
    r02,r02_duration,r02_speed = calculate_upper_bound_speed_at_one_hour_watts(riders)
    logger.info(f"Fastest pull          :  {round(r01_speed)} kph @ {round(r01.get_permitted_30sec_pull_watts())} W ({round(r01.get_permitted_30sec_pull_watts()/r01.weight_kg, 1)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Fastest one hour pull :  {round(r02_speed)} kph @ {round(r02.get_1_hour_watts())} W ({round(r02.get_1_hour_watts()/r02.weight_kg, 1)} W/kg) by {r02.name}.")


    r01,r01_duration,r01_speed =calculate_lower_bound_pull_speed(riders)
    r02,r02_duration,r02_speed = calculate_lower_bound_speed_at_one_hour_watts(riders)
    logger.info(f"Slowest pull          :  {round(r01_speed)} kph @ {round(r01.get_permitted_4_minute_pull_watts())} W ({round(r01.get_permitted_4_minute_pull_watts()/r01.weight_kg)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Slowest one hour pull :  {round(r02_speed)} kph @ {round(r02.get_1_hour_watts())} W ({round(r02.get_1_hour_watts()/r02.weight_kg, 1)} W/kg) by {r02.name}.")

    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed,0),1)) # round to lowest 1 kph, as a float
    plain_vanilla_pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone for Simplest case execute as a team
    seed_speed_array = [lowest_bound_speed] * len(riders)

    iterations, rider_answer_items, halted_rider = make_a_pull_plan_with_a_sensible_top_speed(riders, plain_vanilla_pull_durations, seed_speed_array)
    log_pull_plan(f"\n\nSIMPLEST PLAN: {round(rider_answer_items[halted_rider].speed_kph)} kph", rider_answer_items, logger)

    (solutions, total_alternatives, total_iterations, compute_time) = search_for_optimal_pull_plans(riders, permitted_pull_durations, lowest_bound_speed)

    solution01, solution02 = solutions
    iterations, rider_answer_items, halted_rider = solution02
    log_pull_plan(f"\n\nFAIREST PLAN: {round(rider_answer_items[halted_rider].speed_kph)} kph", rider_answer_items, logger)
    iterations, rider_answer_items, halted_rider = solution01
    log_pull_plan(f"\n\nFASTEST PLAN: {round(rider_answer_items[halted_rider].speed_kph)} kph", rider_answer_items, logger)
    
    logger.info(f"\n\n\nReport: did {fmtc(total_iterations)} iterations to evaluate {fmtc(total_alternatives)} alternatives in {format_hms(compute_time)} \n\n")

if __name__ == "__main__":
    main()


