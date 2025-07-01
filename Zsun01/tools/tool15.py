import logging
from typing import Optional, Dict, Any, List
from computation_classes_display_objects import PacelinePlanTypeEnum, PacelineSolutionsComputationReportDisplayObject, PacelineComputationReportDisplayObject
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem
from handy_utilities import read_dict_of_zsunriderItems
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph, arrange_riders_in_optimal_order, select_n_strongest_riders
from jgh_formulae07 import make_pretty_caption_for_a_paceline_plan, log_a_paceline_plan, save_a_paceline_plan_as_html, save_summary_of_all_paceline_plans_as_html
from jgh_formulae08 import generate_ingenious_paceline_solutions,log_speed_bounds_of_exertion_constrained_paceline_solutions, log_workload_suffix_message
from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST, EXERTION_INTENSITY_FACTOR_LIMIT
from html_fragments import FOOTNOTES
from paceline_plan_display_ingredients import  LIST_OF_CAPTIONS_FOR_PACELINE_PLANS, get_caption_for_summary_of_all_paceline_plans
from filenames import RIDERS_FILE_NAME, get_save_filename_for_single_paceline_plan, get_save_filename_for_summary_of_all_paceline_plans
from dirpaths import DATA_DIRPATH
from teams import get_team_riderIDs


def generate_fastest_solution_for_n_strongest(ingredients: PacelineIngredientsItem, n: int, logger: logging.Logger) -> PacelineComputationReportDisplayObject:
        
    def get_computation_report_safely(
        report: Optional[PacelineComputationReportDisplayObject]
    ) -> PacelineComputationReportDisplayObject:
        return report if report else PacelineComputationReportDisplayObject()

    riders_n = select_n_strongest_riders(ingredients.riders_list, n)
    riders_n = arrange_riders_in_optimal_order(riders_n)
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders_n, logger)
    ingredients_n = PacelineIngredientsItem(
        riders_list=riders_n,
        pull_speeds_kph=[calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders_n)] * len(riders_n),
        sequence_of_pull_periods_sec=STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor=EXERTION_INTENSITY_FACTOR_LIMIT,
    )
    report_n = generate_ingenious_paceline_solutions(ingredients_n)
    report_n_displayobject = PacelineSolutionsComputationReportDisplayObject.from_PacelineSolutionsComputationReportItem(report_n)
    answer = get_computation_report_safely(report_n_displayobject.solutions[PacelinePlanTypeEnum.FASTEST])
    return answer


def log_and_save_all_solutions(
    report_displayobject: PacelineSolutionsComputationReportDisplayObject,
    team_name: str,
    save_dir: str,
    logger: logging.Logger
) -> None:
    for plan_type_enum, caption_prefix, caption_suffix in LIST_OF_CAPTIONS_FOR_PACELINE_PLANS:
        paceline_report: PacelineComputationReportDisplayObject = report_displayobject.solutions[plan_type_enum]
        caption: str = make_pretty_caption_for_a_paceline_plan(caption_prefix, paceline_report, report_displayobject, caption_suffix)
        paceline_report.display_caption = caption
        log_a_paceline_plan(paceline_report, logger)
        filename = get_save_filename_for_single_paceline_plan(team_name, plan_type_enum)
        save_a_paceline_plan_as_html(paceline_report, filename, save_dir, FOOTNOTES, True)


def main() -> None:
    # SET UP LOGGING
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger: logging.Logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    SAVE_OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    # GET THE SOURCE DATA READY
    team_name = "betel"
    dict_of_zsunrideritems: Dict[str, ZsunRiderItem] = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs: List[str] = get_team_riderIDs(team_name)
    riders: List[ZsunRiderItem] = [dict_of_zsunrideritems[riderID] for riderID in riderIDs]
    riders = arrange_riders_in_optimal_order(riders)

    # COMPUTE 1st TO 5th PLANS - FULL TEAM
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders, logger)
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor= EXERTION_INTENSITY_FACTOR_LIMIT,
    )
    report: Any = generate_ingenious_paceline_solutions(ingredients)
    report_displayobject: PacelineSolutionsComputationReportDisplayObject = PacelineSolutionsComputationReportDisplayObject.from_PacelineSolutionsComputationReportItem(report)

    # COMPUTE 6th and 7th PLANS - DIMINISHING TEAM
    report_displayobject.solutions[PacelinePlanTypeEnum.LAST_FIVE] = generate_fastest_solution_for_n_strongest(ingredients, 5, logger)
    report_displayobject.solutions[PacelinePlanTypeEnum.LAST_FOUR] = generate_fastest_solution_for_n_strongest(ingredients, 4, logger)

    report_displayobject.caption = get_caption_for_summary_of_all_paceline_plans(team_name)

    # LOG AND SAVE ALL 7 PLANS. SAVE SUMMARY REPORT
    log_and_save_all_solutions(report_displayobject, team_name, SAVE_OUTPUT_DIRPATH, logger)
    save_summary_of_all_paceline_plans_as_html(report_displayobject, get_save_filename_for_summary_of_all_paceline_plans(team_name), SAVE_OUTPUT_DIRPATH, FOOTNOTES, logger)

if __name__ == "__main__":
    main()