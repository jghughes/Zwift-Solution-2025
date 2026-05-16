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
from typing import Dict, List

from paceline_compute_types import PacelineIngredientsItem, PacelineComputationReportItem
from paceline_computation_display_objects import (
    PacelinePlanTypeEnum,
    PacelineComputationReportDisplayObject,
    PackageOfPacelineComputationReportDisplayObject,
)
from jgh_enums import PacelinePlanTypeEnum
# from html_text import BRUTE_FOOTNOTES_HTML
from jgh_azure_storage_service_client import AzureStorageServiceClient
from jgh_formulae02 import (
    arrange_riders_by_velo_rating,
    calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph,
)
from jgh_formulae08 import (
    generate_a_single_paceline_solution_complying_with_exertion_constraints,
    log_speed_bounds_of_exertion_constrained_paceline_solutions,
)
from jgh_formulae09 import (
    populate_title_for_pace_plan,
    populate_compute_statistics_for_pace_plan,
    format_paceline_plans_as_one_page_html_doc,
    save_html_document_to_hard_drive,
    upload_text_to_blob_storage_in_azure,
)
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_string import make_pretty_count_of_bytes

from jgh_string import capitalize_first_letter
from zwift_id_base import lookup_Items_by_ZwiftID

from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_brute_dto import RiderBruteDTO, RiderBruteDtoListModel
from rider_compute_item import RiderComputeItem
from storage_config import (
    FILENAME_RIDER_BRUTE_DTO_JSON_DICT,
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    DIRPATH_BRUTE_TTT_DOCS,
    AZURE_ACCOUNTNAME_ZSUN,
    AZURE_CONTAINERNAME_BRUTE,
    AZURE_CONTAINERNAME_ZSUN,
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST,
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
        list_of_RiderItem: List[RiderComputeItem] = [
            RiderComputeItem.from_dataTransferObject(rider_brute_dto)
            for rider_brute_dto in list_of_RiderDTO]

        dict_of_RiderItem: Dict[str, RiderComputeItem] = {
            rider_compute_item.zwift_id: rider_compute_item
            for rider_compute_item in list_of_RiderItem
        }    
        print(f"\ncount of riders: {len(list_of_RiderDTO)}")
    except Exception as e:
        print(f"rider data not obtained.\n - Error message: {e}")
        return

    try:
        full_team_of_riders: List[RiderComputeItem] = lookup_Items_by_ZwiftID(_riderIDs, dict_of_RiderItem, RiderComputeItem)
    except Exception as e:
        print(f"Team '{_team_name}' not found:\n - Error message:\n - {e}")
        return

    log_speed_bounds_of_exertion_constrained_paceline_solutions(full_team_of_riders)

    # ===========================
    print(f"\ncomputing - 60_sec pull full team arranged by 1 minute strength")
    # ===========================

    # riders = arrange_riders_by_1_minute_strength(full_team_of_riders)
    riders = arrange_riders_by_velo_rating(full_team_of_riders)
    pull_periods_sec_as_list: list[float] = [60.0] * len(riders)
    paceline_ingredients = PacelineIngredientsItem(
        riders_list                     = riders,
        pull_speeds_kph              = [calculate_safe_lower_bound_speed_to_kick_off_binary_search_algorithm_kph(riders)] * len(riders),
        max_exertion_intensity_factor   = RepositoryOfTeamRosters.get_exertion_intensity_factor_for_team(_team_name),
        sequence_of_pull_periods_sec = pull_periods_sec_as_list,
        )
    report_60sec_plan : PacelineComputationReportItem = generate_a_single_paceline_solution_complying_with_exertion_constraints(paceline_ingredients)
    report_60sec_plan_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report_60sec_plan)
    populate_title_for_pace_plan(PacelinePlanTypeEnum.SIXTY_SEC_PULL, report_60sec_plan_display_object)
    populate_compute_statistics_for_pace_plan(1, report_60sec_plan_display_object)

    # # ===========================
    # log_single_paceline_plan_as_pretty_table(report_60sec_plan_display_object)
    # filename = format_save_filename_for_document_of_single_paceline_plan(_team_name, PacelinePlanTypeEnum.SIXTY_SEC_PULL)
    # html_doc = format_single_paceline_plan_as_html_document(report_60sec_plan_display_object, BRUTE_FOOTNOTES_HTML, True)
    # saved_file_path = save_html_document_to_hard_drive(Path(DIRPATH_BRUTE_TTT_DOCS), filename, html_doc)
    # print(f"\nPaceline plan saved to:\n{saved_file_path}\n")
    # # ===========================


    # ===========================
    print(f"\npublishing to html doc")
    # ===========================

    package_report_optimised_plans_displayobject = PackageOfPacelineComputationReportDisplayObject()

    # gather all the display objects into the dict of solution display objects
    package_report_optimised_plans_displayobject.solutions[PacelinePlanTypeEnum.SIXTY_SEC_PULL]         = report_60sec_plan_display_object

    package_report_optimised_plans_displayobject.caption = f"TTT scenarios by Brute: {capitalize_first_letter(_team_name)}"
    package_report_optimised_plans_displayobject.total_pull_sequences_examined = 999  # dummy value. not currently used
    package_report_optimised_plans_displayobject.total_compute_iterations_performed = 99999  # dummy value. not currently used

    # following line is optional. commented out because we don't want to save each plan as a separate file.
    # export_package_of_paceline_plans_as_multiple_individual_html_documents(BRUTE_DIRPATH_HTML_DOCS_BY_DATE, _team_name, package_report_optimised_plans_displayobject)

    html_file_and_blob_name = f"{make_filename_for_one_page_summary_html_doc(_team_name)}"
    summary_html_doc = format_paceline_plans_as_one_page_html_doc(package_report_optimised_plans_displayobject, BRUTE_FOOTNOTES_HTML,PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET)
    saved_file_path = save_html_document_to_hard_drive(Path(DIRPATH_BRUTE_TTT_DOCS), html_file_and_blob_name, summary_html_doc) 

    print(f"\ncommencing upload of blob {html_file_and_blob_name} to Azure\n")
    url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_BRUTE, html_file_and_blob_name, summary_html_doc)
    print(f"\npaceline scenarios uploaded to:\n - {url_of_uploaded_blob}")
    print(f"\npaceline scenarios saved to:\n - {saved_file_path}\n")
    print("\nwork complete.\n")
    print("\nyou may close the app. thank you.\n")

# runner
if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        _team_name = "inhibited"
        _riderIDs: List[str] = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(_team_name)
        asyncio.run(generate_ttt_scenarios_with_brute())

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

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


