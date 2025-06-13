from typing import  DefaultDict
from jgh_formatting import format_number_2dp
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderContributionItem, RiderContributionDisplayObject
import logging

def populate_rider_contribution_displayobjects(riders: DefaultDict[ZsunRiderItem, RiderContributionItem]) -> DefaultDict[ZsunRiderItem, RiderContributionDisplayObject]:

    answer: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject] = DefaultDict(RiderContributionDisplayObject)

    for rider, item in riders.items():
        rider_display_object = RiderContributionDisplayObject.from_RiderContributionItem(rider, item)
        answer[rider] = rider_display_object

    return answer


def log_rider_contribution_displayobjects(test_description: str, result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject], logger: logging.Logger) -> None:
    
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, z in result.items():
        table.append([
            rider.name,
            z.concatenated_racing_cat_descriptor,
            f"{format_number_2dp(z.zwiftracingapp_zpFTP_wkg)}wkg",
            z.pretty_pull,
            z.pretty_average_watts,
            f"{round(z.normalised_power_watts)}w",
            f"{round(100*z.intensity_factor)}%",
            z.effort_constraint_violation_reason if z.effort_constraint_violation_reason else "",
            z.pretty_p2_3_4_w, 

        ])

    headers = [
        "name",
        "cat",
        "zFTP", 
        "pull", 
        "ave",
        "NP",
        "IF",
        "limit",
        "  2   3   4", 

    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple", stralign="left", disable_numparse=True))


def log_rider_contribution_displayobjectsV2(
    test_description: str,
    result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject],
    logger: logging.Logger
) -> None:
    logger.info(test_description)

    # Prepare data rows
    data = []
    for rider, z in result.items():
        data.append([
            rider.name,
            z.concatenated_racing_cat_descriptor,
            f"{format_number_2dp(z.zwiftracingapp_zpFTP_wkg)}wkg",
            z.pretty_pull,
            z.pretty_average_watts,
            f"{round(z.normalised_power_watts)}w",
            f"{round(100*z.intensity_factor)}%",
            z.effort_constraint_violation_reason if z.effort_constraint_violation_reason else "",
            z.pretty_p2_3_4_w,
        ])

    columns = [
        "name",
        "cat",
        "zFTP",
        "pull",
        "ave",
        "NP",
        "IF",
        "limit",
        "  2   3   4",
    ]

    # Calculate max width for each column (header or any data)
    col_widths = []
    for col_idx, col in enumerate(columns):
        max_data_width = max([len(str(row[col_idx])) for row in data] + [len(col)])
        col_widths.append(max_data_width)

    # Build header (center-aligned)
    header = "  ".join(f"{col:^{col_widths[i]}}" for i, col in enumerate(columns))
    # Build underline
    underline = "  ".join("-" * col_widths[i] for i in range(len(columns)))

    # Build rows: all left-aligned except 'pull' (index 3), which is right-aligned
    formatted_rows = [header, underline]
    for row in data:
        formatted_row = "  ".join(
            f"{str(val):>{col_widths[i]}}" if i == 3 else f"{str(val):<{col_widths[i]}}"
            for i, val in enumerate(row)
        )
        formatted_rows.append(formatted_row)

    logger.info("\n" + "\n".join(formatted_rows))


def log_rider_contribution_displayobjectsV3(
    test_description: str,
    result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject],
    logger: logging.Logger
) -> None:
    import pandas as pd

    logger.info(test_description)

    # Prepare data rows
    data = []
    for rider, z in result.items():
        data.append([
            rider.name,
            z.concatenated_racing_cat_descriptor,
            f"{format_number_2dp(z.zwiftracingapp_zpFTP_wkg)}wkg",
            z.pretty_pull,
            z.pretty_average_watts,
            f"{round(z.normalised_power_watts)}w",
            f"{round(100*z.intensity_factor)}%",
            z.effort_constraint_violation_reason if z.effort_constraint_violation_reason else "",
            z.pretty_p2_3_4_w,
        ])

    columns = [
        "name",
        "cat",
        "zFTP",
        "pull",
        "ave",
        "NP",
        "IF",
        "limit",
        "  2   3   4",
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

def save_rider_contributions_as_html_file(
    test_description: str,
    result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject],
    logger: logging.Logger,
    html_filename: str = "rider_contributions.html"
) -> None:
    import pandas as pd
    import re

    columns = [
        "Name",
        "Race Cat",
        "zFTP<sup>1</sup>",
        "Pull<sup>2</sup>",
        "Ave W/kg",
        "NP<sup>3</sup>",
        "IF<sup>4</sup>",
        "Limit",
        "2nd 3rd 4th"
    ]

    data = []
    for rider, z in result.items():
        data.append([
            rider.name,
            z.concatenated_racing_cat_descriptor,
            f"{format_number_2dp(z.zwiftracingapp_zpFTP_wkg)}wkg",
            z.pretty_pull,
            z.pretty_average_watts,
            f"{round(z.normalised_power_watts)}w",
            f"{round(100*z.intensity_factor)}%",
            z.effort_constraint_violation_reason if z.effort_constraint_violation_reason else "",
            z.pretty_p2_3_4_w,
        ])

    df = pd.DataFrame(data, columns=columns)
    html_table = df.to_html(
        index=False,
        border=0,
        classes="rider-table",
        justify="center",
        escape=False
    )

    # Add a class to the "2nd 3rd 4th" header and its column cells
    html_table = re.sub(
        r'(<th[^>]*>2nd 3rd 4th</th>)',
        r'<th class="left-header">2nd 3rd 4th</th>',
        html_table
    )
    # Optionally, add more column classes as needed

    footnotes = """
    <div class="footnote">
        <sup>1</sup> zFTP: Zwift Functional Threshold Power (W/kg).<br>
        <sup>2</sup> Pull: Duration, power, and ratio to zFTP for each rider's main pull.<br>
        <sup>3</sup> NP: Normalized Power.<br>
        <sup>4</sup> IF: Intensity Factor (NP as % of 1-hour power).<br>
    </div>
    """

    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rider Contribution Report</title>
    <!-- Google Fonts: Roboto Mono -->
    <link href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            background: #fff;
            color: #222;
        }}
        .table-container {{
            overflow-x: auto;
            width: auto;
            max-width: 100vw;
            margin-bottom: 2em;
        }}
        .rider-table {{
            border-collapse: collapse;
            width: auto;           /* Let table shrink to fit content */
            max-width: none;
            font-size: 1.05em;
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
        }}
        .rider-table caption {{
            caption-side: top;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 0.5em;
        }}
        .rider-table th {{
            background-color: #e6ecf5;
            font-size: 1em;
            font-weight: bold;
            text-align: center;
            border-bottom: 2px solid #444;
            padding: 10px 8px;
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
            font-size: 1em;
            padding: 8px 8px;
            border: 1px solid #b0b0b0;
            white-space: nowrap;
        }}
        .rider-table tr:nth-child(even) td {{
            background-color: #f7fafd;
        }}
        .rider-table tr:hover td {{
            background-color: #dbeafe;
        }}
        .rider-table td:nth-child(4) {{
            text-align: right;
            font-weight: bold;
            background-color: #f0f4fa;
        }}
        .footnote {{
            font-size: 0.9em;
            color: #666;
            margin-top: 1.5em;
        }}
        .footnote sup, .rider-table th sup {{
            font-size: 0.8em;
            vertical-align: super;
        }}
    </style>
</head>
<body>
    <h2>{test_description}</h2>
    <div class="table-container">
        {html_table}
    </div>
    {footnotes}
</body>
</html>
"""

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_doc)

    logger.info(f"Rider contribution HTML report written to: {html_filename}")


def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger("numba").setLevel(logging.ERROR)


    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae06 import populate_rider_contributions

    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs    
    from constants import ARRAY_OF_STANDARD_PULL_PERIODS_SEC, MAX_EXERTION_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

    dict_of_zwiftrideritem = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)

    meredith_leubner : ZsunRiderItem = dict_of_zwiftrideritem['1707548'] # davek
    johnh : ZsunRiderItem = dict_of_zwiftrideritem['1884456'] # barryb
    matt_steeve : ZsunRiderItem = dict_of_zwiftrideritem['1024413'] # markb
    roland_segal : ZsunRiderItem = dict_of_zwiftrideritem['384442'] # richardm
    lynsey_segal : ZsunRiderItem = dict_of_zwiftrideritem['383480'] # lynseys
    melissa_warwick : ZsunRiderItem = dict_of_zwiftrideritem['1657744'] # joshn
    
    riders : list[ZsunRiderItem] = [meredith_leubner, johnh, matt_steeve, roland_segal, lynsey_segal, melissa_warwick]


    pull_speeds_kph = [38.8, 38.8,38.8, 38.8, 38.8, 38.8, 38.8, 38.8]
    pull_durations = [240.0, 120.0, 60.0, 30.0, 60.0, 180.0]


    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    dict_of_rider_pullplans = populate_rider_contributions(dict_of_rider_exertions)

    dict_of_rider_pullplan_displayobjects = populate_rider_contribution_displayobjects(dict_of_rider_pullplans)

    log_rider_contribution_displayobjects(f"Comparative rider metrics [RiderContributionItem]: IF capped at {MAX_EXERTION_INTENSITY_FACTOR}", dict_of_rider_pullplan_displayobjects, logger)


if __name__ == "__main__":
    main()
