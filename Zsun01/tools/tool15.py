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
            return f"\n{title} [ID {JghString.first_n_chars(report.guid,3)}]: {format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph  {format_number_3dp(report.calculated_dispersion_of_intensity_of_effort)} sigma {suffix}"
        else:
            return f"\n{title} (ID {JghString.first_n_chars(report.guid,3)}): {format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph  {format_number_3dp(report.calculated_dispersion_of_intensity_of_effort)} sigma"


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

    # basic_contributions   = get_contributions(computation_report)

    # basic_title = f"\nBASIC PLAN (ID {JghString.first_n_chars(computation_report.guid,3)}): {format_number_1dp(computation_report.calculated_average_speed_of_paceline_kph)} kph  {format_number_3dp(computation_report.calculated_dispersion_of_intensity_of_effort)} sigma"
    # log_pretty_paceline_solution_report(basic_title, RiderContributionDisplayObject.from_RiderContributionItems(computation_report.rider_contributions), logger)
    # save_pretty_paceline_solution_as_html_file(basic_title, basic_contributions, logger, "basic_pull_plan.html")

    # DO BRUTE-FORCE SEARCHES WITH ARRAY OF STANDARD PULL PERIODS

    ingredients.sequence_of_pull_periods_sec = ARRAY_OF_STANDARD_PULL_PERIODS_SEC

    computation_report = generate_ingenious_paceline_solutions(ingredients)


    basic    = get_solution(computation_report.basic_solution)
    simple   = get_solution(computation_report.simple_solution)
    balanced = get_solution(computation_report.balanced_intensity_of_effort_solution)
    tempo    = get_solution(computation_report.tempo_solution)
    drop     = get_solution(computation_report.drop_solution)

    basic_contributions   = get_contributions(basic)
    simple_contributions   = get_contributions(simple)
    balanced_contributions = get_contributions(balanced)
    tempo_contributions    = get_contributions(tempo)
    drop_contributions     = get_contributions(drop)

    basic_title = make_pretty_title("\nBASIC PLAN", basic, "(thirty second pull. no drop.)")
    simple_title = make_pretty_title("\nSIMPLE PLAN", simple, "(uniform pull. no drop.)")
    balanced_title = make_pretty_title("\nBALANCED PLAN", balanced, "(balanced workload. no drop)")
    tempo_title = make_pretty_title("\nTEMPO PLAN", tempo, "(speedy. no drop)") 
    drop_title = make_pretty_title("\nSPEED PLAN", drop, "(focus on speed alone)")

    log_pretty_paceline_solution_report(basic_title,  basic_contributions, logger,)
    log_pretty_paceline_solution_report(simple_title,  simple_contributions, logger,)
    log_pretty_paceline_solution_report(balanced_title,  balanced_contributions, logger)
    log_pretty_paceline_solution_report(tempo_title, tempo_contributions, logger)
    log_pretty_paceline_solution_report(drop_title, drop_contributions, logger)

    # LOG SUFFIX MESSAGE ABOUT BRUTE-FORCE COMPUTATIONS

    log_workload_suffix_message(computation_report, logger)

    # SAVE A SOLUTION AS HTML FILE

    save_pretty_paceline_solution_as_html_file(basic_title, basic_contributions, logger, "basic_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(simple_title, simple_contributions, logger, "simple_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(balanced_title, balanced_contributions, logger, "balanced_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(tempo_title, tempo_contributions, logger, "tempo_pull_plan.html")
    save_pretty_paceline_solution_as_html_file(drop_title, drop_contributions, logger, "drop_pull_plan.html")



if __name__ == "__main__":
    main()


