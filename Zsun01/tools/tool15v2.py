from typing import List
from jgh_formatting import format_number_1dp, format_number_comma_separators, format_duration_hms, truncate 
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem
from handy_utilities import read_dict_of_zsunriderItems, log_multiline
from repository_of_teams import get_team_riderIDs
from jgh_formulae02 import calculate_lower_bound_paceline_speed, calculate_lower_bound_paceline_speed_at_one_hour_watts, calculate_upper_bound_paceline_speed, calculate_upper_bound_paceline_speed_at_one_hour_watts
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import (populate_rider_contribution_displayobjects, log_rider_contribution_displayobjectsV3, save_rider_contributions_as_html_file)
from jgh_formulae08v2 import generate_two_groovy_paceline_solutions, generate_a_single_paceline_solution_complying_with_exertion_constraints 
from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging

def calculate_safe_lowest_bound_speed_to_kick_off_binary_search_algorithm_kph(riders: List[ZsunRiderItem]) -> float:

    _, _, lower_bound_pull_rider_speed   = calculate_lower_bound_paceline_speed(riders)
    _, _, lower_bound_1_hour_rider_speed = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)

    safe_lowest_bound_speed = round(min(truncate(lower_bound_pull_rider_speed, 0), truncate(lower_bound_1_hour_rider_speed, 0)), 1)

    return safe_lowest_bound_speed


def show_safe_binary_search_startpoint_to_locate_speeds(riders: List[ZsunRiderItem], verbose : bool, logger: logging.Logger) -> float:

    upper_bound_pull_rider, upper_bound_pull_rider_duration, upper_bound_pull_rider_speed   = calculate_upper_bound_paceline_speed(riders)
    upper_bound_1_hour_rider, _, upper_bound_1_hour_rider_speed                             = calculate_upper_bound_paceline_speed_at_one_hour_watts(riders)
    lower_bound_pull_rider, lower_bound_pull_rider_duration, lower_bound_pull_rider_speed   = calculate_lower_bound_paceline_speed(riders)
    lower_bound_1_hour_rider, _, lower_bound_1_hour_rider_speed                             = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)

    # Calculate safe_lowest_bound_speed required as the safe floor/start-point for iterating using binary search to determine speed limit
    safe_lowest_bound_speed = round(min(truncate(lower_bound_pull_rider_speed, 0), truncate(lower_bound_1_hour_rider_speed, 0)), 1)

    if not verbose:
        return safe_lowest_bound_speed

    message_lines = [
        "\nPACELINE PULL SPEED: upper and lower bounds: -\n",
        f"Upper bound pull        :  {round(upper_bound_pull_rider_speed)}kph @ {round(upper_bound_pull_rider.get_standard_30sec_pull_watts())}w "
        f"{format_number_1dp(upper_bound_pull_rider.get_standard_30sec_pull_watts()/upper_bound_pull_rider.weight_kg)}wkg by {upper_bound_pull_rider.name} "
        f"for a pull of {round(upper_bound_pull_rider_duration)} seconds.",
        f"Upper bound 1-hour pull :  {round(upper_bound_1_hour_rider_speed)}kph @ {round(upper_bound_1_hour_rider.get_one_hour_watts())}w "
        f"{format_number_1dp(upper_bound_1_hour_rider.get_one_hour_watts()/upper_bound_1_hour_rider.weight_kg)}wkg by {upper_bound_1_hour_rider.name}.",
        f"Lower bound pull        :  {round(lower_bound_pull_rider_speed)}kph @ {round(lower_bound_pull_rider.get_standard_4_minute_pull_watts())}w "
        f"{format_number_1dp(lower_bound_pull_rider.get_standard_4_minute_pull_watts()/lower_bound_pull_rider.weight_kg)}wkg by {lower_bound_pull_rider.name} "
        f"for a pull of {round(lower_bound_pull_rider_duration)} seconds.",
        f"Lower bound 1-hour pull :  {round(lower_bound_1_hour_rider_speed)}kph @ {round(lower_bound_1_hour_rider.get_one_hour_watts())}w "
        f"{format_number_1dp(lower_bound_1_hour_rider.get_one_hour_watts()/lower_bound_1_hour_rider.weight_kg)}wkg by {lower_bound_1_hour_rider.name}."
    ]

    log_multiline(logger, message_lines)

    return safe_lowest_bound_speed


def show_summary_of_work_performed(total_compute_iterations_done: int, total_num_of_all_conceivable_plans: int, compute_time : float, intensity_factor: float, logger: logging.Logger
) -> None:

    message_lines = [
        f"\nBrute report: did {format_number_comma_separators(total_compute_iterations_done)} iterations to evaluate {format_number_comma_separators(total_num_of_all_conceivable_plans)} alternative plans in {format_duration_hms(compute_time)}. IF capped at {round(100*intensity_factor)}% in this run.",
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


def generate_and_show_simple_paceline_solution(riders: List[ZsunRiderItem], simple_pull_period: float, safe_lowest_bound_speed: float, intensity_factor: float, logger: logging.Logger):
    """
    Creates and logs a simple pull plan where all riders pull for the same duration and speed.
    """
    simplest_pull_duration_as_array = [simple_pull_period] * len(riders)
    safe_lowest_bound_speed_as_array = [safe_lowest_bound_speed] * len(riders)

    ingredients = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = simplest_pull_duration_as_array,
        pull_speeds_kph               = safe_lowest_bound_speed_as_array,
        max_exertion_intensity_factor = intensity_factor
    )

    simple_solution                     = generate_a_single_paceline_solution_complying_with_exertion_constraints(ingredients)
    simple_solution_rider_contributions = simple_solution.rider_contributions
    calculated_speed                    = round(simple_solution.average_speed_of_paceline_kph, 1)

    simple_solution_rider_contribution_displayobjects = populate_rider_contribution_displayobjects(simple_solution_rider_contributions)

    log_rider_contribution_displayobjectsV3(f"\nSIMPLE PULL-PLAN: {calculated_speed}kph. Same pulls for everybody. IF capped at {round(100*intensity_factor)}%.",
        simple_solution_rider_contribution_displayobjects,
        logger
    )

    return simple_solution


def generate_and_show_two_groovy_paceline_solutions(riders: List[ZsunRiderItem], pull_periods: List[float], seed_speed_kph: float, intensity_factor: float, logger: logging.Logger
):
    """
    Runs the optimal pull plan generation and logs the summary and details for both low dispersion and high speed plans.
    """
    ingredients = PacelineIngredientsItem(
        riders_list                    = riders,
        sequence_of_pull_periods_sec   = pull_periods,
        pull_speeds_kph                = [seed_speed_kph] * len(riders),
        max_exertion_intensity_factor  = intensity_factor
    )

    groovy_solution_computation_outcome = generate_two_groovy_paceline_solutions(ingredients)

    list_of_groovy_solutions        = groovy_solution_computation_outcome.solutions
    total_solutions_examined        = groovy_solution_computation_outcome.total_pull_sequences_examined
    total_compute_iterations_done   = groovy_solution_computation_outcome.total_compute_iterations_performed
    compute_time                    = groovy_solution_computation_outcome.computational_time

    low_std_deviation_solution = list_of_groovy_solutions[0]
    fast_speed_solution        = list_of_groovy_solutions[1]

    low_std_deviation_solution_rider_contributions  = low_std_deviation_solution.rider_contributions
    fast_speed_solution_rider_contributions         = fast_speed_solution.rider_contributions

    low_std_deviation_solution_kph = round(low_std_deviation_solution.average_speed_of_paceline_kph, 1)
    fast_speed_solution_kph       = round(fast_speed_solution.average_speed_of_paceline_kph, 1)


    low_std_deviation_solution_rider_contribution_displayobjects = populate_rider_contribution_displayobjects(low_std_deviation_solution_rider_contributions)
    fast_speed_solution_rider_contribution_displayobjects        = populate_rider_contribution_displayobjects(fast_speed_solution_rider_contributions)

    low_std_deviation_solution_title = f"\nBALANCED EFFORT PULL-PLAN: {low_std_deviation_solution_kph}kph  IF capped at {round(100*intensity_factor)}%."
    fast_speed_solution_title = f"\nTEMPO PULL-PLAN: {fast_speed_solution_kph}kph  IF capped at {round(100*intensity_factor)}%."

    log_rider_contribution_displayobjectsV3(low_std_deviation_solution_title, low_std_deviation_solution_rider_contribution_displayobjects, logger)
    log_rider_contribution_displayobjectsV3(fast_speed_solution_title, fast_speed_solution_rider_contribution_displayobjects, logger)

    show_summary_of_work_performed(total_compute_iterations_done, total_solutions_examined, compute_time, intensity_factor, logger,)

    save_rider_contributions_as_html_file(low_std_deviation_solution_title, low_std_deviation_solution_rider_contribution_displayobjects, logger)

    return groovy_solution_computation_outcome


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

    seed_speed_kph = calculate_safe_lowest_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)

    # MAKE A SIMPLE PULL PLAN AT LOW INTENSITY

    pull_period = 60.0
    intensity_factor = 0.80 
    generate_and_show_simple_paceline_solution(riders, pull_period, seed_speed_kph, intensity_factor, logger)

    # DO BRUTE-FORCE SEARCH FOR TWO DIFFERENTLY OPTIMAL PULL PLANS - ONE FOR LOW STD DEVIATION OF INTENSITY, ANOTHER FOR SPEED

    pull_periods = STANDARD_PULL_PERIODS_SEC
    intensity_factor = MAX_INTENSITY_FACTOR
    generate_and_show_two_groovy_paceline_solutions(riders, pull_periods, seed_speed_kph, intensity_factor, logger)


if __name__ == "__main__":
    main()


