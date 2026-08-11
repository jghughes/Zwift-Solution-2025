"""
Paceline Plan Display and Export Utilities
==========================================

This module provides utilities for formatting, logging, and exporting cycling
paceline plan results. It enables the creation of readable captions, tabular
logs, and HTML documents that summarize rider contributions and team
performance metrics.

Features:
---------
- Generate formatted captions for paceline plans, including speed, dispersion,
  and summary statistics.
- Log paceline plan details in a tabular format for analysis and debugging.
- Export individual and summary paceline plans as HTML fragments or complete
  documents, with optional CSS styling.
- Support batch export of multiple paceline plan solutions with captions and
  html_footnotes.
- Upload HTML summaries to Azure Blob Storage.

Functions:
----------
- populate_captions_for_pace_plan_in_collectively_computed_package:
    Create a formatted caption for a paceline plan.
- log_single_paceline_plan_as_pretty_table:
    Log rider contributions and plan details in a readable table.
- export_single_paceline_plan_as_html_document:
    Export a single paceline plan as an HTML fragment or file.
- export_package_of_paceline_plans_as_multiple_individual_html_documents:
    Export multiple individual paceline plans as separate HTML files.
- format_paceline_plans_as_one_page_html_doc:
    Compose a summary of all paceline plans as a single HTML document
    (returns HTML as a string).
- save_html_document_to_hard_drive:
    Save the summary HTML document to disk.
- upload_text_to_blob_storage_in_azure:
    Asynchronously upload the summary HTML document to Azure Blob Storage.

Notes:
------
- Logging is intended for main-thread usage only.

Example:
--------
    log_single_paceline_plan_as_pretty_table(report)
    export_single_paceline_plan_as_html_document(report, "plan.html", "./", "", True)
    save_html_document_to_hard_drive(summary, "summary.html", "./",
                                               "Footnotes")
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from collections import defaultdict

import pandas as pd

from paceline_display_objects import (
    PacelineComputationReportDisplayObject,
    PackageOfPacelineComputationReportDisplayObject,
)
from jgh_azure_storage_service_client import AzureStorageServiceClient
from jgh_enums import PacelinePlanTypeEnum
from jgh_formatting import format_number_1dp, format_number_with_comma_separators
from jgh_read_write import write_text_with_html_file_extension
from jgh_string import first_n_chars
from jgh_enums import PacelinePlanTypeEnum

from storage_config import format_save_filename_for_document_of_single_paceline_plan

DISPLAY_ORDER_OF_PACELINE_PLANS = [
    PacelinePlanTypeEnum.THIRTY_SEC_PULL,
    PacelinePlanTypeEnum.SIXTY_SEC_PULL,
    PacelinePlanTypeEnum.BALANCED_INTENSITY,
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD,
    PacelinePlanTypeEnum.FASTEST,
    PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE,
    PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR,
]


DICT_OF_CAPTION_PARTS_FOREACH_PACELINE_PLAN: Dict[PacelinePlanTypeEnum, Tuple[str, str]] = defaultdict(
    lambda: ("", ""),
    {
        PacelinePlanTypeEnum.THIRTY_SEC_PULL:           ("Scenario #1:","THIRTY-SECOND PULLS"),
        PacelinePlanTypeEnum.SIXTY_SEC_PULL:            ("Scenario #2:","ONE-MINUTE PULLS"),
        PacelinePlanTypeEnum.BALANCED_INTENSITY:        ("Scenario #3:","MOST BALANCED INTENSITY"),
        PacelinePlanTypeEnum.EVERYBODY_PULL_HARD:       ("Scenario #4:","HARD, EVERYBODY PULLS, NO-DROP"),
        PacelinePlanTypeEnum.FASTEST:                   ("Scenario #5:","FASTEST (FULL-TEAM) "),
        PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE:    ("Scenario #6:","FASTEST (STRONGEST-FIVE) "),
        PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR:    ("Scenario #7:","FASTEST (STRONGEST-FOUR) "),
    }
)



def get_caption_for_consolidated_document(team_name: str) -> str:
    return f"Paceline scenarios : {team_name}"



def log_single_paceline_plan_as_pretty_table(
    plan_report_displayobject: PacelineComputationReportDisplayObject,
) -> None:
    print(f"\n")
    print(f"{plan_report_displayobject.display_caption_left_aligned}    {plan_report_displayobject.display_caption_right_aligned}")

    # Prepare contents of rows_of_data - each row is a horizontal list of objects (strings, numbers etc)
    rows_of_data: List[List[object]] = []

    for rider, z in plan_report_displayobject.rider_contributions_display_objects.items():
        rows_of_data.append([
            rider.name,
            z.pretty_concatenated_racing_cat_descriptor,
            z.pretty_pull,
            z.pretty_p1_2_3_4_w,
            # z.pretty_zwiftracingapp_zpFTP_wkg,
            z.pretty_pull_comparison,
            z.pretty_average_watts,
            z.pretty_normalised_power_watts,
            z.pretty_intensity_factor,
            z.pretty_effort_constraint_violation_reason,

        ])

    column_headings = [
        "Name",
        "Race Cat",
        "Pull",
        "pull 2nd 3rd 4th",
        # "zFTP",
        "zFTP v pull",
        "Ave power",
        "NP",
        "IF",
        "Limit",
    ]

    df = pd.DataFrame(rows_of_data, columns=column_headings)

    lines_in_table: list[str] = []

    # Calculate max width for each column (header or data in any cell)
    col_widths: list[int] = []
    for col in column_headings:
        column_values: list[object] = list(df[col])
        str_lengths: list[int] = []
        for val in column_values:
            v: object = val  # type hint for val
            str_lengths.append(len(str(v)))
        max_data_width = max(str_lengths + [len(col)])
        col_widths.append(max_data_width)

    # Begin with header line
    header_parts: list[str] = []
    for i, col in enumerate(column_headings):
        header_parts.append(f"{col:^{col_widths[i]}}")
    header_line: str = "  ".join(header_parts)
    lines_in_table.append(header_line)


    # add underlining
    underline_parts: list[str] = []
    for i in range(len(column_headings)):
        underline_parts.append("-" * col_widths[i])
    underline_line: str = "  ".join(underline_parts)
    lines_in_table.append(underline_line)

    for _, row in df.iterrows():
        # Build each row as a list of formatted cell strings
        row_cells: list[str] = []
        for i in range(len(column_headings)):
            cell_value = str(row.iloc[i])
            if i == 3:
                # Right-align the 4th column (index 3) (i can't remenber why or what effect this have, if any)
                formatted_cell = f"{cell_value:>{col_widths[i]}}"
            else:
                # Left-align all other columns
                formatted_cell = f"{cell_value:<{col_widths[i]}}"
            row_cells.append(formatted_cell)
        formatted_row: str = "  ".join(row_cells)
        lines_in_table.append(formatted_row)

    print("\n" + "\n".join(lines_in_table))

def populate_title_for_pace_plan(plan_type_enum: PacelinePlanTypeEnum,
    plan_report_displayobject: PacelineComputationReportDisplayObject,
) -> None:
    caption_part_a, caption_part_b = DICT_OF_CAPTION_PARTS_FOREACH_PACELINE_PLAN[plan_type_enum]
    plan_report_displayobject.display_caption_left_aligned = f"{caption_part_a} {caption_part_b} : {format_number_1dp(plan_report_displayobject.calculated_average_speed_of_paceline_kph)}kph"

def populate_compute_statistics_for_pace_plan(
    total_pull_sequences_examined : int,
    plan_report_displayobject: PacelineComputationReportDisplayObject,
) -> None:

    plan_report_displayobject.display_caption_right_aligned = f"[sigma={format_number_1dp(100*plan_report_displayobject.calculated_dispersion_of_intensity_of_effort)}%  variations={total_pull_sequences_examined}  compute={format_number_with_comma_separators(plan_report_displayobject.computational_time)}sec  ID={first_n_chars(plan_report_displayobject.guid,3)}]"

def format_single_paceline_plan_as_html_document(
    plan_report: PacelineComputationReportDisplayObject,
    html_footnotes: str,
    include_internally_provided_css: bool,
    css: str = ""
) -> str:

    # Column headers with footnote markers where appropriate
    column_header_labels = [
        "#",
        "Name<sup>1,2</sup>",
        "Race Cat",
        "Pull<sup>3</sup>",
        "pull 2nd 3rd 4th",
        # "zFTP<sup>4</sup>",
        "zFTP v pull<sup>4</sup>",
        "Ave power",
        "NP<sup>5</sup>",
        "IF<sup>6</sup>",
        "Limit<sup>7</sup>",
    ]

     # Prepare contents of rows_of_data - each row is a horizontal list of objects (strings, numbers etc)
    rows_of_data: List[List[object]] = []

    for rider, z in plan_report.rider_contributions_display_objects.items():
        rows_of_data.append([
            z.index,
            rider.name,
            z.pretty_concatenated_racing_cat_descriptor,
            z.pretty_pull,
            z.pretty_p1_2_3_4_w,
            # z.pretty_zwiftracingapp_zpFTP_wkg,
            z.pretty_pull_comparison,
            z.pretty_average_watts,
            z.pretty_normalised_power_watts,
            z.pretty_intensity_factor,
            z.pretty_effort_constraint_violation_reason,
        ])
    df = pd.DataFrame(rows_of_data, columns=column_header_labels)
    html_table : str = df.to_html(
        index=False,
        border=1,
        classes=["rider-table"],
        escape=False,
    )

    # only apply css if this is a standalone function. If called 
    # from function that already contains the css, this css must be empty
    css_to_use = css if include_internally_provided_css else ""

    # Compose a HTML fragment. but with no <html> or <head> elements because this is a fragment included in a larger HTML document
    html_fragment = f"""
            <style>\n{css_to_use}\n</style>
        <div>
            <div class="caption-flex">
                <span class="caption-left">{plan_report.display_caption_left_aligned}</span>
                <span class="caption-right">{plan_report.display_caption_right_aligned}</span>
            </div>
            {html_table}
            {html_footnotes}
        </div>
        """
    return html_fragment

def export_package_of_paceline_plans_as_multiple_individual_html_documents(
    dirpath: Path,
    team_name: str,
    package_report_displayobject: PackageOfPacelineComputationReportDisplayObject,
    html_footnotes: str,
) -> None:
    for key in DICT_OF_CAPTION_PARTS_FOREACH_PACELINE_PLAN:
        paceline_report: PacelineComputationReportDisplayObject = package_report_displayobject.solutions[key]
        # caption_opening_element, caption_closing_element = DICT_OF_CAPTION_PARTS_FOREACH_PACELINE_PLAN[key]
        # caption: str = populate_captions_for_pace_plan_in_collectively_computed_package(caption_opening_element, caption_closing_element, paceline_report, package_report_displayobject, )
        # paceline_report.display_caption_left_aligned = caption
        log_single_paceline_plan_as_pretty_table(paceline_report)
        html_fragment = format_single_paceline_plan_as_html_document(paceline_report, html_footnotes, True)
        filename = format_save_filename_for_document_of_single_paceline_plan(team_name, key)
        write_text_with_html_file_extension(dirpath, filename, html_fragment)

def format_paceline_plans_as_one_page_html_doc(
    package_report_displayobject: Optional[PackageOfPacelineComputationReportDisplayObject],
    html_footnotes: str,
    css: str = ""
) -> str:

    if package_report_displayobject is None:
        print("No computation report provided to save as HTML.")
        return ""

    html_sections : list[str] = []

    import re

    for sol_type in DISPLAY_ORDER_OF_PACELINE_PLANS:
        solution = package_report_displayobject.solutions[sol_type]
        if not solution.rider_contributions_display_objects:
            continue

        html_fragment = format_single_paceline_plan_as_html_document(solution, "", False)

        html_fragment = re.sub(
            r'<div><strong>(.*?)</strong></div>\s*(<table[^>]*>)',
            r'\2\n<caption>\1</caption>',
            html_fragment,
            flags=re.DOTALL
        )
        html_sections.append(f'<section class="section-separator">{html_fragment}</section>')

    html_doc = f"""<!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
            <style>\n{css}\n</style>
        </head>
        <body>
            <h1>{package_report_displayobject.caption}</h1>
            {''.join(html_sections)}
            <div class="table-container">
                <div class="footnote summary-footnote">{html_footnotes}</div>
            </div>
        </body>
    </html>
    """
    return html_doc

def save_html_document_to_hard_drive(
    dir_path: Path,
    filename: str,
    hml_doc: str,
) -> Path:
    write_text_with_html_file_extension(dir_path, filename, hml_doc)
    file_path = Path(dir_path) / Path(filename)
    # file_path = dir_path / filename # Use Path object overload for joining path and filename
    return file_path

async def upload_text_to_blob_storage_in_azure(
    storage_account_name: str,
    container_name: str,
    blob_name: str,
    text: str,
) -> str| None:
    azure_client = AzureStorageServiceClient()
    url_of_uploaded_blob = await azure_client.upload_string_to_block_blob_async(
        storage_account_name, container_name, blob_name, text, False,)
    return url_of_uploaded_blob


