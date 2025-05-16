from zsun_rider_item import ZsunRiderItem
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_units_ticks,set_y_axis_units_ticks
from jgh_read_write import write_pandas_dataframe_as_xlsx
from handy_utilities import *
from computation_classes import RiderWorkAssignmentItem, RiderExertionItem

from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae04 import populate_rider_work_assignments, log_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions, log_rider_exertions

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO



ZSUN01_BETEL_PROFILES_FILE_NAME = "betel_ZsunRiderItems.json"
ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

barryb ='5490373' #ftp 273
johnh ='1884456' #ftp 240 zmap 292
lynseys ='383480' #ftp 201
joshn ='2508033' #ftp 260
richardm ='1193' # ftp 200
markb ='5530045' #ftp 280
davek="3147366" #ftp 276 critical_power 278
husky="5134" #ftp 268
scottm="11526" #ftp 247
timr= "5421258" #ftp 380
tom_bick= "11741" #ftp 303 critical_power 298
bryan_bumpas = "9011" #ftp 214
matt_steeve = "1024413"
giao_nguyen = "183277" #ftp 189
meridith_leubner ="1707548" #ftp 220
melissa_warwick = "1657744" #ftp 213
brandi_steeve = "991817" #ftp 196
selena = "2682791" #ftp 214
steve_seiler = "6142432" #ftp 270
david_evanetich= '4945836'
coryc = "5569057"

# choose a rider to model
zwiftID = lynseys


def fmt(x):
    return f"{x:.2g}"

def log_rider_one_hour_speeds(riders: list[ZsunRiderItem], logger: logging.Logger):
    from tabulate import tabulate

    table = []
    for rider in riders:
        table.append([
            rider.name,
            fmt(rider.calculate_strength_wkg()),
            fmt(rider.get_zwiftracingapp_zpFTP_wkg()),
            fmt(rider.get_zsun_one_hour_wkg()),
            fmt(rider.calculate_speed_at_one_hour_watts())
        ])

    headers = [
        "Rider",
        "Strength (w/kg)",
        "ZRA ZP FTP (w/kg)",
        "ZSUN 1hr (w/kg)",
        "1hr Speed (kph)"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


def main():
    dict_of_zsunrideritems = read_dict_of_zsunriderItems(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    riders : list[ZsunRiderItem] = [
        dict_of_zsunrideritems[tom_bick],
        dict_of_zsunrideritems[davek],
        dict_of_zsunrideritems[husky],
        dict_of_zsunrideritems[timr],
        dict_of_zsunrideritems[meridith_leubner],
        dict_of_zsunrideritems[johnh],
    ]

    # Sort riders by 1hr speed (descending)
    riders_sorted = sorted(
        riders,
        key=lambda r: r.calculate_speed_at_one_hour_watts(),
        reverse=True
    )

    log_rider_one_hour_speeds(riders_sorted, logger)

    riders = arrange_riders_in_optimal_order(riders)

    seed_speed = min(riders, key=lambda r: r.calculate_speed_at_one_hour_watts()).calculate_speed_at_one_hour_watts()

    pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone
    pull_speeds_kph = [seed_speed] * len(riders)

    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    log_rider_work_assignments("Example riders",work_assignments, logger)

    rider_exertions = populate_rider_exertions(work_assignments)

    log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    log_rider_answer_items("7-riders @40kph", rider_answer_items_with_cp_and_w_prime, logger)


if __name__ == "__main__":
    main()


