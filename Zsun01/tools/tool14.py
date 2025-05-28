from jgh_formatting import format_number_1dp, format_number_comma_separators, format_duration_hms, truncate 
from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import populate_pullplan_displayobjects, log_concise_pullplan_displayobjects
from jgh_formulae08 import calculate_lower_bound_pull_speed, calculate_lower_bound_speed_at_one_hour_watts, calculate_upper_bound_pull_speed, calculate_upper_bound_speed_at_one_hour_watts
from jgh_formulae08 import make_a_pull_plan_complying_with_exertion_constraints
from jgh_formulae09 import search_for_optimal_pull_plans_concurrently_with_chunking
from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging



def main():
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders : list[ZsunRiderItem] = []
    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    logger.info(f"\nPACELINE PULL SPEED: upper and lower bounds: -\n")

    r01,r01_duration,r01_speed = calculate_upper_bound_pull_speed(riders)
    r02,_,r02_speed = calculate_upper_bound_speed_at_one_hour_watts(riders)
    logger.info(f"Upper bound pull        :  {round(r01_speed)} kph @ {round(r01.get_standard_30sec_pull_watts())} W ({format_number_1dp(r01.get_standard_30sec_pull_watts()/r01.weight_kg)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Upper bound 1-hour pull :  {round(r02_speed)} kph @ {round(r02.get_1_hour_watts())} W ({format_number_1dp(r02.get_1_hour_watts()/r02.weight_kg)} W/kg) by {r02.name}.")

    r01,r01_duration,r01_speed = calculate_lower_bound_pull_speed(riders)
    r02,_,r02_speed = calculate_lower_bound_speed_at_one_hour_watts(riders)
    logger.info(f"Lower bound pull        :  {round(r01_speed)} kph @ {round(r01.get_standard_4_minute_pull_watts())} W ({format_number_1dp(r01.get_standard_4_minute_pull_watts()/r01.weight_kg)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Lower bound 1-hour pull :  {round(r02_speed)} kph @ {round(r02.get_1_hour_watts())} W ({format_number_1dp(r02.get_1_hour_watts()/r02.weight_kg)} W/kg) by {r02.name}.")

    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed,0),1)) # round to lowest 1 kph, as a float
    simplest_pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone for Simplest case to execute as a team
    lowest_bound_speed_as_array = [lowest_bound_speed] * len(riders)

    _, plan_line_items, halted_rider = make_a_pull_plan_complying_with_exertion_constraints(riders, simplest_pull_durations, lowest_bound_speed_as_array, MAX_INTENSITY_FACTOR)
    plan_line_items_displayobjects = populate_pullplan_displayobjects(plan_line_items)
    log_concise_pullplan_displayobjects(f"\n\nSIMPLEST PLAN: {round(plan_line_items[halted_rider].speed_kph,1)} kph", plan_line_items_displayobjects, logger)

    (pull_plans, total_num_of_all_conceivable_plans, total_compute_iterations, compute_time) = search_for_optimal_pull_plans_concurrently_with_chunking(riders, STANDARD_PULL_PERIODS_SEC, lowest_bound_speed, MAX_INTENSITY_FACTOR, verbose=False)

    plan01, plan02 = pull_plans
    _, plan_line_items, halted_rider = plan02
    plan_line_items_displayobjects = populate_pullplan_displayobjects(plan_line_items)
    log_concise_pullplan_displayobjects(f"\n\nFAIREST PLAN: {round(plan_line_items[halted_rider].speed_kph,1)} kph", plan_line_items_displayobjects, logger)
    _, plan_line_items, halted_rider = plan01
    plan_line_items_displayobjects = populate_pullplan_displayobjects(plan_line_items)
    log_concise_pullplan_displayobjects(f"\n\nFASTEST PLAN: {round(plan_line_items[halted_rider].speed_kph,1)} kph", plan_line_items_displayobjects, logger)
    
    logger.info(f"\n\n\nReport: did {format_number_comma_separators(total_compute_iterations)} iterations to evaluate {format_number_comma_separators(total_num_of_all_conceivable_plans)} alternatives in {format_duration_hms(compute_time)} \n\n")

if __name__ == "__main__":
    main()


