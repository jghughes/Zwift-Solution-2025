from typing import Optional, DefaultDict
from collections import defaultdict
from jgh_string import JghString
from jgh_formatting import format_number_1dp
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formatting import format_number_comma_separators
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph, arrange_riders_in_optimal_order, select_n_strongest_riders 
from jgh_formulae07 import log_pretty_paceline_solution_report, save_pretty_paceline_solution_as_html_file
from jgh_formulae08 import generate_ingenious_paceline_solutions,log_speed_bounds_of_exertion_constrained_paceline_solutions, log_workload_suffix_message
from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST, EXERTION_INTENSITY_FACTOR_LIMIT, RIDERS_FILE_NAME, DATA_DIRPATH
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineSolutionsComputationReport, PacelineComputationReport, PacelineIngredientsItem, RiderContributionDisplayObject, RiderContributionItem


def main():
    # SET UP LOGGING
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    # SET UP HELPER FUNCTIONS

    def get_solution(solution: Optional[PacelineComputationReport])-> PacelineComputationReport:
        return solution if solution else PacelineComputationReport()

    def get_contributions(solution: PacelineComputationReport)-> DefaultDict[ZsunRiderItem, RiderContributionDisplayObject]:
        return RiderContributionDisplayObject.from_RiderContributionItems(solution.rider_contributions if solution.rider_contributions else defaultdict(RiderContributionItem))

    def make_pretty_title(title: str, report : PacelineComputationReport, big_picture: PacelineSolutionsComputationReport, suffix : Optional[str]) -> str:
        if suffix:
            return f"\n{title} [ID {JghString.first_n_chars(report.guid,3)}] speed {format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph sigma {format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% n={format_number_comma_separators(big_picture.total_pull_sequences_examined)} itr={format_number_comma_separators(report.compute_iterations_performed_count)} {suffix}"
        else:
            return f"\n{title} (ID {JghString.first_n_chars(report.guid,3)}) speed {format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph sigma {format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% n={format_number_comma_separators(big_picture.total_pull_sequences_examined)} itr={format_number_comma_separators(report.compute_iterations_performed_count)} {suffix}"


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
        riders_list                     = riders,
        pull_speeds_kph                 = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec    = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor   = EXERTION_INTENSITY_FACTOR_LIMIT
    )

    # DO BRUTE-FORCE SEARCHES WITH ARRAY OF STANDARD PULL PERIODS

    computation_report = generate_ingenious_paceline_solutions(ingredients)

    thirty_sec          = get_solution(computation_report.thirty_sec_solution)
    identical_pull      = get_solution(computation_report.uniform_pull_solution)
    balanced_intensity  = get_solution(computation_report.balanced_intensity_of_effort_solution)
    everyone_pull_hard  = get_solution(computation_report.pull_hard_solution)
    hang_in             = get_solution(computation_report.hang_in_solution)

    thirty_sec_contributions         = get_contributions(thirty_sec)
    identical_pull_contributions     = get_contributions(identical_pull)
    balanced_intensity_contributions = get_contributions(balanced_intensity)
    everyone_pull_hard_contributions = get_contributions(everyone_pull_hard)
    hang_in_contributions            = get_contributions(hang_in)

    thirty_title    = make_pretty_title("\nTHIRTY SECOND PULLS PLAN", thirty_sec, computation_report,"(thirty_sec second pull for everyone)")
    identical_title = make_pretty_title("\nIDENTICAL PULLS PLAN", identical_pull, computation_report, "(identical pull for everyone)")
    balanced_title  = make_pretty_title("\nBALANCED-INTENSITY PLAN", balanced_intensity, computation_report, "(intensity is balanced. everybody pulls.)")
    pull_hard_title = make_pretty_title("\nPUSH HARD PLAN", everyone_pull_hard, computation_report, "(everybody pulls. weaker riders work hardest.)") 
    hang_in_title   = make_pretty_title("\nHANG-IN PLAN", hang_in,computation_report, "(eveybody rotates, maybe or maybe not pulling)")

    log_pretty_paceline_solution_report(thirty_title,  thirty_sec_contributions, logger,)
    log_pretty_paceline_solution_report(identical_title,  identical_pull_contributions, logger,)
    log_pretty_paceline_solution_report(balanced_title,  balanced_intensity_contributions, logger)
    log_pretty_paceline_solution_report(pull_hard_title, everyone_pull_hard_contributions, logger)
    log_pretty_paceline_solution_report(hang_in_title, hang_in_contributions, logger)

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(computation_report, logger)

    # SAVE A SOLUTION AS HTML FILE

    save_pretty_paceline_solution_as_html_file(thirty_title, thirty_sec_contributions, logger, "thirty_sec_pulls_plan.html")
    save_pretty_paceline_solution_as_html_file(identical_title, identical_pull_contributions, logger, "identical_pulls_plan.html")
    save_pretty_paceline_solution_as_html_file(balanced_title, balanced_intensity_contributions, logger, "balanced_intensity_plan.html")
    save_pretty_paceline_solution_as_html_file(pull_hard_title, everyone_pull_hard_contributions, logger, "everybody_pulls_hard_plan.html")
    save_pretty_paceline_solution_as_html_file(hang_in_title, hang_in_contributions, logger, "hang_in_plan.html")

    # RINSE AND REPEAT FOR THE LAST FIVE

    riders = select_n_strongest_riders(ingredients.riders_list, 5)

    riders = arrange_riders_in_optimal_order(riders)

    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders, logger)

    ingredients = PacelineIngredientsItem(
        riders_list                     = riders,
        pull_speeds_kph                 = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec    = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor   = EXERTION_INTENSITY_FACTOR_LIMIT
    )

    computation_report = generate_ingenious_paceline_solutions(ingredients)
    last_five  = get_solution(computation_report.hang_in_solution)
    last_five_contributions  = get_contributions(last_five)
    last_five_title = make_pretty_title("\nLAST-FIVE PLAN", last_five, computation_report, "(last five. everybody rotates, maybe or maybe not pulling)")
    log_pretty_paceline_solution_report(last_five_title, last_five_contributions, logger)
    save_pretty_paceline_solution_as_html_file(last_five_title, last_five_contributions, logger, "last_five_plan.html")

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(computation_report, logger)


    # RINSE AND REPEAT FOR THE FINAL FOUR

    riders = select_n_strongest_riders(ingredients.riders_list, 4)

    riders = arrange_riders_in_optimal_order(riders)

    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders, logger)

    ingredients = PacelineIngredientsItem(
        riders_list                     = riders,
        pull_speeds_kph                 = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec    = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor   = EXERTION_INTENSITY_FACTOR_LIMIT
    )

    computation_report = generate_ingenious_paceline_solutions(ingredients)
    final_four  = get_solution(computation_report.hang_in_solution)
    final_four_contributions  = get_contributions(final_four)
    final_four_title = make_pretty_title("\nLAST-FOUR PLAN", final_four, computation_report, "(last four. everybody rotates, maybe or maybe not pulling)")
    log_pretty_paceline_solution_report(final_four_title, final_four_contributions, logger)
    save_pretty_paceline_solution_as_html_file(final_four_title, final_four_contributions, logger, "last_four_plan.html")

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(computation_report, logger)

if __name__ == "__main__":
    main()


