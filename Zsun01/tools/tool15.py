from typing import DefaultDict, Optional, Dict, Any, List
from collections import defaultdict

from computation_classes_display_objects import (
    PacelineSolutionType,
    PacelineSolutionsComputationReportDisplayObject,
    PacelineComputationReportDisplayObject,
    RiderContributionDisplayObject,
)
from zsun_rider_item import ZsunRiderItem
from computation_classes import PacelineIngredientsItem
from handy_utilities import read_dict_of_zsunriderItems
from repository_of_teams import get_team_riderIDs
from constants import (
    STANDARD_PULL_PERIODS_SEC_AS_LIST,
    EXERTION_INTENSITY_FACTOR_LIMIT,
    RIDERS_FILE_NAME,
    DATA_DIRPATH,
    SOLUTION_CONFIG,
    SAVE_FILE_NAMES_FOR_PULL_PLANS,
    get_consolidated_report_filename,
    FOOTNOTES
)
from jgh_string import JghString
from jgh_formatting import format_number_1dp, format_number_comma_separators
from jgh_formulae02 import (
    calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph,
    arrange_riders_in_optimal_order,
    select_n_strongest_riders,
)
from jgh_formulae07 import (
    log_pretty_paceline_solution_report,
    save_pretty_paceline_plan_as_html_file,
    save_all_pretty_paceline_plans_in_consolidated_html_file,
)
from jgh_formulae08 import (
    generate_ingenious_paceline_solutions,
    log_speed_bounds_of_exertion_constrained_paceline_solutions,
    log_workload_suffix_message)

def main() -> None:
    # SET UP LOGGING
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger: logging.Logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    SAVE_FILE_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/Betel/"

    # HELPER FUNCTIONS
    def get_computation_report_safely(
        report: Optional[PacelineComputationReportDisplayObject]
    ) -> PacelineComputationReportDisplayObject:
        return report if report else PacelineComputationReportDisplayObject()

    def make_pretty_table_caption(
        title: str,
        report: PacelineComputationReportDisplayObject,
        overall_report: PacelineSolutionsComputationReportDisplayObject,
        suffix: Optional[str],
    ) -> str:
        if suffix:
            return (
                f"\n{title} [ID {JghString.first_n_chars(report.guid,3)}] "
                f"speed {format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph "
                f"sigma {format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% "
                f"n={format_number_comma_separators(overall_report.total_pull_sequences_examined)} "
                f"itr={format_number_comma_separators(report.compute_iterations_performed_count)} {suffix}"
            )
        else:
            return (
                f"\n{title} (ID {JghString.first_n_chars(report.guid,3)}) "
                f"speed {format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph "
                f"sigma {format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% "
                f"n={format_number_comma_separators(overall_report.total_pull_sequences_examined)} "
                f"itr={format_number_comma_separators(report.compute_iterations_performed_count)} {suffix}"
            )

    # GET THE DATA READY
    team_name = "betel"
    consolidated_report_caption = f"Paceline plans for {team_name}"
    dict_of_zsunrideritems: Dict[str, ZsunRiderItem] = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs: List[str] = get_team_riderIDs(team_name)
    riders: List[ZsunRiderItem] = [dict_of_zsunrideritems[riderID] for riderID in riderIDs]
    riders = arrange_riders_in_optimal_order(riders)

    # MAIN PACELINE SOLUTIONS
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders, logger)
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor= EXERTION_INTENSITY_FACTOR_LIMIT,
    )
    report: Any = generate_ingenious_paceline_solutions(ingredients)
    report_displayobject: PacelineSolutionsComputationReportDisplayObject = PacelineSolutionsComputationReportDisplayObject.from_PacelineSolutionsComputationReportItem(report)

    # LAST FIVE
    riders_last_five: List[ZsunRiderItem] = select_n_strongest_riders(ingredients.riders_list, 5)
    riders_last_five                      = arrange_riders_in_optimal_order(riders_last_five)
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders_last_five, logger)
    ingredients_last_five: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders_last_five,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders_last_five)] * len(riders_last_five),
        sequence_of_pull_periods_sec = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor= EXERTION_INTENSITY_FACTOR_LIMIT,
    )
    report_last_five: Any = generate_ingenious_paceline_solutions(ingredients_last_five)
    report_last_five_displayobject: PacelineSolutionsComputationReportDisplayObject = PacelineSolutionsComputationReportDisplayObject.from_PacelineSolutionsComputationReportItem(report_last_five)
    last_five: PacelineComputationReportDisplayObject = get_computation_report_safely(report_last_five_displayobject.solutions[PacelineSolutionType.FASTEST])

    # LAST FOUR
    riders_last_four: List[ZsunRiderItem] = select_n_strongest_riders(ingredients.riders_list, 4)
    riders_last_four                      = arrange_riders_in_optimal_order(riders_last_four)
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders_last_four, logger)
    ingredients_last_four: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders_last_four,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders_last_four)] * len(riders_last_four),
        sequence_of_pull_periods_sec = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor= EXERTION_INTENSITY_FACTOR_LIMIT,
    )
    report_last_four: Any = generate_ingenious_paceline_solutions(ingredients_last_four)
    report_last_four_display_object: PacelineSolutionsComputationReportDisplayObject = PacelineSolutionsComputationReportDisplayObject.from_PacelineSolutionsComputationReportItem(report_last_four)
    last_four: PacelineComputationReportDisplayObject = get_computation_report_safely(report_last_four_display_object.solutions[PacelineSolutionType.FASTEST])

    # CONSOLIDATED REPORT
    consolidated_report_display_object: PacelineSolutionsComputationReportDisplayObject = PacelineSolutionsComputationReportDisplayObject(
        caption                            = consolidated_report_caption,
        total_pull_sequences_examined      = report_displayobject.total_pull_sequences_examined,
        total_compute_iterations_performed = report_displayobject.total_compute_iterations_performed,
        computational_time                 = report_displayobject.computational_time,
        solutions                          = report_displayobject.solutions.copy(),
    )
    # Add LAST_FIVE and LAST_FOUR externally
    consolidated_report_display_object.solutions[PacelineSolutionType.LAST_FIVE] = last_five
    consolidated_report_display_object.solutions[PacelineSolutionType.LAST_FOUR] = last_four

    # Map for overall report context for each solution type
    overall_report_map: Dict[PacelineSolutionType, PacelineSolutionsComputationReportDisplayObject] = {
        PacelineSolutionType.LAST_FIVE: report_last_five_displayobject,
        PacelineSolutionType.LAST_FOUR: report_last_four_display_object,
    }
    default_overall_report: PacelineSolutionsComputationReportDisplayObject = report_displayobject

    # log and save all paceline plans one by one
    for plan_enum, caption_prefix, caption_suffix in SOLUTION_CONFIG:
        report_obj: PacelineComputationReportDisplayObject = consolidated_report_display_object.solutions[plan_enum]
        overall_report: PacelineSolutionsComputationReportDisplayObject = overall_report_map.get(plan_enum, default_overall_report)
        caption: str = make_pretty_table_caption(caption_prefix, report_obj, overall_report, caption_suffix)
        report_obj.display_caption = caption
        # Log and save individual HTML files
        log_pretty_paceline_solution_report(report_obj, logger)
        filename = SAVE_FILE_NAMES_FOR_PULL_PLANS[plan_enum]
        save_pretty_paceline_plan_as_html_file(report_obj, filename, SAVE_FILE_DIRPATH, FOOTNOTES,logger)

    # Save all solutions as a single HTML file
    save_all_pretty_paceline_plans_in_consolidated_html_file(consolidated_report_display_object, get_consolidated_report_filename(team_name), SAVE_FILE_DIRPATH, FOOTNOTES, logger)

if __name__ == "__main__":
    main()