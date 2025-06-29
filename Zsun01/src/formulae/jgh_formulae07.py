from typing import DefaultDict, Optional, Union
import io
from constants import DISPLAY_ORDER_OF_CONSOLIDATED_PACELINE_PLANS
from jgh_read_write import write_html_file
from jgh_formatting import format_number_2dp
from zsun_rider_item import ZsunRiderItem
from computation_classes_display_objects import (
    PacelineSolutionType,
    RiderContributionDisplayObject,
    PacelineComputationReportDisplayObject,
    PacelineSolutionsComputationReportDisplayObject,
)
import logging

def log_pretty_paceline_solution_report(
    report: PacelineComputationReportDisplayObject,
    logger: logging.Logger
) -> None:
    import pandas as pd

    logger.info(report.display_caption)

    # Prepare data rows
    data = []
    for rider, z in report.rider_contributions_display_objects.items():
        data.append([
            rider.name,
            z.pretty_concatenated_racing_cat_descriptor,
            z.pretty_pull,
            z.pretty_zwiftracingapp_zpFTP_wkg,
            z.pretty_pull_suffix,
            z.pretty_average_watts,
            z.pretty_normalised_power_watts,
            z.pretty_intensity_factor,
            z.pretty_effort_constraint_violation_reason,
            z.pretty_p2_3_4_w,
        ])

    columns = [
        "Name",
        "Race Cat",
        "Pull",
        "zFTP",
        "Pull/zFTP",
        "Ave w/kg",
        "NP",
        "IF",
        "Limit",
        "2nd 3rd 4th"
    ]

    df = pd.DataFrame(data, columns=columns)

    # Calculate max width for each column (header or any data)
    col_widths = []
    for col in columns:
        max_data_width = max([len(str(val)) for val in df[col]] + [len(col)])
        col_widths.append(max_data_width)

    # Build header (center-aligned)
    header = "  ".join(f"{col:^{col_widths[i]}}" for i, col in enumerate(columns))
    underline = "  ".join("-" * col_widths[i] for i in range(len(columns)))

    # Build rows: all left-aligned except 'pull' (index 3), which is right-aligned
    formatted_rows = [header, underline]
    for _, row in df.iterrows():
        formatted_row = "  ".join(
            f"{str(row.iloc[i]):>{col_widths[i]}}" if i == 3 else f"{str(row.iloc[i]):<{col_widths[i]}}"
            for i in range(len(columns))
        )
        formatted_rows.append(formatted_row)

    logger.info("\n" + "\n".join(formatted_rows))


def save_pretty_paceline_plan_as_html_file(
    report: PacelineComputationReportDisplayObject,
    filename : Union[str, io.StringIO], #
    dir_path : str,
    footnotes: str,
    logger: logging.Logger,
) -> None:
    import pandas as pd
    import re

    columns = [
        "Name",
        "Race Cat",
        "Pull<sup>1</sup>",
        "zFTP<sup>2</sup>",
        "Pull/zFTP",
        "Ave w/kg",
        "NP<sup>3</sup>",
        "IF<sup>4</sup>",
        "Limit<sup>5</sup>",
        "2nd 3rd 4th"
    ]

    data = []

    for rider, z in report.rider_contributions_display_objects.items():
        data.append([
            rider.name,
            z.pretty_concatenated_racing_cat_descriptor,
            z.pretty_pull,
            z.pretty_zwiftracingapp_zpFTP_wkg,
            z.pretty_pull_suffix,
            z.pretty_average_watts,
            z.pretty_normalised_power_watts,
            z.pretty_intensity_factor,
            z.pretty_effort_constraint_violation_reason,
            z.pretty_p2_3_4_w,
        ])

    df = pd.DataFrame(data, columns=columns)
    html_table = df.to_html(
        index=False,
        border=0,
        classes="rider-table",
        justify="center",
        escape=False,
    )
    html_table = re.sub(
        r'(<table[^>]*>)',
        r'\1\n<caption>{}</caption>'.format(report.display_caption),
        html_table,
        count=1
    )
    # Add a class to the "2nd 3rd 4th" header and its column cells
    html_table = re.sub(
        r'(<th[^>]*>2nd 3rd 4th</th>)',
        r'<th class="left-header">2nd 3rd 4th</th>',
        html_table
    )

    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rider Contribution Report</title>
    <!-- Google Fonts: Roboto Mono for table data, Roboto for headings, footnotes, and first two columns -->    
    <link href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            background: #fff;
            color: #222;
            padding: 6px 12px;
        }}
        .table-container {{
            width: 260mm;
            max-width: 100vw;
            margin-left: 0;
            margin-right: auto;
            overflow-x: auto;
        }}
        .rider-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.95em;
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
        }}
        .rider-table caption {{
            caption-side: top;
            font-size: 0.95em;
            font-weight: 500;
            margin-bottom: 0.5em;
            font-family: 'Roboto', Arial, sans-serif;
            text-align: left;
        }}
        .rider-table th {{
            background-color: #e6ecf5;
            font-size: 0.95em;
            font-weight: bold;
            text-align: center;
            border-bottom: 2px solid #444;
            padding: 6px 6px;
            letter-spacing: 0.02em;
            white-space: nowrap;
        }}
        .rider-table th.left-header {{
            text-align: left;
        }}
        .rider-table td.left-header {{
            text-align: left;
        }}
        .rider-table td {{
            font-size: 0.95em;
            padding: 6px 6px;
            border: 1px solid #b0b0b0;
            white-space: nowrap;
        }}
        .rider-table th:nth-child(1),
        .rider-table td:nth-child(1),
        .rider-table th:nth-child(2),
        .rider-table td:nth-child(2) {{
            font-family: 'Roboto', Arial, sans-serif !important;
            font-size: 0.95em !important;
            font-weight: 400;
        }}
        .rider-table tr:nth-child(even) td {{
            background-color: #f7fafd;
        }}
        .rider-table tr:hover td {{
            background-color: #dbeafe;
        }}
        .rider-table td:nth-child(3) {{
            text-align: right;
            font-weight: bold;
            background-color: #f0f4fa;
        }}
        .rider-table td:nth-child(4) {{
            text-align: right;
        }}
        .rider-table td:nth-child(5) {{
            text-align: right;
        }}
        .rider-table td:nth-child(7) {{
            text-align: right;
        }}
        .rider-table td:nth-child(8) {{
            text-align: right;
        }}
        .footnote {{
            font-size: 0.95em;
            color: #666;
            margin-top: 1.5em;
            font-weight: 500;
            font-family: 'Roboto', Arial, sans-serif;
            width: 100%;
            text-align: left;
        }}
        .footnote-item {{
            margin-bottom: 0.5em;
            padding-left: 2em;
            text-indent: -2em;
        }}
        .footnote sup, .rider-table th sup  {{
            font-size: 0.8em;
            vertical-align: super;
            font-weight: bold;
        }}        
    </style>
</head>

<body>
    <div class="table-container">
        {html_table}
    </div>
    {footnotes}
</body></html>
"""

    # Determine if filename is a string (file path) or a file-like object
    if isinstance(filename, str):
        write_html_file(html_doc, filename, dir_path)
        # logger.info(f"\nPaceline pull-plan written and saved to hard-drive: path={dir_path} file={filename}")
    else:
        # Assume file-like object (e.g., io.StringIO)
        filename.write(html_doc)
        # logger.info(f"\nPaceline pull-plan written to file-like object (not saved to disk).")

def save_all_pretty_paceline_plans_in_consolidated_html_file(
    computation_report_display_object: Optional[PacelineSolutionsComputationReportDisplayObject],
    filename: str,
    dir_path: str,
    html_footnotes: str,
    logger: logging.Logger,

) -> None:

    if computation_report_display_object is None:
        logger.error("No computation report provided to save as HTML.")
        return


    html_sections : list[str] = []
    for sol_type in DISPLAY_ORDER_OF_CONSOLIDATED_PACELINE_PLANS:
        solution = computation_report_display_object.solutions[sol_type]
        if not solution.rider_contributions_display_objects:
            continue
        # Generate HTML for this solution using the single-solution HTML function
        buf= io.StringIO()
        save_pretty_paceline_plan_as_html_file(solution,
            filename=buf,  # We'll capture the HTML as a string
            dir_path=dir_path,  # Directory path for saving the file
            footnotes="",  # Don't repeat footnotes in each section
            logger=logger,
        )
        html_sections.append(f'<section class="section-separator">{buf.getvalue()}</section>')
    # Combine all html_sections and write to file
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Paceline Plans</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', Arial, sans-serif;
            background: #fff;
            color: #222;
            margin: 0;
            padding-left: 18px;
        }}
        h1 {{
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 1.05em;
            font-weight: 700;
            color: #1a365d;
            letter-spacing: 0.01em;
        }}
        .section-separator {{
            margin: 32px 0;
        }}
    </style>
</head>
<body>
    <h1>{computation_report_display_object.caption}</h1>
    {''.join(html_sections)}
    <div class="footnote">{html_footnotes}</div>
</body>
</html>
"""
    write_html_file(full_html, filename, dir_path)

    logger.info(f"\nPaceline plans written to consolidated document and saved to hard-drive: path={dir_path}/{filename}")


def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)

    from constants import EXERTION_INTENSITY_FACTOR_LIMIT
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae06 import populate_rider_contributions
    from zsun_rider_dto import ZsunRiderDTO

    # Example: Instantiate riders using the Config class
    example_riders_data = [
        # ZsunRiderItem.Config.json_schema_extra["meridithl"],
        ZsunRiderItem.Config.json_schema_extra["melissaw"],
        ZsunRiderItem.Config.json_schema_extra["richardm"],
        # ZsunRiderItem.Config.json_schema_extra["davek"],
        # ZsunRiderItem.Config.json_schema_extra["huskyc"],
        # ZsunRiderItem.Config.json_schema_extra["scottm"],
        ZsunRiderItem.Config.json_schema_extra["johnh"],
        # ZsunRiderItem.Config.json_schema_extra["joshn"],
        # ZsunRiderItem.Config.json_schema_extra["brent"],
        # ZsunRiderItem.Config.json_schema_extra["coryc"],
        # ZsunRiderItem.Config.json_schema_extra["davide"],
    ]

    # Convert example data to ZsunRiderItem instances
    riders = [
        ZsunRiderItem.from_dataTransferObject(ZsunRiderDTO.model_validate(data))
        for data in example_riders_data
    ]


    pull_durations = [30.0, 0.0, 30.0] # duration array MUST be same len as riders (or longer), and the sequence MUST match the rider order in the paceline
    pull_speeds_kph = [40.0] * len(riders)
    pull_speed = 40.0  # Example speed in kph
    pull_speeds_kph = [pull_speed] * len(riders)

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    dict_of_rider_pullplans = populate_rider_contributions(dict_of_rider_exertions, EXERTION_INTENSITY_FACTOR_LIMIT)

    dict_of_rider_pullplan_displayobjects = RiderContributionDisplayObject.from_RiderContributionItems(dict_of_rider_pullplans)

    log_pretty_paceline_solution_report(f"Rider contributions: IF capped at {EXERTION_INTENSITY_FACTOR_LIMIT}", dict_of_rider_pullplan_displayobjects, logger)


if __name__ == "__main__":
    main()
