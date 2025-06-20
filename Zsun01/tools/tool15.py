from typing import Optional, DefaultDict
from collections import defaultdict

from sympy import Basic
from jgh_string import JghString
from jgh_formatting import format_number_1dp, format_number_2dp, format_number_4dp, format_number_3dp
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph, arrange_riders_in_optimal_order
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

    # SET UP HELPER FUNCTIONS

    def get_solution(solution: Optional[PacelineComputationReport])-> PacelineComputationReport:
        return solution if solution else PacelineComputationReport()

    def get_contributions(solution: PacelineComputationReport)-> DefaultDict[ZsunRiderItem, RiderContributionDisplayObject]:
        return RiderContributionDisplayObject.from_RiderContributionItems(solution.rider_contributions if solution.rider_contributions else defaultdict(RiderContributionItem))

    def make_pretty_title(title: str, report : PacelineComputationReport, suffix : Optional[str]) -> str:
        if suffix:
            return f"\n{title} [ID {JghString.first_n_chars(report.guid,3)}]...{format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph  {format_number_3dp(report.calculated_dispersion_of_intensity_of_effort)} sigma {suffix}"
        else:
            return f"\n{title} (ID {JghString.first_n_chars(report.guid,3)})...{format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph  {format_number_3dp(report.calculated_dispersion_of_intensity_of_effort)} sigma"


    # GET THE DATA READY

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    riderIDs = get_team_riderIDs("giants")

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

    # DO A SIMPLE PULL PLAN WITH A SINGLE UNIFORM PULL PERIOD

    # ingredients.sequence_of_pull_periods_sec = [30.0] * len(riders)

    # computation_report = generate_a_single_paceline_solution_complying_with_exertion_constraints(ingredients)

    # thirty_contributions   = get_contributions(computation_report)

    # thirty_title = f"\nBASIC PLAN (ID {JghString.first_n_chars(computation_report.guid,3)}): {format_number_1dp(computation_report.calculated_average_speed_of_paceline_kph)} kph  {format_number_3dp(computation_report.calculated_dispersion_of_intensity_of_effort)} sigma"
    # log_pretty_paceline_solution_report(thirty_title, RiderContributionDisplayObject.from_RiderContributionItems(computation_report.rider_contributions), logger)
    # save_pretty_paceline_solution_as_html_file(thirty_title, thirty_contributions, logger, "basic_pull_plan.html")

    # DO BRUTE-FORCE SEARCHES WITH ARRAY OF STANDARD PULL PERIODS

    ingredients.sequence_of_pull_periods_sec = ARRAY_OF_STANDARD_PULL_PERIODS_SEC

    computation_report = generate_ingenious_paceline_solutions(ingredients)


    thirty          = get_solution(computation_report.thirty_sec_solution)
    uniform         = get_solution(computation_report.uniform_pull_solution)
    balanced        = get_solution(computation_report.balanced_intensity_of_effort_solution)
    pull_hard       = get_solution(computation_report.pull_hard_solution)
    hang_in         = get_solution(computation_report.hang_in_solution)
    surviving_four  = get_solution(computation_report.surviving_four_solution)

    thirty_contributions    = get_contributions(thirty)
    uniform_contributions   = get_contributions(uniform)
    balanced_contributions = get_contributions(balanced)
    pull_hard_contributions = get_contributions(pull_hard)
    hang_in_contributions  = get_contributions(hang_in)
    surviving_four_contributions  = get_contributions(surviving_four)

    thirty_title = make_pretty_title("\nTHIRTY SECOND PLAN", thirty, "(thirty second pull for everyone)")
    uniform_title = make_pretty_title("\nUNIFORM PULL PLAN", uniform, "(same pull for everyone)")
    balanced_title = make_pretty_title("\nBALANCED INTENSITY PLAN", balanced, "(everybody pulls. work intensity is balanced)")
    pull_hard_tempo = make_pretty_title("\nPULL HARD PLAN", pull_hard, "(everybody pulls. weaker riders work harder to pull)") 
    hang_in_title = make_pretty_title("\nHANG-IN PLAN", hang_in, "(eveybody plays a part, maybe or maybe not pulling)")
    surviving_four_title = make_pretty_title("\nSURVIVING FOUR PLAN", hang_in, "(down to the last four, eveybody plays a part, maybe or maybe not pulling)")

    log_pretty_paceline_solution_report(thirty_title,  thirty_contributions, logger,)
    log_pretty_paceline_solution_report(uniform_title,  uniform_contributions, logger,)
    log_pretty_paceline_solution_report(balanced_title,  balanced_contributions, logger)
    log_pretty_paceline_solution_report(pull_hard_tempo, pull_hard_contributions, logger)
    log_pretty_paceline_solution_report(hang_in_title, hang_in_contributions, logger)
    log_pretty_paceline_solution_report(surviving_four_title, surviving_four_contributions, logger)

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(computation_report, logger)

    # SAVE A SOLUTION AS HTML FILE

    save_pretty_paceline_solution_as_html_file(thirty_title, thirty_contributions, logger, "thirty_sec_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(uniform_title, uniform_contributions, logger, "uniform_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(balanced_title, balanced_contributions, logger, "balanced_intensity_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(pull_hard_tempo, pull_hard_contributions, logger, "pull_hard_plan.html")
    save_pretty_paceline_solution_as_html_file(hang_in_title, hang_in_contributions, logger, "hang_in_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(surviving_four_title, surviving_four_contributions, logger, "surviving_four_pull_plan.html")



if __name__ == "__main__":
    main()


