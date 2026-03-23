"""
Paceline Plan Generation and Analysis Tool for Cycling Teams

This module generates, analyzes, and exports detailed paceline plans for a specified cycling team,
focusing on exertion-constrained and optimal strategies for team time trial (TTT) scenarios.

Key Features:
- Loads and arranges rider data for a given team, supporting multiple rider selection and ordering strategies.
- Computes paceline plans under various pull durations (e.g., 30s, 60s) and exertion constraints.
- Generates advanced paceline solutions for full teams and reduced team sizes (e.g., strongest five or four riders).
- Applies combinatorial optimization to identify balanced, fastest, and high-intensity pacing strategies.
- Summarizes results in display objects and exports individual and consolidated HTML reports.
- Supports automated upload of summary reports to Azure Blob Storage for sharing and review.
- Provides detailed logging and error handling for robust batch execution.

This tool is intended for cycling performance analysts and coaches seeking to optimize TTT strategies
using data-driven, reproducible methods in Python.
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from paceline_computation_types import PacelineIngredientsItem, PacelineComputationReportItem
from paceline_computation_display_objects import (
    PacelinePlanTypeEnum,
    PacelineComputationReportDisplayObject,
    PackageOfPacelineComputationReportDisplayObject,
)
from constants import PERMISSABLE_PULL_PERIODS_SEC_AS_LIST
from jgh_enums import PacelinePlanTypeEnum
# from html_text import BRUTE_FOOTNOTES_HTML
from jgh_azure_storage_service_client import AzureStorageServiceClient
from jgh_formulae02 import (
    arrange_riders_by_1_minute_strength,
    arrange_riders_by_zwiftracingapp_zpFTP_strength,
    arrange_riders_interleaved_by_1_minute_strength,
    calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph,
    select_n_riders_at_the_top_of_the_list,
)
from jgh_formulae08 import (
    generate_a_single_paceline_solution_complying_with_exertion_constraints,
    generate_package_of_paceline_solutions,
    log_speed_bounds_of_exertion_constrained_paceline_solutions,
)
from jgh_formulae09 import (
    # log_single_paceline_plan_as_pretty_table,
    populate_title_for_pace_plan,
    populate_compute_statistics_for_pace_plan,
    # format_single_paceline_plan_as_html_document,
    format_paceline_plans_as_one_page_html_doc,
    save_html_document_to_hard_drive,
    upload_text_to_blob_storage_in_azure,
)
from jgh_internet_helpers import throw_if_no_internet_connection

from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_string import make_pretty_count_of_bytes

from jgh_string import capitalize_first_letter
from zwift_id_base import lookup_Items_by_ZwiftID

from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_brute_dto import RiderBruteDTO, RiderBruteDtoListModel
from rider_brute_item import RiderBruteItem
from storage_config import (
    FILENAME_RIDER_BRUTE_DTO_JSON_DICT,
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    DIRPATH_BRUTE_TTT_DOCS,
    AZURE_ACCOUNTNAME_ZSUN,
    AZURE_CONTAINERNAME_BRUTE,
    AZURE_CONTAINERNAME_ZSUN,
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST,
    # format_save_filename_for_document_of_single_paceline_plan,
    make_filename_for_one_page_summary_html_doc,)

import time
import logging
from jgh_exceptions import AlertMessageError

def load_css_style_sheet() -> str:
    path = Path(__file__).parent.parent / "src" / "css" / "paceline_plan_summary.css"
    with open(path, encoding="utf-8") as f:
        return f.read()

PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET = load_css_style_sheet()

def load_footnotes_html() -> str:
    path = Path(__file__).parent.parent / "src" / "html" / "footnotes.html"
    with open(path, encoding="utf-8") as f:
        return f.read()

BRUTE_FOOTNOTES_HTML = load_footnotes_html()


# HEAP POWERFUL
async def generate_ttt_scenarios_with_brute() -> None:
    print("Tool starting")

    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_BRUTE_TTT_DOCS)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_BRUTE_DTO_JSON_DICT])
    except Exception as err:
        print(err)
        return

    # ===========================
    print(f"\ndownloading riderDTO from Azure Blob Storage\n   Account: {AZURE_ACCOUNTNAME_ZSUN}\n   Container: {AZURE_CONTAINERNAME_ZSUN}\n   Blob: {AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST}")
    # ===========================

    try:
        azure_client = AzureStorageServiceClient()

        blob_as_bytes : bytes = await azure_client.download_block_blob_as_bytes_async(AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN, AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST)
        blob_size = make_pretty_count_of_bytes(len(blob_as_bytes))
        # ===========================
        print(f"\ndownloaded {blob_size}")
        # ===========================
        blob_as_text = blob_as_bytes.decode('utf-8')

        something = json.loads(blob_as_text)
        list_of_RiderDTO: List[RiderBruteDTO] = RiderBruteDtoListModel.model_validate(something, strict=True).root
        list_of_RiderItem: List[RiderBruteItem] = [
            RiderBruteItem.from_dataTransferObject(rider_brute_dto)
            for rider_brute_dto in list_of_RiderDTO]

        dict_of_RiderItem: Dict[str, RiderBruteItem] = {
            rider_brute_item.zwift_id: rider_brute_item
            for rider_brute_item in list_of_RiderItem
        }    
        print(f"\ncount of riders: {len(list_of_RiderDTO)}")
    except Exception as e:
        print(f"rider data not obtained.\n - Error message: {e}")
        return

    try:
        full_team_of_riders: List[RiderBruteItem] = lookup_Items_by_ZwiftID(_riderIDs, dict_of_RiderItem, RiderBruteItem)
    except Exception as e:
        print(f"Team '{_team_name}' not found:\n - Error message:\n - {e}")
        return

    log_speed_bounds_of_exertion_constrained_paceline_solutions(full_team_of_riders)

    # ===========================
    print(f"\nTask #1: computing 1st scenario - 30_sec pull full team...")
    # ===========================

    riders = arrange_riders_by_zwiftracingapp_zpFTP_strength(full_team_of_riders)
    pull_periods_sec_as_list: list[float] = [30.0] * len(riders)
    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = riders,
        pull_speeds_kph                 = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        max_exertion_intensity_factor   = RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(_team_name),
        sequence_of_pull_periods_sec    = pull_periods_sec_as_list,
        )
    report_30sec_plan : PacelineComputationReportItem = generate_a_single_paceline_solution_complying_with_exertion_constraints(paceline_ingredients)
    report_30sec_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_30sec_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.THIRTY_SEC_PULL, report_30sec_plan_display_object)
    populate_compute_statistics_for_pace_plan(1, report_30sec_plan_display_object)

    # ===========================
    # log_single_paceline_plan_as_pretty_table(report_30sec_plan_display_object)
    # filename = format_save_filename_for_document_of_single_paceline_plan(_team_name, PacelinePlanTypeEnum.THIRTY_SEC_PULL)
    # html_doc = format_single_paceline_plan_as_html_document(report_30sec_plan_display_object, BRUTE_FOOTNOTES_HTML, True)
    # saved_file_path = save_html_document_to_hard_drive(Path(DIRPATH_BRUTE_TTT_DOCS), filename, html_doc)
    # print(f"\nPaceline plan saved to:\n{saved_file_path}\n")
    # ===========================

    # ===========================
    print(f"\nTask #2: computing 2nd scenario - 60_sec pull full team")
    # ===========================

    riders = arrange_riders_by_zwiftracingapp_zpFTP_strength(full_team_of_riders)
    pull_periods_sec_as_list: list[float] = [60.0] * len(riders)
    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = riders,
        pull_speeds_kph                 = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        max_exertion_intensity_factor   = RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(_team_name),
        sequence_of_pull_periods_sec    = pull_periods_sec_as_list,
        )
    report_60sec_plan : PacelineComputationReportItem = generate_a_single_paceline_solution_complying_with_exertion_constraints(paceline_ingredients)
    report_60sec_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_60sec_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.SIXTY_SEC_PULL, report_60sec_plan_display_object)
    populate_compute_statistics_for_pace_plan(1, report_60sec_plan_display_object)

    # ===========================
    # log_single_paceline_plan_as_pretty_table(report_60sec_plan_display_object)
    # filename = format_save_filename_for_document_of_single_paceline_plan(_team_name, PacelinePlanTypeEnum.SIXTY_SEC_PULL)
    # html_doc = format_single_paceline_plan_as_html_document(report_60sec_plan_display_object, BRUTE_FOOTNOTES_HTML, True)
    # saved_file_path = save_html_document_to_hard_drive(Path(DIRPATH_BRUTE_TTT_DOCS), filename, html_doc)
    # print(f"\nPaceline plan saved to:\n{saved_file_path}\n")
    # ===========================

    # ===========================
    print(f"\nTask #3 computing 3rd to 5th scenarios - full team")
    # ===========================

    riders = arrange_riders_interleaved_by_1_minute_strength(full_team_of_riders)
    pull_periods_sec_as_list = PERMISSABLE_PULL_PERIODS_SEC_AS_LIST
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec = pull_periods_sec_as_list,
        max_exertion_intensity_factor= RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(_team_name),
    )
    package: Any = generate_package_of_paceline_solutions(ingredients)

    report_balanced_intensity_plan = package.dict_of_solutions[PacelinePlanTypeEnum.BALANCED_INTENSITY]
    report_balanced_intensity_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_balanced_intensity_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.BALANCED_INTENSITY, report_balanced_intensity_plan_display_object)
    populate_compute_statistics_for_pace_plan(package.total_pull_sequences_examined, report_balanced_intensity_plan_display_object)

    report_everybody_pull_hard_plan = package.dict_of_solutions[PacelinePlanTypeEnum.EVERYBODY_PULL_HARD]
    report_everybody_pull_hard_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_everybody_pull_hard_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.EVERYBODY_PULL_HARD, report_everybody_pull_hard_plan_display_object)
    populate_compute_statistics_for_pace_plan(package.total_pull_sequences_examined, report_everybody_pull_hard_plan_display_object)

    report_fastest_full_team_plan = package.dict_of_solutions[PacelinePlanTypeEnum.FASTEST]
    report_fastest_full_team_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_fastest_full_team_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.FASTEST,report_fastest_full_team_plan_display_object)
    populate_compute_statistics_for_pace_plan(package.total_pull_sequences_examined, report_fastest_full_team_plan_display_object)

    # ===========================
    print(f"\nTask #4: computing 6th scenario - strongest five riders")
    # ===========================

    riders = arrange_riders_by_1_minute_strength(full_team_of_riders)
    riders = select_n_riders_at_the_top_of_the_list(riders, 5)
    riders = arrange_riders_interleaved_by_1_minute_strength(riders)

    pull_periods_sec_as_list = PERMISSABLE_PULL_PERIODS_SEC_AS_LIST
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec = pull_periods_sec_as_list,
        max_exertion_intensity_factor= RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(_team_name),
    )

    package: Any = generate_package_of_paceline_solutions(ingredients)
    report_fastest_strongest_five_plan = package.dict_of_solutions[PacelinePlanTypeEnum.FASTEST]
    report_fastest_strongest_five_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_fastest_strongest_five_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE,report_fastest_strongest_five_plan_display_object)
    populate_compute_statistics_for_pace_plan(package.total_pull_sequences_examined, report_fastest_strongest_five_plan_display_object)

    # ===========================
    print(f"\nTask #5: computing 7th scenario - strongest four riders")
    # ===========================

    riders = arrange_riders_by_1_minute_strength(full_team_of_riders)
    riders = select_n_riders_at_the_top_of_the_list(riders, 4)
    riders = arrange_riders_interleaved_by_1_minute_strength(riders)

    pull_periods_sec_as_list = PERMISSABLE_PULL_PERIODS_SEC_AS_LIST
    ingredients: PacelineIngredientsItem = PacelineIngredientsItem(
        riders_list                  = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        sequence_of_pull_periods_sec = pull_periods_sec_as_list,
        max_exertion_intensity_factor= RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(_team_name),
    )
    package: Any = generate_package_of_paceline_solutions(ingredients)
    report_fastest_strongest_four_plan = package.dict_of_solutions[PacelinePlanTypeEnum.FASTEST]
    report_fastest_strongest_four_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_fastest_strongest_four_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR,report_fastest_strongest_four_plan_display_object)
    populate_compute_statistics_for_pace_plan(package.total_pull_sequences_examined, report_fastest_strongest_four_plan_display_object)

    # ===========================
    print(f"\nTask #6: publishing to html doc")
    # ===========================

    package_report_optimised_plans_displayobject = PackageOfPacelineComputationReportDisplayObject()

    # gather all the display objects into the dict of solution display objects
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.THIRTY_SEC_PULL]        = report_30sec_plan_display_object
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.SIXTY_SEC_PULL]         = report_60sec_plan_display_object
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.BALANCED_INTENSITY]     = report_balanced_intensity_plan_display_object
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.EVERYBODY_PULL_HARD]    = report_everybody_pull_hard_plan_display_object
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.FASTEST]                = report_fastest_full_team_plan_display_object
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE] = report_fastest_strongest_five_plan_display_object
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR] = report_fastest_strongest_four_plan_display_object

    package_report_optimised_plans_displayobject.caption = f"TTT scenarios by Brute: {capitalize_first_letter(_team_name)}"
    package_report_optimised_plans_displayobject.total_pull_sequences_examined = 999  # dummy value. not currently used
    package_report_optimised_plans_displayobject.total_compute_iterations_performed = 99999  # dummy value. not currently used

    # following line is optional. commented out because we don't want to save each plan as a separate file.
    # export_package_of_paceline_plans_as_multiple_individual_html_documents(BRUTE_DIRPATH_HTML_DOCS_BY_DATE, _team_name, package_report_optimised_plans_displayobject)

    html_file_and_blob_name = f"{make_filename_for_one_page_summary_html_doc(_team_name)}"
    summary_html_doc        = format_paceline_plans_as_one_page_html_doc(package_report_optimised_plans_displayobject, BRUTE_FOOTNOTES_HTML, css=PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET)
    saved_file_path         = save_html_document_to_hard_drive(Path(DIRPATH_BRUTE_TTT_DOCS), html_file_and_blob_name, summary_html_doc) 

    print(f"\ncommencing upload of blob {html_file_and_blob_name} to Azure\n")
    url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_BRUTE, html_file_and_blob_name, summary_html_doc)
    print(f"\npaceline scenarios uploaded to:\n - {url_of_uploaded_blob}")
    print(f"\npaceline scenarios saved to:\n - {saved_file_path}\n")
    print("\nwork complete.\n")
    print("\nyou may close the app. thank you.\n")

if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()

    try:
        _team_name = "betel" 
        _riderIDs: List[str] = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(_team_name)
        throw_if_no_internet_connection()
        asyncio.run(generate_ttt_scenarios_with_brute())

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All work executed without error.\n")

    except AlertMessageError as alert_err:
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )
        print(f"{alert_err.message}\n")

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")




