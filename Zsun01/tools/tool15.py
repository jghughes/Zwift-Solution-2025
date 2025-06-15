from collections import defaultdict
from jgh_formatting import format_number_2dp, format_number_4dp
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae07 import log_pretty_paceline_solution_report, save_pretty_paceline_solution_as_html_file
from jgh_formulae08 import generate_ingenious_paceline_solutions, generate_a_single_paceline_solution_complying_with_exertion_constraints, log_speed_bounds_of_exertion_constrained_paceline_solutions, log_workload_suffix_message
from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC, EXERTION_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineComputationReport, PacelineIngredientsItem, RiderContributionDisplayObject, RiderContributionItem


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

    computation_report = generate_ingenious_paceline_solutions(ingredients)

    simple = computation_report.simple_solution if computation_report.simple_solution else PacelineComputationReport()
    balanced = computation_report.balanced_intensity_of_effort_solution if computation_report.balanced_intensity_of_effort_solution else PacelineComputationReport()
    tempo = computation_report.tempo_solution if computation_report.tempo_solution else PacelineComputationReport()
    drop = computation_report.drop_solution if computation_report.drop_solution else PacelineComputationReport()

    simple_kph = simple.calculated_average_speed_of_paceline_kph if simple else 0.0
    balanced_kph = balanced.calculated_average_speed_of_paceline_kph if balanced else 0.0
    tempo_kph = tempo.calculated_average_speed_of_paceline_kph if tempo else 0.0
    drop_kph = drop.calculated_average_speed_of_paceline_kph if drop else 0.0

    simple_intensity = round(100 * simple.exertion_intensity_constraint_used) if simple else None
    balanced_intensity = round(100 * balanced.exertion_intensity_constraint_used) if balanced else None
    tempo_intensity = round(100 * tempo.exertion_intensity_constraint_used) if tempo else None
    drop_intensity = round(100 * drop.exertion_intensity_constraint_used) if drop else None


    simple_contributions = (
        RiderContributionDisplayObject.from_RiderContributionItems(simple.rider_contributions)
        if simple and simple.rider_contributions
        else RiderContributionDisplayObject.from_RiderContributionItems(defaultdict(RiderContributionItem))
    )

    balanced_contributions = (
        RiderContributionDisplayObject.from_RiderContributionItems(balanced.rider_contributions)
        if balanced and balanced.rider_contributions
        else RiderContributionDisplayObject.from_RiderContributionItems(defaultdict(RiderContributionItem))
    )

    tempo_contributions = (
        RiderContributionDisplayObject.from_RiderContributionItems(tempo.rider_contributions)
        if tempo and tempo.rider_contributions
        else RiderContributionDisplayObject.from_RiderContributionItems(defaultdict(RiderContributionItem))
    )

    drop_contributions = (
        RiderContributionDisplayObject.from_RiderContributionItems(drop.rider_contributions)
        if drop and drop.rider_contributions
        else RiderContributionDisplayObject.from_RiderContributionItems(defaultdict(RiderContributionItem))
    )


    simple_title = f"\nSIMPLE PULL-PLAN: {format_number_4dp(simple_kph)}kph  IF capped at {simple_intensity}%"
    balanced_title = f"\nBALANCED-EFFORT PULL-PLAN: {format_number_4dp(balanced_kph)}kph  IF capped at {balanced_intensity}%"
    tempo_title = f"\nTEMPO PULL-PLAN: {format_number_4dp(tempo_kph)}kph  IF capped at {tempo_intensity}%"
    drop_title = f"\nDROP PULL-PLAN: {format_number_4dp(drop_kph)}kph  IF capped at {drop_intensity}%"

    log_pretty_paceline_solution_report(simple_title,  simple_contributions, logger)
    log_pretty_paceline_solution_report(balanced_title,  balanced_contributions, logger)
    log_pretty_paceline_solution_report(tempo_title, tempo_contributions, logger)
    log_pretty_paceline_solution_report(drop_title, drop_contributions, logger)

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(computation_report.total_compute_iterations_performed, computation_report.total_pull_sequences_examined, computation_report.computational_time, logger,)

    # SAVE A SOLUTION AS HTML FILE

    save_pretty_paceline_solution_as_html_file(balanced_title, balanced_contributions, logger)



if __name__ == "__main__":
    main()


