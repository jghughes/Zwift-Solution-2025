from typing import  DefaultDict

from jgh_formatting import format_number_2dp
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderContributionDisplayObject
import logging

def log_pretty_paceline_solution_report(
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
            z.pretty_pull_suffix,
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
        "/zFTP",
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

def save_pretty_paceline_solution_as_html_file(
    my_table_caption: str,
    result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject],
    logger: logging.Logger,
    html_filename: str = "rider_contributions.html"
) -> None:
    import pandas as pd
    import re

    print("Pandas version at runtime:", pd.__version__)
    columns = [
        "Name",
        "Race Cat",
        "zFTP<sup>1</sup>",
        "Pull<sup>2</sup>",
        "/zFTP",
        "Ave W/kg",
        "NP<sup>3</sup>",
        "IF<sup>4</sup>",
        "Limit<sup>5</sup>",
        "2nd 3rd 4th"
    ]

    data = []
    for rider, z in result.items():
        data.append([
            rider.name,
            z.concatenated_racing_cat_descriptor,
            f"{format_number_2dp(z.zwiftracingapp_zpFTP_wkg)}wkg",
            z.pretty_pull,
            z.pretty_pull_suffix,
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
        escape=False,
    )
    html_table = re.sub(
        r'(<table[^>]*>)',
        r'\1\n<caption>{}</caption>'.format(my_table_caption),
        html_table,
        count=1
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
        <sup>1</sup> zFTP: Zwift Functional Threshold Power (W/kg). zFTP metrics are displayed, but play no role in computations.<br>
        <sup>2</sup> Pull: Duration, power, and ratio to zFTP for each rider's main pull. Stronger riders are prioritised for longer pulls and are located front and rear of the paceline, protecting weaker riders in the middle. Rider strength is a metric based on 90-day-best data from ZwiftPower for five-minute and one-hour intervals.<br>
        <sup>3</sup> NP: Normalized Power.<br>
        <sup>4</sup> IF: Intensity Factor (NP as % of 90-day-best one-hour power).<br>
        <sup>5</sup> Limit: For no-drop rides, the speed of the paceline is governed by the pulling capabilities and intensity of effort of the riders working hardest to keep up. Pulling capabilities are related to individual 90-day-best data for durations ranging from 3.5 minutes up to 20 minutes.<br>
    </div>
    """

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
        }}
        .table-container {{
            width: 260mm;
            max-width: 100vw;
            margin-left: auto;
            margin-right: auto;
            overflow-x: auto;
        }}
        .rider-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.95em; /* Reduced from 1.05em */
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
        }}
        .rider-table caption {{
            caption-side: top;
            font-size: 0.95em;
            font-weight: 500; /* Reduced from bold which is 700 */
            margin-bottom: 0.5em;
            font-family: 'Roboto', Arial, sans-serif;
            text-align: left; /* Left align the caption */
        }}
        .rider-table th {{
            background-color: #e6ecf5;
            font-size: 0.95em; /* (optional: reduce font size for compactness) */
            font-weight: bold;
            text-align: center;
            border-bottom: 2px solid #444;
            padding: 6px 6px;   /* Reduced from 10px 8px */
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
            font-size: 0.95em;  /* (optional: reduce font size for compactness) */
            padding: 6px 6px;   /* Reduced from 8px 8px */
            border: 1px solid #b0b0b0;
            white-space: nowrap;
        }}
        <!--  Use Roboto for the first two columns (Name and Race Cat) in both header and data cells -->   
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
        .rider-table td:nth-child(4) {{
            text-align: right;
            font-weight: bold;
            background-color: #f0f4fa;
        }}
        .footnote {{
            font-size: 0.95em;
            color: #666;
            margin-top: 1.5em;
            font-weight: 500;
            font-family: 'Roboto', Arial, sans-serif;
            width: 100%;         /* Match table width */
            text-align: left; /* Left align the footnotes */
        }}
        .footnote sup, .rider-table th sup {{
            font-size: 0.8em;
            vertical-align: super;
            font-weight: bold;
        }}
    </style>
</head>

<body>
    <div class="table-container">
        {html_table}
    <div class="footnote">
        {footnotes}
    </div>
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

    from constants import EXERTION_INTENSITY_FACTOR
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

    dict_of_rider_pullplans = populate_rider_contributions(dict_of_rider_exertions, EXERTION_INTENSITY_FACTOR)

    dict_of_rider_pullplan_displayobjects = RiderContributionDisplayObject.from_RiderContributionItems(dict_of_rider_pullplans)

    log_pretty_paceline_solution_report(f"Rider contributions: IF capped at {EXERTION_INTENSITY_FACTOR}", dict_of_rider_pullplan_displayobjects, logger)


if __name__ == "__main__":
    main()
