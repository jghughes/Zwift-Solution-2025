from typing import  DefaultDict
from jgh_formatting import format_number_2dp
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderContributionItem, RiderContributionDisplayObject
import logging

def populate_ridercontribution_displayobjects(riders: DefaultDict[ZsunRiderItem, RiderContributionItem]) -> DefaultDict[ZsunRiderItem, RiderContributionDisplayObject]:

    answer: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject] = DefaultDict(RiderContributionDisplayObject)

    for rider, item in riders.items():
        rider_display_object = RiderContributionDisplayObject.from_RiderContributionItem(rider, item)
        answer[rider] = rider_display_object

    return answer


def log_concise_ridercontribution_displayobjectsV2(
    test_description: str,
    result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject],
    logger: logging.Logger
) -> None:
    import pandas as pd

    logger.info(test_description)

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
            z.invalidation_reason if z.invalidation_reason else "",
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

    # Right-align the 'pull' column, left-align others
    col_formats = {col: '<' for col in df.columns}
    col_formats['pull'] = '>'  # right-align 'pull'

    # Build formatted string for logging
    formatted_rows = []
    header = "  ".join([f"{col:{col_formats[col]}15}" for col in df.columns])
    formatted_rows.append(header)
    for _, row in df.iterrows():
        formatted_row = "  ".join(
            f"{str(val):{col_formats[col]}15}" for col, val in row.items()
        )
        formatted_rows.append(formatted_row)

    logger.info("\n" + "\n".join(formatted_rows))


def log_concise_ridercontribution_displayobjects(test_description: str, result: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject], logger: logging.Logger) -> None:
    
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
            z.invalidation_reason if z.invalidation_reason else "",
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
    from constants import STANDARD_PULL_PERIODS_SEC, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

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

    dict_of_rider_pullplan_displayobjects = populate_ridercontribution_displayobjects(dict_of_rider_pullplans)

    log_concise_ridercontribution_displayobjects(f"Comparative rider metrics [RiderContributionItem]: IF capped at {MAX_INTENSITY_FACTOR}", dict_of_rider_pullplan_displayobjects, logger)


if __name__ == "__main__":
    main()
