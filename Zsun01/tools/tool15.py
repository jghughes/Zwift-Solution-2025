from jgh_formatting import format_number_2dp
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import log_pretty_paceline_solution_report, save_pretty_paceline_solution_as_html_file
from jgh_formulae08 import generate_groovy_paceline_solutions, generate_a_single_paceline_solution_complying_with_exertion_constraints, log_speed_bounds_of_exertion_constrained_paceline_solutions, log_workload_suffix_message
from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC, EXERTION_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem, RiderContributionDisplayObject


def main():
    # SET UP LOGGING
    import logging
    from jgh_logging import jgh_configure_logging
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
    computation_report_title = f"\nSIMPLE PULL-PLAN: {format_number_2dp(practice.calculated_average_speed_of_paceline_kph)}kph  IF capped at {round(100*practice.exertion_intensity_constraint_used)}%"
    log_pretty_paceline_solution_report(computation_report_title, RiderContributionDisplayObject.from_RiderContributionItems(practice.rider_contributions), logger)

    # DO BRUTE-FORCE SEARCH FOR TWO DIFFERENTLY OPTIMAL PULL PLANS - FOR BALANCED EXERTION INTENSITY, AND SPEED

    ingredients.sequence_of_pull_periods_sec = ARRAY_OF_STANDARD_PULL_PERIODS_SEC

    two_solutions_computation_report = generate_groovy_paceline_solutions(ingredients)

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


