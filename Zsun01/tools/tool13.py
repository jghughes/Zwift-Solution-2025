from typing import Tuple

from matplotlib.pylab import f
from zsun_rider_item import ZsunRiderItem
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_units_ticks,set_y_axis_units_ticks
from jgh_read_write import write_pandas_dataframe_as_xlsx
from handy_utilities import *
from computation_classes import RiderAnswerItem

from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae04 import populate_rider_work_assignments, log_rider_work_assignments
from jgh_formulae05 import populate_rider_exertions, log_rider_exertions
from jgh_formulae06 import populate_rider_answeritems, log_rider_answer_items

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

permitted_pull_durations = [30.0, 60.0, 120.0, 180.0, 240.0] # in seconds

def fmt(x : Union[int, float]):
    return f"{x:.2g}"

def fmtl(x : Union[int, float]):
    return f"{x:.4g}"

def log_rider_one_hour_speeds(riders: list[ZsunRiderItem], logger: logging.Logger):
    from tabulate import tabulate

    table = []
    for rider in riders:
        table.append([
            rider.name,
            fmt(rider.calculate_strength_wkg()),
            fmt(rider.get_zwiftracingapp_zpFTP_wkg()),
            fmt(rider.get_zsun_one_hour_wkg()),
            fmt(rider.calculate_speed_at_one_hour_watts()),
            fmt(rider.zsun_one_hour_watts),
            fmt(rider.calculate_speed_at_permitted_30sec_pull_watts()),
            fmt(rider.get_permitted_30sec_pull_watts()),
        ])

    headers = [
        "Rider",
        "Pull 2m (w/kg)",
        "zFTP (w/kg)",
        "1hr (w/kg)",
        "1hr (kph)",
        "1hr (W)",
        "Pull 30s (kph)",
        "Pull 30s (W)",
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


def calculate_lower_bound_pull_speed(riders: list[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    slowest_rider = riders[0]
    slowest_duration = 30.0
    slowest_speed = 100.0  # Arbitrarily high speed


    duration_methods = [
        (30.0, 'calculate_speed_at_permitted_30sec_pull_watts'),
        (60.0, 'calculate_speed_at_permitted_1_minute_pull_watts'),
        (120.0, 'calculate_speed_at_permitted_2_minute_pull_watts'),
        (180.0, 'calculate_speed_at_permitted_3_minute_pull_watts'),
        (240.0, 'calculate_speed_at_permitted_4_minute_pull_watts'),
    ]

    for rider in riders:
        for duration, method_name in duration_methods:
            speed = getattr(rider, method_name)()
            if speed < slowest_speed:
                slowest_speed = speed
                slowest_rider = rider
                slowest_duration = duration

    return slowest_rider, slowest_duration, slowest_speed

def calculate_lower_bound_speed_at_one_hour_watts(riders: list[ZsunRiderItem]) -> Tuple[ZsunRiderItem, float, float]:
    # (rider, duration_sec, speed_kph)
    slowest_rider = riders[0]
    slowest_duration = 3600.0  # 1 hour in seconds
    slowest_speed = slowest_rider.calculate_speed_at_one_hour_watts()

    for rider in riders:
        speed = rider.calculate_speed_at_one_hour_watts()
        if speed < slowest_speed:
            slowest_speed = speed
            slowest_rider = rider
            # duration is always 1 hour for this function
            slowest_duration = 3600.0

    return slowest_rider, slowest_duration, slowest_speed


def populate_rider_answers(riders: List[ZsunRiderItem], pull_durations: List[float], pull_speeds_kph: List[float])-> defaultdict[ZsunRiderItem, RiderAnswerItem]:
    
    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    # log_rider_work_assignments("Example riders",work_assignments, logger)

    rider_exertions = populate_rider_exertions(work_assignments)

    # log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    rider_answer_items = do_diagnostic(rider_answer_items)

    # log_rider_answer_items(f"{len(riders)} riders in paceline", rider_answer_items, logger)


    return rider_answer_items

def do_diagnostic(rider_answers: defaultdict[ZsunRiderItem, RiderAnswerItem]) -> defaultdict[ZsunRiderItem, RiderAnswerItem]:
    for rider, answer in rider_answers.items():
        msg = ""
        # Step 1: Intensity factor checks
        if answer.np_intensity_factor >= 1.0:
            msg += "halt. intensity factor > 1.0. "
        # elif answer.np_intensity_factor >= 0.95:
        #     msg += "warning. intensity factor >= 0.95. "

        # Step 2: Pull watt limit checks
        pull_limit = rider.lookup_permissable_pull_watts(answer.p1_duration)
        if answer.p1_w >= pull_limit:
            msg += "halt. pull watts exceed limit."
        # elif answer.p1_w >= 0.95 * pull_limit:
        #     msg += "warning. pull watts >= .95 of limit."

        answer.diagnostic_message = msg
    return rider_answers

def iterate_until_halted (riders: list[ZsunRiderItem], pull_durations: list[float], pull_speeds_kph: list[float]) -> tuple[int, defaultdict[ZsunRiderItem, RiderAnswerItem], ZsunRiderItem]:

    rider_answer_items : defaultdict[ZsunRiderItem, RiderAnswerItem] = populate_rider_answers(riders, pull_durations, pull_speeds_kph)

    # iterate until a rider has a diagnostic message
    i = 1
    current_speed = round(pull_speeds_kph[0], 1)

    while True:
        # break if any rider has a diagnostic message
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            halting_rider = next(rider for rider, answer in rider_answer_items.items() if answer.diagnostic_message)
            break
        current_speed = current_speed + 0.1
        pull_speeds_kph = [current_speed] * len(riders)
        rider_answer_items = populate_rider_answers(riders, pull_durations, pull_speeds_kph)
        i += 1
    return i-1, rider_answer_items, halting_rider



import itertools
import numpy as np
from collections import defaultdict
from typing import List, Tuple

def make_inventory_of_all_combinations_of_pull_durations(
    riders: List[ZsunRiderItem],
    permitted_durations: List[float],
    lower_bound_speed: float
) -> List[Tuple[int, defaultdict[ZsunRiderItem, RiderAnswerItem], ZsunRiderItem]]:
    # Generate all combinations of pull durations
    all_combinations = list(itertools.product(permitted_durations, repeat=len(riders)))
    seed_speed_array = [lower_bound_speed] * len(riders)

    fastest_tuple = None
    fastest_speed = -float('inf')

    lowest_dispersion_tuple = None
    lowest_dispersion = float('inf')

    for pull_durations in all_combinations:
        iterations, rider_answer_items, halted_rider = iterate_until_halted(
            riders, list(pull_durations), seed_speed_array
        )
        halted_speed = rider_answer_items[halted_rider].speed_kph

        # Memo for fastest halted speed
        if halted_speed > fastest_speed:
            fastest_speed = halted_speed
            fastest_tuple = (iterations, rider_answer_items, halted_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [answer.np_intensity_factor for answer in rider_answer_items.values()]
        dispersion = np.std(np_intensity_factors)
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_tuple = (iterations, rider_answer_items, halted_rider)

    return [fastest_tuple, lowest_dispersion_tuple]


def main():
    dict_of_zsunrideritems = read_dict_of_zsunriderItems(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    riders : list[ZsunRiderItem] = [
        dict_of_zsunrideritems[tom_bick],
        dict_of_zsunrideritems[davek],
        dict_of_zsunrideritems[husky],
        # dict_of_zsunrideritems[timr],
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

    a,b,c =calculate_lower_bound_pull_speed(riders)
    logger.info(f"Lower bound pull speed: {fmtl(c)} kph for {a.name} at {b} seconds")

    d,e,f = calculate_lower_bound_speed_at_one_hour_watts(riders)
    logger.info(f"Lower bound speed at one hour: {fmtl(f)} kph for {d.name} at {e} seconds")

    seed_speed = round(min(c, f),1) # 1 decimal place

    pull_durations = [30.0] * len(riders) # seed: 30 seconds for everyone to begin with
    seed_speed_array = [seed_speed] * len(riders)

    iterations, rider_answer_items, halted_rider = iterate_until_halted(riders, pull_durations, seed_speed_array)

    log_rider_answer_items(f"{len(riders)} riders in paceline", rider_answer_items, logger)

    halted_speed = rider_answer_items[halted_rider].speed_kph

    logger.info(f"\nHalted after {iterations} iterations. Halted: {fmtl(halted_speed)} kph  Halting rider: {halted_rider.name} Diagnostic: {rider_answer_items[halted_rider].diagnostic_message}")

    # pull_durations[0] = 240 
    # pull_durations[1] = 240 
    # pull_durations[2] = 240 
    # pull_durations[4] = 240 
    # pull_durations[5] = 240 

    # iterations, rider_answer_items, halted_rider = iterate_until_halted(riders, pull_durations, seed_speed_array)

    # log_rider_answer_items(f"{len(riders)} riders in paceline", rider_answer_items, logger)

    # halted_speed = rider_answer_items[halted_rider].speed_kph

    # logger.info(f"\nHalted after {iterations} iterations. Halted: {fmtl(halted_speed)} kph  Halting rider: {halted_rider.name} Diagnostic: {rider_answer_items[halted_rider].diagnostic_message}")

    a, b = make_inventory_of_all_combinations_of_pull_durations(riders, permitted_pull_durations, seed_speed)

    log_rider_answer_items(f"\nFastest solution: Halted after {a[0]} iterations. ", a[1], logger)
    log_rider_answer_items(f"\nMost evenly balanced solution: Halted after {b[0]} iterations. ", b[1], logger)
if __name__ == "__main__":
    main()


