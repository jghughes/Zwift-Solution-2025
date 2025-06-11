from jgh_formatting import format_number_1dp, format_number_comma_separators, format_duration_hms, truncate 
from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import populate_ridercontribution_displayobjects, log_concise_ridercontribution_displayobjects
from jgh_formulae08 import calculate_lower_bound_paceline_speed, calculate_lower_bound_paceline_speed_at_one_hour_watts, calculate_upper_bound_paceline_speed, calculate_upper_bound_paceline_speed_at_one_hour_watts
from jgh_formulae08 import generate_paceline_rotation_solutions_using_parallel_workstealing,  compute_a_single_paceline_solution_complying_with_exertion_constraints
from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging

def main():
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders : list[ZsunRiderItem] = []
    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    logger.info(f"\nPACELINE PULL SPEED: upper and lower bounds: -\n")

    r01,r01_duration,r01_speed = calculate_upper_bound_paceline_speed(riders)
    r02,_,r02_speed = calculate_upper_bound_paceline_speed_at_one_hour_watts(riders)
    logger.info(f"Upper bound pull        :  {round(r01_speed)} kph @ {round(r01.get_standard_30sec_pull_watts())} W ({format_number_1dp(r01.get_standard_30sec_pull_watts()/r01.weight_kg)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Upper bound 1-hour pull :  {round(r02_speed)} kph @ {round(r02.get_one_hour_watts())} W ({format_number_1dp(r02.get_one_hour_watts()/r02.weight_kg)} W/kg) by {r02.name}.")

    r01,r01_duration,r01_speed = calculate_lower_bound_paceline_speed(riders)
    r02,_,r02_speed = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)
    logger.info(f"Lower bound pull        :  {round(r01_speed)} kph @ {round(r01.get_standard_4_minute_pull_watts())} W ({format_number_1dp(r01.get_standard_4_minute_pull_watts()/r01.weight_kg)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Lower bound 1-hour pull :  {round(r02_speed)} kph @ {round(r02.get_one_hour_watts())} W ({format_number_1dp(r02.get_one_hour_watts()/r02.weight_kg)} W/kg) by {r02.name}.")

    lowest_bound_speed = round(min(truncate(r01_speed, 0), truncate(r02_speed,0),1)) # round to lowest 1 kph, as a float
    simplest_pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone for Simplest case to execute as a team
    lowest_bound_speed_as_array = [lowest_bound_speed] * len(riders)

    _, plan_line_items, halted_rider = compute_a_single_paceline_solution_complying_with_exertion_constraints(riders, simplest_pull_durations, lowest_bound_speed_as_array, MAX_INTENSITY_FACTOR)
    plan_line_items_displayobjects = populate_ridercontribution_displayobjects(plan_line_items)
    log_concise_ridercontribution_displayobjects(f"\n\nSIMPLEST PLAN: {round(plan_line_items[halted_rider].speed_kph,1)} kph", plan_line_items_displayobjects, logger)

    (pull_plans, total_num_of_all_conceivable_plans, total_compute_iterations, compute_time) = generate_paceline_rotation_solutions_using_parallel_workstealing(riders, STANDARD_PULL_PERIODS_SEC, lowest_bound_speed, MAX_INTENSITY_FACTOR)

    plan01, plan02 = pull_plans
    _, plan_line_items, halted_rider = plan02
    plan_line_items_displayobjects = populate_ridercontribution_displayobjects(plan_line_items)
    log_concise_ridercontribution_displayobjects(f"\n\nFAIREST PLAN: {round(plan_line_items[halted_rider].speed_kph,1)} kph", plan_line_items_displayobjects, logger)
    _, plan_line_items, halted_rider = plan01
    plan_line_items_displayobjects = populate_ridercontribution_displayobjects(plan_line_items)
    log_concise_ridercontribution_displayobjects(f"\n\nFASTEST PLAN: {round(plan_line_items[halted_rider].speed_kph,1)} kph", plan_line_items_displayobjects, logger)
    
    logger.info(f"\n\n\nReport: did {format_number_comma_separators(total_compute_iterations)} iterations to evaluate {format_number_comma_separators(total_num_of_all_conceivable_plans)} alternatives in {format_duration_hms(compute_time)} \n\n")


    # --- Begin iterative weakest-rider removal process for FASTEST PLAN (plan01) ---
    original_fastest_speed = plan_line_items[halted_rider].speed_kph
    current_riders = riders.copy()
    removed_riders = []
    plan01_records = []
    speed_records = []
    halted_rider_records = []
    total_iterations = total_num_of_all_conceivable_plans
    total_alternatives = total_compute_iterations
    total_time = compute_time

    while len(current_riders) > 2:
        # Remove the weakest rider (halted_rider from last plan01)
        halted_rider_index = current_riders.index(halted_rider)
        removed_riders.append(current_riders[halted_rider_index])
        del current_riders[halted_rider_index]

        # Recompute the fastest plan for the reduced team
        (pull_plans, num_alternatives, num_iterations, compute_time) = generate_paceline_rotation_solutions_using_parallel_workstealing(
            current_riders, STANDARD_PULL_PERIODS_SEC, lowest_bound_speed, MAX_INTENSITY_FACTOR
        )
        plan01, plan02 = pull_plans
        _, plan_line_items, halted_rider = plan01

        # Record stats
        plan01_records.append(plan01)
        speed_records.append(plan_line_items[halted_rider].speed_kph)
        halted_rider_records.append(halted_rider)
        total_iterations += num_iterations
        total_alternatives += num_alternatives
        total_time += compute_time

    # Find the fastest plan among the new ones
    if not speed_records or max(speed_records) <= original_fastest_speed:
        logger.info(f"\nNo faster solution found by removing riders. Original fastest speed: {original_fastest_speed:.1f} kph.")
    else:
        idx = speed_records.index(max(speed_records))
        best_plan01 = plan01_records[idx]
        _, plan_line_items, halted_rider = best_plan01
        plan_line_items_displayobjects = populate_ridercontribution_displayobjects(plan_line_items)
        log_concise_ridercontribution_displayobjects(
            f"\n\nFASTEST PLAN PLUS: {round(plan_line_items[halted_rider].speed_kph,1)} kph",
            plan_line_items_displayobjects,
            logger
        )

    logger.info(f"\n\n\nFASTEST PLAN PLUS: {len(speed_records)} iterations, {format_number_comma_separators(total_iterations)} total iterations, {format_number_comma_separators(total_alternatives)} alternatives, {format_duration_hms(total_time)} compute time.\n\n")
















if __name__ == "__main__":
    main()


