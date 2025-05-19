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

ZSUN01_BETEL_PROFILES_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

# ZSUNBetelguese
barry_beck = '5490373' #ftp 273
brandi_steeve = "991817" #ftp 196
bryan_bumpas = "9011" #ftp 214
cory_cook = "5569057"
dave_konicek = "3147366" #ftp 276 critical_power 278
david_evanetich = '4945836'
giao_nguyen = "183277" #ftp 189
husky_crone = "5134" #ftp 268
john_hughes = '1884456' #ftp 240 zmap 292
josh_neil = '2508033' #ftp 260
lynseys_segal = '383480' #ftp 201
mark_brzezinski = '5530045' #ftp 280
matt_steeve = "1024413"
melissa_warwick = "1657744" #ftp 213
meridith_leubner = "1707548" #ftp 220
richard_mann = '1193' # ftp 200
scott_mcveigh = "11526" #ftp 247
selena_shaikh = "2682791" #ftp 214
steve_seiler = "6142432" #ftp 270
tim_reid = "5421258" #ftp 380
tom_bick = "11741" #ftp 303 critical_power 298

betelguese = [
    # barry_beck,
    # brandi_steeve,
    # bryan_bumpas,
    # cory_cook,
    # dave_konicek,
    david_evanetich,
    giao_nguyen,
    # husky_crone,
    # john_hughes,
    josh_neil,
    # lynseys_segal,
    # mark_brzezinski,
    # matt_steeve,
    # melissa_warwick,
    # meridith_leubner,
    richard_mann,
    # scott_mcveigh,
    # selena_shaikh,
    # steve_seiler,
    # tim_reid,
    # tom_bick,
]
# ZSUNGiants
ceri_pritchard = "4204538"
colin_humphrey = "407780"
dave_konicek = "3147366" #ftp 276 critical_power 278
ed_bentley = "2449352"
eltjo_biemold = "106298"
ivan_parks = "2847282"
john_glass = "172221"
roy_roesthuis = "197937"
steve_james = "1662067"
giants = [
    ceri_pritchard,
    colin_humphrey,
    # dave_konicek,
    # ed_bentley,
    # eltjo_biemold,
    # ivan_parks,
    john_glass,
    roy_roesthuis,
    steve_james,
]

#ZSUNderFire
dave_konicek = "3147366"
gertjan_buisman = "1408923"
harrison_clark = "4348809"
james_veitch = "5959864"
rick_porteous = "2873877"
sjors_van_liempt = "2705238"
tom_bick = "11741"
xander_crawshaw = "2419188"
zsunderfire = [
    dave_konicek,
    gertjan_buisman,
    # harrison_clark,
    james_veitch,
    rick_porteous,
    sjors_van_liempt,
    tom_bick,
    # xander_crawshaw,
]

riderIDS = betelguese

permitted_pull_durations = [30.0, 60.0, 120.0, 180.0, 240.0] # in seconds

def fmt(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 2 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.2e+03' or '12'.
    """
    return f"{x:.2g}"

def fmtl(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 4 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.234e+03' or '1234'.
    """
    return f"{x:.4g}"

def fmtc(x: Union[int, float]) -> str:
    """
    Format a number with thousands separators and up to 2 decimal places.
    For floats, trailing zeros and decimal points are removed if unnecessary.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1,234' or '1,234.56'.
    """
    if isinstance(x, int):
        return f"{x:,}"
    elif isinstance(x, float):
        return f"{x:,.2f}".rstrip('0').rstrip('.') if '.' in f"{x:,.2f}" else f"{x:,.2f}"
    else:
        return str(x)

def format_hms(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    # Format seconds with one leading zero if < 10, else no leading zero
    sec_str = f"{secs:03.1f}" if secs < 10 else f"{secs:0.1f}"
    if hours >= 1:
        return f"{int(hours)} hours {int(minutes):02} minutes {sec_str} seconds"
    elif minutes >= 1:
        return f"{int(minutes):02} minutes {sec_str} seconds"
    else:
        return f"{sec_str} seconds"

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
        if answer.np_intensity_factor >= 0.95:
            msg += " NP/1hr>0.95"

        # Step 2: Pull watt limit checks
        pull_limit = rider.lookup_permissable_pull_watts(answer.p1_duration)
        if answer.p1_w >= pull_limit:
            msg += " pull-watts>limit"

        answer.diagnostic_message = msg
    return rider_answers

# def iterate_until_halted (riders: list[ZsunRiderItem], pull_durations: list[float], pull_speeds_kph: list[float]) -> tuple[int, defaultdict[ZsunRiderItem, RiderAnswerItem], ZsunRiderItem]:

#     rider_answer_items : defaultdict[ZsunRiderItem, RiderAnswerItem] = populate_rider_answers(riders, pull_durations, pull_speeds_kph)

#     # iterate until a rider has a diagnostic message
#     i = 1
#     current_speed = round(pull_speeds_kph[0], 1)

#     while True:
#         # break if any rider has a diagnostic message
#         if any(answer.diagnostic_message for answer in rider_answer_items.values()):
#             halting_rider = next(rider for rider, answer in rider_answer_items.items() if answer.diagnostic_message)
#             break
#         current_speed = current_speed + 0.1
#         pull_speeds_kph = [current_speed] * len(riders)
#         rider_answer_items = populate_rider_answers(riders, pull_durations, pull_speeds_kph)
#         i += 1
#     return i-1, rider_answer_items, halting_rider

def iterate_until_halted(
    riders: list[ZsunRiderItem],
    pull_durations: list[float],
    pull_speeds_kph: list[float],
    precision: float = 0.1,
    max_iter: int = 20
) -> tuple[int, defaultdict[ZsunRiderItem, RiderAnswerItem], ZsunRiderItem]:
    """
    Uses binary search to find the maximum speed before a diagnostic message appears.
    Returns (iterations, rider_answer_items, halting_rider).
    """
    # Initial lower and upper bounds
    lower = pull_speeds_kph[0]
    upper = lower

    # Find an upper bound where a diagnostic message appears
    for _ in range(10):
        test_speeds = [upper] * len(riders)
        rider_answer_items = populate_rider_answers(riders, pull_durations, test_speeds)
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            break
        upper += 5.0  # Increase by a reasonable chunk
    else:
        # If we never find an upper bound, just return the last result
        return 1, rider_answer_items, None

    iterations = 0
    halting_rider = None
    last_valid_items = None

    while (upper - lower) > precision and iterations < max_iter:
        mid = (lower + upper) / 2
        test_speeds = [mid] * len(riders)
        rider_answer_items = populate_rider_answers(riders, pull_durations, test_speeds)
        iterations += 1
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            upper = mid
            halting_rider = next(rider for rider, answer in rider_answer_items.items() if answer.diagnostic_message)
        else:
            lower = mid
            last_valid_items = rider_answer_items


    # Use the halting (upper) speed after binary search
    final_speeds = [upper] * len(riders)
    rider_answer_items = populate_rider_answers(riders, pull_durations, final_speeds)
    if any(answer.diagnostic_message for answer in rider_answer_items.values()):
        halting_rider = next(rider for rider, answer in rider_answer_items.items() if answer.diagnostic_message)
    else:
        halting_rider = None

    return iterations, rider_answer_items, halting_rider

import itertools
import numpy as np
from collections import defaultdict
from typing import List, Tuple

import concurrent.futures
import itertools
import numpy as np
from collections import defaultdict
from typing import List, Tuple

def evaluate_combination(args):
    # Unpack arguments
    riders, pull_durations, seed_speed_array = args
    # Call the simulation for this combination
    return iterate_until_halted(riders, list(pull_durations), seed_speed_array)

def find_optimal_solutions(
        riders: List[ZsunRiderItem],
        permitted_durations: List[float],
        lower_bound_speed: float
) -> Tuple[
        List[Tuple[int, defaultdict[ZsunRiderItem, RiderAnswerItem], ZsunRiderItem]],
        int,  # total_alternatives
        int   # total_iterations
]:
    all_combinations = list(itertools.product(permitted_durations, repeat=len(riders)))
    seed_speed_array = [lower_bound_speed] * len(riders)
    total_alternatives = len(all_combinations)
    total_iterations = 0

    # Prepare arguments for each process
    args_list = [(riders, pull_durations, seed_speed_array) for pull_durations in all_combinations]

    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(evaluate_combination, args_list):
            results.append(result)

    fastest_tuple = None
    fastest_speed = -float('inf')
    lowest_dispersion_tuple = None
    lowest_dispersion = float('inf')

    for iterations, rider_answer_items, halted_rider in results:
        total_iterations += iterations
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

    return ([fastest_tuple, lowest_dispersion_tuple], total_alternatives, total_iterations)

import time

def main():
    dict_of_zsunrideritems = read_dict_of_zsunriderItems(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)


    riders : list[ZsunRiderItem] = []
    for riderID in riderIDS:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    a,b,c =calculate_lower_bound_pull_speed(riders)
    d,e,f = calculate_lower_bound_speed_at_one_hour_watts(riders)

    logger.info(f"\nPaceline constraints:-")
    logger.info(f"p1 constraint (slowest p1)    :  {fmtl(c)}kph by {a.name} for a pull of {b}sec.")
    logger.info(f"1hr constraint (slowest 1hr)  :  {fmtl(f)}kph by {d.name} for a pull of {e}sec.")

    seed_speed = round(min(c, f),1) # 1 decimal place
    plain_vanilla_pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone for Simplest case execute as a team
    seed_speed_array = [seed_speed] * len(riders)

    iterations, rider_answer_items, halted_rider = iterate_until_halted(riders, plain_vanilla_pull_durations, seed_speed_array)
    log_rider_answer_items(f"\n\nSIMPLEST PLAN:", rider_answer_items, logger)

    start_time = time.time()
    (results, total_alternatives, total_iterations) = find_optimal_solutions(riders, permitted_pull_durations, seed_speed)
    elapsed_time = time.time() - start_time

    a,b, = results
    log_rider_answer_items(f"\n\nFASTEST PLAN:", a[1], logger)
    log_rider_answer_items(f"\n\nFAIREST PLAN:", b[1], logger)
    logger.info(f"\n\n\nReport: did {fmtc(total_iterations)} iterations to evaluate {fmtc(total_alternatives)} alternatives in {format_hms(elapsed_time)} \n\n")

if __name__ == "__main__":
    main()


