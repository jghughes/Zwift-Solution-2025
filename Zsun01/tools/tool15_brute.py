"""
This tool generates, analyzes, and exports detailed paceline plans for a specified cycling team, focusing on exertion-constrained and optimal strategies.

The script performs the following steps:
- Configures logging for the application.
- Loads rider data for a specified team and arranges riders in an optimal order for paceline efficiency.
- Logs the speed bounds for exertion-constrained paceline solutions.
- Constructs the input parameters for paceline planning, including rider list, pull speeds, pull periods, and exertion limits.
- Computes a set of paceline plans for the full team using an advanced solution generation algorithm.
- Computes additional plans for smaller team sizes (last five and last four riders) to analyze diminishing team scenarios.
- Prepares a display object summarizing all computed paceline solutions, including captions and metadata.
- Saves individual and summary paceline plans as HTML reports for further review and sharing.

This tool demonstrates advanced team time trial (TTT) strategy modeling, combinatorial optimization, and automated report generation for cycling performance analysis using Python.
"""

from typing import Dict, Any, List
from computation_classes_display_objects import PacelinePlanTypeEnum, PackageOfPacelineComputationReportDisplayObject
from zsun_rider_item import ZsunItem
from computation_classes import PacelineIngredientsItem
from handy_utilities import read_json_dict_of_ZsunDTO, get_recognised_ZsunItems_only
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph, arrange_riders_in_optimal_order
from jgh_formulae07 import save_summary_of_all_paceline_plans_as_html
from jgh_formulae08 import generate_package_of_paceline_solutions,log_speed_bounds_of_exertion_constrained_paceline_solutions
from jgh_formulae09 import generate_fastest_paceline_plan_for_n_strongest, save_multiple_individual_paceline_plans_as_html
from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST
from html_css import FOOTNOTES
from paceline_plan_display_ingredients import  get_caption_for_summary_of_all_paceline_plans
from filenames import RIDERS_FILE_NAME, get_save_filename_for_summary_of_all_paceline_plans
from dirpaths import DATA_DIRPATH
from team_rosters import RepositoryOfTeams
import logging
logger = logging.getLogger(__name__)

def main() -> None:
    # GET THE SOURCE DATA READY
    team_nickname = "betel" # see inside team_rosters.py for other teams
    riderIDs: List[str] = RepositoryOfTeams.get_IDs_of_riders_on_a_team(team_nickname)
    dict_of_ZsunItems: Dict[str, ZsunItem] = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)
    riders: List[ZsunItem] = get_recognised_ZsunItems_only(riderIDs, dict_of_ZsunItems)
    riders = arrange_riders_in_optimal_order(riders)

    # COMPUTE 1st TO 5th PLANS - FULL TEAM
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders)
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor= RepositoryOfTeams.get_exertion_intensity_factor_for_team(team_nickname),
    )
    report: Any = generate_package_of_paceline_solutions(ingredients)
    report_displayobject: PackageOfPacelineComputationReportDisplayObject = PackageOfPacelineComputationReportDisplayObject.from_PackageOfPacelineComputationReportItem(report)

    # COMPUTE 6th and 7th PLANS - DIMINISHING TEAM
    report_displayobject.solutions[PacelinePlanTypeEnum.LAST_FIVE] = generate_fastest_paceline_plan_for_n_strongest(ingredients, 5)
    report_displayobject.solutions[PacelinePlanTypeEnum.LAST_FOUR] = generate_fastest_paceline_plan_for_n_strongest(ingredients, 4)

    report_displayobject.caption = get_caption_for_summary_of_all_paceline_plans(team_nickname)

    # SAVE WORK
    save_multiple_individual_paceline_plans_as_html(report_displayobject, team_nickname, SAVE_OUTPUT_DIRPATH)
    save_summary_of_all_paceline_plans_as_html(report_displayobject, get_save_filename_for_summary_of_all_paceline_plans(team_nickname), SAVE_OUTPUT_DIRPATH, FOOTNOTES)

if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logging.getLogger("numba").setLevel(logging.ERROR)

    SAVE_OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel_new/"

    main()