from typing import List, Union, DefaultDict, Tuple
from jgh_formatting import format_number_1dp, format_number_comma_separators, format_duration_hms, truncate 
from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem
from handy_utilities import read_dict_of_zsunriderItems, log_multiline
from repository_of_teams import get_team_riderIDs
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import populate_pullplan_displayobjects, log_concise_pullplan_displayobjects, log_concise_pullplan_displayobjectsV2
from jgh_formulae08 import (
    calculate_lower_bound_pull_speed, 
    calculate_lower_bound_speed_at_one_hour_watts, 
    calculate_upper_bound_pull_speed, 
    calculate_upper_bound_speed_at_one_hour_watts,
    search_for_optimal_pull_plans_using_most_performant_algorithm,  
    make_a_single_pull_plan_complying_with_exertion_constraints
    )
from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging

def calculate_safe_binary_search_startpoint_to_locate_speeds(riders: List[ZsunRiderItem], verbose : bool, logger: logging.Logger) -> float:

    upper_bound_pull_rider, upper_bound_pull_rider_duration, upper_bound_pull_rider_speed = calculate_upper_bound_pull_speed(riders)
    upper_bound_1_hour_rider, _, upper_bound_1_hour_rider_speed = calculate_upper_bound_speed_at_one_hour_watts(riders)
    lower_bound_pull_rider, lower_bound_pull_rider_duration, lower_bound_pull_rider_speed = calculate_lower_bound_pull_speed(riders)
    lower_bound_1_hour_rider, _, lower_bound_1_hour_rider_speed = calculate_lower_bound_speed_at_one_hour_watts(riders)

    # Calculate safe_lowest_bound_speed required as the safe floor/start-point for iterating using binary search to determine speed limit
    safe_lowest_bound_speed = round(min(truncate(lower_bound_pull_rider_speed, 0), truncate(lower_bound_1_hour_rider_speed, 0)), 1)

    if not verbose:
        return safe_lowest_bound_speed

    message_lines = [
        "\nPACELINE PULL SPEED: upper and lower bounds: -\n",
        f"Upper bound pull        :  {round(upper_bound_pull_rider_speed)}kph @ {round(upper_bound_pull_rider.get_standard_30sec_pull_watts())}w "
        f"{format_number_1dp(upper_bound_pull_rider.get_standard_30sec_pull_watts()/upper_bound_pull_rider.weight_kg)}wkg by {upper_bound_pull_rider.name} "
        f"for a pull of {round(upper_bound_pull_rider_duration)} seconds.",
        f"Upper bound 1-hour pull :  {round(upper_bound_1_hour_rider_speed)}kph @ {round(upper_bound_1_hour_rider.get_1_hour_watts())}w "
        f"{format_number_1dp(upper_bound_1_hour_rider.get_1_hour_watts()/upper_bound_1_hour_rider.weight_kg)}wkg by {upper_bound_1_hour_rider.name}.",
        f"Lower bound pull        :  {round(lower_bound_pull_rider_speed)}kph @ {round(lower_bound_pull_rider.get_standard_4_minute_pull_watts())}w "
        f"{format_number_1dp(lower_bound_pull_rider.get_standard_4_minute_pull_watts()/lower_bound_pull_rider.weight_kg)}wkg by {lower_bound_pull_rider.name} "
        f"for a pull of {round(lower_bound_pull_rider_duration)} seconds.",
        f"Lower bound 1-hour pull :  {round(lower_bound_1_hour_rider_speed)}kph @ {round(lower_bound_1_hour_rider.get_1_hour_watts())}w "
        f"{format_number_1dp(lower_bound_1_hour_rider.get_1_hour_watts()/lower_bound_1_hour_rider.weight_kg)}wkg by {lower_bound_1_hour_rider.name}."
    ]

    log_multiline(logger, message_lines)

    return safe_lowest_bound_speed


def log_summary_message(total_compute_iterations: int, total_num_of_all_conceivable_plans: int, compute_time : float, intensity_factor: float, logger: logging.Logger
) -> None:

    message_lines = [
        f"\nBrute report: did {format_number_comma_separators(total_compute_iterations)} iterations to evaluate {format_number_comma_separators(total_num_of_all_conceivable_plans)} alternative plans in {format_duration_hms(compute_time)}. IF capped at {round(100*intensity_factor)}% in this run.",
        "Intensity Factor is Normalized Power/one-hour power. zFTP metrics are displayed, but play no role in computations.",
        "Pull capacities are obtained from individual 90-day best power graphs on ZwiftPower.",
        "",
        "30 second pull capacity = best power for 3.5 minutes",
        "1 minute pull capacity  = best power for  5 minutes",
        "2 minute pull capacity  = best power for 12 minutes",
        "3 minute pull capacity  = best power for 15 minutes",
        "4 minute pull capacity  = best power for 20 minutes",
        "",
        "Riders with superior pull capacity are prioritised for longer pulls.",
        "The speed of the paceline is constant and does not vary from one rider to the next.",
        "The pull capacity of the slowest puller governs the speed, leaving room for upside.",
        "The circle of the paceline puts stronger riders around the outside and weaker riders in the middle.",
        "Based on data from Zwiftpower as at March/April 2025. Some ZSUN riders have more comprehensive data than others.\n\n",
    ]
    log_multiline(logger, message_lines)


from computation_classes import PullPlanComputationParams  # Add this import at the top

def show_simple_pull_plan(
    riders: List[ZsunRiderItem],
    simple_pull_period: float,
    safe_lowest_bound_speed: float,
    intensity_factor: float,
    logger: logging.Logger
):
    """
    Creates and logs a simple pull plan where all riders pull for the same duration and speed.
    """
    simplest_pull_duration_as_array = [simple_pull_period] * len(riders)
    safe_lowest_bound_speed_as_array = [safe_lowest_bound_speed] * len(riders)

    params = PullPlanComputationParams(
        riders_list                  =riders,
        standard_pull_periods_sec    =simplest_pull_duration_as_array,
        pull_speeds_kph              =safe_lowest_bound_speed_as_array,
        max_exertion_intensity_factor=intensity_factor
    )

    result = make_a_single_pull_plan_complying_with_exertion_constraints(params)
    simple_plan_line_items = result.rider_pull_plans
    simple_plan_halted_rider = result.limiting_rider

    if simple_plan_halted_rider is None:
        calculated_speed = 0.0
    else:
        calculated_speed = round(simple_plan_line_items[simple_plan_halted_rider].speed_kph, 1)

    plan_line_items_displayobjects = populate_pullplan_displayobjects(simple_plan_line_items)
    log_concise_pullplan_displayobjects(
        f"\nSIMPLE PULL-PLAN: {calculated_speed}kph. Same pulls for everybody. IF capped at {round(100*intensity_factor)}%.",
        plan_line_items_displayobjects,
        logger
    )

    return result

def show_two_optimized_pull_plans(
    riders: List[ZsunRiderItem],
    pull_periods: List[float],
    binary_search_parameter: float,
    intensity_factor: float,
    logger: logging.Logger
):
    """
    Runs the optimal pull plan search and logs the summary and details for both low dispersion and high speed plans.
    """
    params = PullPlanComputationParams(
        riders_list                     =riders,
        standard_pull_periods_sec       =pull_periods,
        pull_speeds_kph                 =[binary_search_parameter] * len(riders),
        max_exertion_intensity_factor   =intensity_factor
    )

    result = search_for_optimal_pull_plans_using_most_performant_algorithm(params)

    two_pull_plans = result.solutions
    total_num_of_all_conceivable_plans = result.total_num_of_all_pull_plan_period_schedules
    total_compute_iterations = result.total_compute_iterations_count
    compute_time = result.computational_time

    low_dispersion_plan = two_pull_plans[0]
    high_speed_plan = two_pull_plans[1]

    low_dispersion_plan_line_items = low_dispersion_plan.rider_pull_plans
    low_dispersion_halted_rider = low_dispersion_plan.limiting_rider
    high_speed_plan_line_items = high_speed_plan.rider_pull_plans
    high_speed_halted_rider = high_speed_plan.limiting_rider

    low_dispersion_plan_line_items_displayobjects = populate_pullplan_displayobjects(low_dispersion_plan_line_items)
    high_speed_plan_line_items_displayobjects = populate_pullplan_displayobjects(high_speed_plan_line_items)

    low_dispersion_plan_title = (
        f"\nBALANCED EFFORT PULL-PLAN: {round(low_dispersion_plan_line_items[low_dispersion_halted_rider].speed_kph,1)}kph. "
        f"IF capped at {round(100*intensity_factor)}%."
    )
    high_speed_plan_title = (
        f"\nTEMPO PULL-PLAN: {round(high_speed_plan_line_items[high_speed_halted_rider].speed_kph,1)}kph. "
        f"IF capped at {round(100*intensity_factor)}%."
    )

    log_concise_pullplan_displayobjects(low_dispersion_plan_title, low_dispersion_plan_line_items_displayobjects, logger)
    log_concise_pullplan_displayobjects(high_speed_plan_title, high_speed_plan_line_items_displayobjects, logger)

    log_summary_message(
        total_compute_iterations,
        total_num_of_all_conceivable_plans,
        compute_time,
        intensity_factor,
        logger,
    )

    return result


def main():
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    # GET READY

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders : list[ZsunRiderItem] = []

    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    binary_search_parameter = calculate_safe_binary_search_startpoint_to_locate_speeds(riders, True, logger)

    # MAKE A SIMPLE PULL PLAN AT LOW INTENSITY

    pull_period = 60.0
    intensity_factor = 0.80 
    show_simple_pull_plan(riders, pull_period, binary_search_parameter, intensity_factor, logger)

    # DO BRUTE-FORCE SEARCH FOR TWO DIFFERENTLY OPTIMAL PULL PLANS - ONE FOR LOW DISPERSION OF INTENSITY, ANOTHER FOR SPEED

    pull_periods = STANDARD_PULL_PERIODS_SEC
    intensity_factor = MAX_INTENSITY_FACTOR
    show_two_optimized_pull_plans(riders, pull_periods, binary_search_parameter, intensity_factor, logger)

if __name__ == "__main__":
    main()


