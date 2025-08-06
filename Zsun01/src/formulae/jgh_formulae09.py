from typing import Optional
from computation_classes import PacelineIngredientsItem
from computation_classes_display_objects import PacelinePlanTypeEnum, PacelineSolutionsComputationReportDisplayObject, PacelineComputationReportDisplayObject
from jgh_formulae02 import calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph, arrange_riders_in_optimal_order, select_n_strongest_riders
from jgh_formulae07 import make_pretty_caption_for_a_paceline_plan, log_a_paceline_plan, save_a_paceline_plan_as_html
from jgh_formulae08 import generate_package_of_paceline_solutions,log_speed_bounds_of_exertion_constrained_paceline_solutions
from constants import STANDARD_PULL_PERIODS_SEC_AS_LIST, EXERTION_INTENSITY_FACTOR_LIMIT
from html_css import FOOTNOTES
from paceline_plan_display_ingredients import  LIST_OF_CAPTIONS_FOR_PACELINE_PLANS
from filenames import get_save_filename_for_single_paceline_plan
import logging
logger = logging.getLogger(__name__)

def generate_fastest_paceline_plan_for_n_strongest(ingredients: PacelineIngredientsItem, n: int) -> PacelineComputationReportDisplayObject:
        
    def get_computation_report_safely(
        report: Optional[PacelineComputationReportDisplayObject]
    ) -> PacelineComputationReportDisplayObject:
        return report if report else PacelineComputationReportDisplayObject()

    riders_n = select_n_strongest_riders(ingredients.riders_list, n)
    riders_n = arrange_riders_in_optimal_order(riders_n)
    log_speed_bounds_of_exertion_constrained_paceline_solutions(riders_n)
    ingredients_n = PacelineIngredientsItem(
        riders_list=riders_n,
        pull_speeds_kph=[calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders_n)] * len(riders_n),
        sequence_of_pull_periods_sec=STANDARD_PULL_PERIODS_SEC_AS_LIST,
        max_exertion_intensity_factor=EXERTION_INTENSITY_FACTOR_LIMIT,
    )
    report_n = generate_package_of_paceline_solutions(ingredients_n)
    report_n_displayobject = PacelineSolutionsComputationReportDisplayObject.from_PacelineSolutionsComputationReportItem(report_n)
    answer = get_computation_report_safely(report_n_displayobject.solutions[PacelinePlanTypeEnum.FASTEST])
    return answer


def save_multiple_individual_paceline_plans_as_html(
    report_displayobject: PacelineSolutionsComputationReportDisplayObject,
    team_name: str,
    save_dir: str,
) -> None:
    for plan_type_enum, caption_prefix, caption_suffix in LIST_OF_CAPTIONS_FOR_PACELINE_PLANS:
        paceline_report: PacelineComputationReportDisplayObject = report_displayobject.solutions[plan_type_enum]
        caption: str = make_pretty_caption_for_a_paceline_plan(caption_prefix, paceline_report, report_displayobject, caption_suffix)
        paceline_report.display_caption = caption
        log_a_paceline_plan(paceline_report)
        filename = get_save_filename_for_single_paceline_plan(team_name, plan_type_enum)
        save_a_paceline_plan_as_html(paceline_report, filename, save_dir, FOOTNOTES, True)

