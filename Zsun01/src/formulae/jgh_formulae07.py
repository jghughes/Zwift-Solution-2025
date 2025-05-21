from typing import  DefaultDict
from jgh_formatting import round_to_nearest_10
from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem
from zsun_rider_pullplan_displayobject import RiderPullPlanDisplayObject
import logging

def populate_pullplan_displayobjects(riders: DefaultDict[ZsunRiderItem, RiderPullPlanItem]) -> DefaultDict[ZsunRiderItem, RiderPullPlanDisplayObject]:

    answer: DefaultDict[ZsunRiderItem, RiderPullPlanDisplayObject] = DefaultDict(RiderPullPlanDisplayObject)

    for rider, item in riders.items():
        rider_display_object = RiderPullPlanDisplayObject.from_RiderPullPlanItem(rider, item)
        answer[rider] = rider_display_object

    return answer

def log_concise_pullplan_displayobjects(test_description: str, result: DefaultDict[ZsunRiderItem, RiderPullPlanDisplayObject], logger: logging.Logger) -> None:
    
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, z in result.items():
        table.append([
            rider.name, 
            z.p1_duration,
            round_to_nearest_10(z.p1_w), 
            z.pretty_p2_3_4_w, 
            round(z.zsun_one_hour_watts),
            round(z.zsun_one_hour_watts/rider.weight_kg,1),
            round(z.p1_wkg,1),
            round(z.p1_ratio_to_1hr_w,1),
            round(z.np_intensity_factor,2),
            z.diagnostic_message if z.diagnostic_message else ""

        ])

    headers = [
        "",
        "sec", 
        "p1", 
        "  2   3   4", 
        "FTP", 
        "FTP", 
        "p1",
        "x",
        "IF",
        "limit"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))

def log_full_pullplan_displayobjects(test_description: str, result: DefaultDict[ZsunRiderItem, RiderPullPlanDisplayObject], logger: logging.Logger) -> None:
    
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, z in result.items():
        table.append([
            z.name,
            z.concatenated_racing_cat_descriptor,
            z.zwift_zrs,
            z.zwift_zrs_cat,
            z.zwiftracingapp_zpFTP_cat,
            z.zwiftracingapp_pretty_cat_descriptor,
            z.zwiftracingapp_zpFTP,
            z.zwiftracingapp_zpFTP_wkg,
            z.speed_kph,
            z.p1_duration,
            z.p1_wkg,
            z.p1_ratio_to_1hr_w,
            z.p1_w,
            z.p2_w,
            z.p3_w,
            z.p4_w,
            z.pretty_p2_3_4_w,
            z.zsun_one_hour_watts,
            z.p__w,
            z.np_intensity_factor,
            z.diagnostic_message
        ])
    
        headers = [
            "name",
            "concatenated_racing_cat_descriptor",
            "zwift_zrs",
            "zwift_zrs_cat",
            "zwiftracingapp_zpFTP_cat",
            "zwiftracingapp_pretty_cat_descriptor",
            "zwiftracingapp_zpFTP",
            "zwiftracingapp_zpFTP_wkg",
            "speed_kph",
            "p1_duration",
            "p1_wkg",
            "p1_ratio_to_1hr_w",
            "p1_w",
            "p2_w",
            "p3_w",
            "p4_w",
            "pretty_p2_3_4_w",
            "zsun_one_hour_watts",
            "p__w",
            "np_intensity_factor",
            "diagnostic_message"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))


def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae06 import populate_pull_plan_from_rider_exertions

    from handy_utilities import read_dict_of_zsunriderItems

    RIDERDATA_FILE_NAME = "betel_ZsunRiderItems.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zsunriderItems(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)


    barryb : ZsunRiderItem = dict_of_zwiftrideritem['5490373'] # barryb
    johnh : ZsunRiderItem = dict_of_zwiftrideritem['1884456'] # johnh
    lynseys : ZsunRiderItem = dict_of_zwiftrideritem['383480'] # lynseys
    joshn : ZsunRiderItem = dict_of_zwiftrideritem['2508033'] # joshn
    richardm : ZsunRiderItem = dict_of_zwiftrideritem['1193'] # richardm

    pull_speeds_kph = [42.0, 42.0, 42.0, 42.0, 42.0]
    pull_durations = [30.0, 30.0, 30.0, 30.0, 30.0]
    riders : list[ZsunRiderItem] = [barryb, johnh, lynseys, joshn, richardm]

    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    dict_of_rider_pullplans = populate_pull_plan_from_rider_exertions(rider_exertions)


    dict_of_rider_pullplan_displayobjects = populate_pullplan_displayobjects(dict_of_rider_pullplans)

    log_concise_pullplan_displayobjects("Comparative rider metrics [RiderPullPlanItem]:", dict_of_rider_pullplan_displayobjects, logger)


if __name__ == "__main__":
    main()
