from typing import Optional, Union
import io
from jgh_string import first_n_chars
from jgh_formatting import format_number_1dp, format_number_comma_separators
from paceline_plan_display_ingredients import DISPLAY_ORDER_OF_SUMMARY_OF_PACELINE_PLANS
from html_css import  PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET
from jgh_read_write import write_html_file
from zsun_rider_item import ZsunItem
from computation_classes_display_objects import RiderContributionDisplayObject, PacelineComputationReportDisplayObject, PacelineSolutionsComputationReportDisplayObject
import logging


def make_pretty_caption_for_a_paceline_plan(
    title: str,
    report: PacelineComputationReportDisplayObject,
    overall_report: PacelineSolutionsComputationReportDisplayObject,
    suffix: Optional[str],
) -> str:
    if suffix:
        return (
            f"\n{title} "
            f"{format_number_1dp(report.calculated_average_speed_of_paceline_kph)}kph "
            f"{suffix} "
            f"[sigma={format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% "
            f"n={format_number_comma_separators(overall_report.total_pull_sequences_examined)} "
            f"t={format_number_comma_separators(overall_report.computational_time)}sec "
            # f"itr={format_number_comma_separators(report.compute_iterations_performed_count)}"
            f"ID={first_n_chars(report.guid,3)}]"
        )
    else:
        return (
            f"\n{title} "
            f"{format_number_1dp(report.calculated_average_speed_of_paceline_kph)} kph "
            f"[sigma={format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% "
            f"sigma={format_number_1dp(100*report.calculated_dispersion_of_intensity_of_effort)}% "
            f"n={format_number_comma_separators(overall_report.total_pull_sequences_examined)} "
            f"t={format_number_comma_separators(overall_report.computational_time)}sec"
            # f"itr={format_number_comma_separators(report.compute_iterations_performed_count)}"
            f"ID={first_n_chars(report.guid,3)}]"
        )


def log_a_paceline_plan(
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
            z.pretty_p2_3_4_w,
            z.pretty_zwiftracingapp_zpFTP_wkg,
            z.pretty_pull_suffix,
            z.pretty_average_watts,
            z.pretty_normalised_power_watts,
            z.pretty_intensity_factor,
            z.pretty_effort_constraint_violation_reason,

        ])

    columns = [
        "Name",
        "Race Cat",
        "Pull",
        "2nd 3rd 4th",
        "zFTP",
        "Pull/zFTP",
        "Ave w/kg",
        "NP",
        "IF",
        "Limit",
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


def save_a_paceline_plan_as_html(
    report: PacelineComputationReportDisplayObject,
    filename: Union[str, io.StringIO],
    dir_path: str,
    footnotes: str,
    include_internally_provided_css: bool
) -> None:
    import pandas as pd

    # Minimal columns and data
    column_header_labels = [
        "Name",
        "Race Cat",
        "Pull<sup>1</sup>",
        "2nd 3rd 4th",
        "zFTP<sup>2</sup>",
        "Pull/zFTP",
        "Ave w/kg",
        "NP<sup>3</sup>",
        "IF<sup>4</sup>",
        "Limit<sup>5</sup>",
    ]
    data = []
    for rider, z in report.rider_contributions_display_objects.items():
        data.append([
            rider.name,
            z.pretty_concatenated_racing_cat_descriptor,
            z.pretty_pull,
            z.pretty_p2_3_4_w,
            z.pretty_zwiftracingapp_zpFTP_wkg,
            z.pretty_pull_suffix,
            z.pretty_average_watts,
            z.pretty_normalised_power_watts,
            z.pretty_intensity_factor,
            z.pretty_effort_constraint_violation_reason,
        ])
    df = pd.DataFrame(data, columns=column_header_labels)
    html_table : str = df.to_html(
        index=False,
        border=1,
        classes=["rider-table"],
        escape=False,
    )

    # only apply css if this is a standalone function. If called 
    # from function that already contains the css, this css must be empty
    css = PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET if include_internally_provided_css else ""

    # Compose a HTML fragment. but with no <html> or <head> elements because this is a fragment included in a larger HTML document
    html_fragment = f"""
        {css}
        <div>
            <div><strong>{report.display_caption}</strong></div>
            {html_table}
            <div>{footnotes}</div>
        </div>
        """

    if isinstance(filename, str):
        write_html_file(html_fragment, filename, dir_path)
    else:
        filename.write(html_fragment)


def save_summary_of_all_paceline_plans_as_html(
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

    import re

    for sol_type in DISPLAY_ORDER_OF_SUMMARY_OF_PACELINE_PLANS:
        solution = computation_report_display_object.solutions[sol_type]
        if not solution.rider_contributions_display_objects:
            continue
        buf = io.StringIO()
        save_a_paceline_plan_as_html(solution, filename=buf, dir_path=dir_path, footnotes="",  include_internally_provided_css=False)
        fragment = buf.getvalue()
        # Move caption into table
        fragment = re.sub(
            r'<div><strong>(.*?)</strong></div>\s*(<table[^>]*>)',
            r'\2\n<caption>\1</caption>',
            fragment,
            flags=re.DOTALL
        )
        html_sections.append(f'<section class="section-separator">{fragment}</section>')


    full_html = f"""<!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Paceline Plans</title>
            <link href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
            {PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET}
        </head>
        <body>
            <h1>{computation_report_display_object.caption}</h1>
            {''.join(html_sections)}
            <div class="table-container">
                <div class="footnote summary-footnote">{html_footnotes}</div>
            </div>
        </body>
    </html>
    """

    write_html_file(full_html, filename, dir_path)

    logger.info(f"\nPaceline plans written to summary document and saved to hard-drive: path={dir_path}/{filename}")


def main() -> None:

    from constants import EXERTION_INTENSITY_FACTOR_LIMIT
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae06 import populate_rider_contributions
    from zsun_rider_dto import ZsunDTO

    # Example: Instantiate riders using the Config class
    example_riders_data = [
        # ZsunItem.Config.json_schema_extra["meridithl"],
        ZsunItem.Config.json_schema_extra["melissaw"],
        ZsunItem.Config.json_schema_extra["richardm"],
        # ZsunItem.Config.json_schema_extra["davek"],
        # ZsunItem.Config.json_schema_extra["huskyc"],
        # ZsunItem.Config.json_schema_extra["scottm"],
        ZsunItem.Config.json_schema_extra["johnh"],
        # ZsunItem.Config.json_schema_extra["joshn"],
        # ZsunItem.Config.json_schema_extra["brent"],
        # ZsunItem.Config.json_schema_extra["coryc"],
        # ZsunItem.Config.json_schema_extra["davide"],
    ]

    # Convert example data to ZsunItem instances
    riders = [
        ZsunItem.from_dataTransferObject(ZsunDTO.model_validate(data))
        for data in example_riders_data
    ]


    pull_durations = [30.0, 0.0, 30.0] # duration array MUST be same len as riders (or longer), and the sequence MUST match the rider order in the paceline
    pull_speeds_kph = [40.0] * len(riders)
    pull_speed = 40.0  # Example speed in kph
    pull_speeds_kph = [pull_speed] * len(riders)

    dict_of_rider_work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    dict_of_rider_exertions = populate_rider_exertions(dict_of_rider_work_assignments)

    dict_of_rider_contributions = populate_rider_contributions(dict_of_rider_exertions, EXERTION_INTENSITY_FACTOR_LIMIT)

    dict_of_rider_pullplan_displayobjects = RiderContributionDisplayObject.from_RiderContributionItems(dict_of_rider_contributions)

    log_a_paceline_plan(f"Rider contributions: IF capped at {EXERTION_INTENSITY_FACTOR_LIMIT}", dict_of_rider_pullplan_displayobjects, logger)


if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger("numba").setLevel(logging.ERROR)

    main()

