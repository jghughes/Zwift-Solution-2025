from typing import List
from jgh_formatting import format_number_1dp, format_number_2dp, format_number_comma_separators, format_pretty_duration_hms
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem, RiderContributionDisplayObject
from handy_utilities import read_dict_of_zsunriderItems, log_multiline
from repository_of_teams import get_team_riderIDs
from jgh_formulae02 import calculate_lower_bound_paceline_speed, calculate_lower_bound_paceline_speed_at_one_hour_watts, calculate_upper_bound_paceline_speed, calculate_upper_bound_paceline_speed_at_one_hour_watts, calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import log_pretty_paceline_solution_report, save_pretty_paceline_solution_as_html_file
from jgh_formulae08 import generate_two_groovy_paceline_solutions, generate_a_single_paceline_solution_complying_with_exertion_constraints 
from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC, EXERTION_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

import logging
from jgh_logging import jgh_configure_logging


def log_speed_bounds_of_exertion_constrained_paceline_solutions(riders: List[ZsunRiderItem], logger: logging.Logger):

    upper_bound_pull_rider, upper_bound_pull_rider_duration, upper_bound_pull_rider_speed   = calculate_upper_bound_paceline_speed(riders)
    upper_bound_1_hour_rider, _, upper_bound_1_hour_rider_speed                             = calculate_upper_bound_paceline_speed_at_one_hour_watts(riders)
    lower_bound_pull_rider, lower_bound_pull_rider_duration, lower_bound_pull_rider_speed   = calculate_lower_bound_paceline_speed(riders)
    lower_bound_1_hour_rider, _, lower_bound_1_hour_rider_speed                             = calculate_lower_bound_paceline_speed_at_one_hour_watts(riders)

    message_lines = [
        "\nPACELINE PULL SPEED: upper and lower bounds of exertion-constrained pull plans:\n",
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


def log_workload_suffix_message(total_compute_iterations_done: int, total_num_of_all_conceivable_plans: int, compute_time : float, logger: logging.Logger
) -> None:

    message_lines = [
        f"\nBrute report: did {format_number_comma_separators(total_compute_iterations_done)} iterations to evaluate {format_number_comma_separators(total_num_of_all_conceivable_plans)} alternative plans in {format_pretty_duration_hms(compute_time)}.",
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
        "The paceline puts weaker riders in the middle.",
        "Based on data from Zwiftpower as at March/April 2025. Some ZSUN riders have more comprehensive data than others.\n\n",
    ]
    log_multiline(logger, message_lines)


def main():

    # SET UP LOGGING

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    # GET THE DATA READY

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("betel")

    riders : list[ZsunRiderItem] = []

    for riderID in riderIDs:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    # SET UP PACELINE INGREDIENTS

    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders, logger)

    ingredients = PacelineIngredientsItem(
        riders_list                   = riders,
        pull_speeds_kph               = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        max_exertion_intensity_factor = EXERTION_INTENSITY_FACTOR
    )

    # DO A SIMPLE PULL PLAN - FOR PRACTICING TECHNIQUE

    ingredients.sequence_of_pull_periods_sec = [30.0] * len(riders)

    practice = generate_a_single_paceline_solution_complying_with_exertion_constraints(ingredients)
    computation_report_title = f"\nPRACTICE PULL-PLAN: {format_number_2dp(practice.calculated_average_speed_of_paceline_kph)}kph  IF capped at {round(100*practice.exertion_intensity_constraint_used)}%"
    log_pretty_paceline_solution_report(computation_report_title, RiderContributionDisplayObject.from_RiderContributionItems(practice.rider_contributions), logger)

    # DO BRUTE-FORCE SEARCH FOR TWO DIFFERENTLY OPTIMAL PULL PLANS - FOR BALANCED EXERTION INTENSITY, AND SPEED

    ingredients.sequence_of_pull_periods_sec = ARRAY_OF_STANDARD_PULL_PERIODS_SEC

    two_solutions_computation_report = generate_two_groovy_paceline_solutions(ingredients)

    balanced = two_solutions_computation_report.solutions[0]
    balanced_title = f"\nBALANCED-EFFORT PULL-PLAN: {format_number_2dp(balanced.calculated_average_speed_of_paceline_kph)}kph  IF capped at {round(100*balanced.exertion_intensity_constraint_used)}%"
    log_pretty_paceline_solution_report(balanced_title,  RiderContributionDisplayObject.from_RiderContributionItems(balanced.rider_contributions), logger)

    tempo = two_solutions_computation_report.solutions[1]
    tempo_title = f"\nTEMPO PULL-PLAN: {format_number_2dp(tempo.calculated_average_speed_of_paceline_kph)}kph  IF capped at {round(100*tempo.exertion_intensity_constraint_used)}%"
    log_pretty_paceline_solution_report(tempo_title, RiderContributionDisplayObject.from_RiderContributionItems(tempo.rider_contributions), logger)

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(two_solutions_computation_report.total_compute_iterations_performed, two_solutions_computation_report.total_pull_sequences_examined, two_solutions_computation_report.computational_time, logger,)

    # SAVE A SOLUTION AS HTML FILE

    save_pretty_paceline_solution_as_html_file(balanced_title, RiderContributionDisplayObject.from_RiderContributionItems(balanced.rider_contributions), logger)



if __name__ == "__main__":
    main()


