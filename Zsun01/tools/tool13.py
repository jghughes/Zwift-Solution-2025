from random import seed
from attr import s
from zsun_rider_item import ZsunRiderItem
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_units_ticks,set_y_axis_units_ticks
from jgh_read_write import write_pandas_dataframe_as_xlsx
from handy_utilities import *
from computation_classes import RiderWorkAssignmentItem, RiderExertionItem, RiderAnswerItem

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


def fmt(x : Union[int, float]):
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
            fmt(rider.calculate_speed_at_one_hour_watts()),
            fmt(rider.zsun_one_hour_watts)
        ])

    headers = [
        "Rider",
        "Strength (w/kg)",
        "zFTP (w/kg)",
        "1hr (w/kg)",
        "1hr (kph)",
        "1hr (W)"
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))

def populate_rider_answers(riders: List[ZsunRiderItem], pull_durations: List[float], pull_speeds_kph: List[float])-> defaultdict[ZsunRiderItem, RiderAnswerItem]:
    
    work_assignments = populate_rider_work_assignments(riders, pull_durations, pull_speeds_kph)

    # log_rider_work_assignments("Example riders",work_assignments, logger)

    rider_exertions = populate_rider_exertions(work_assignments)

    # log_rider_exertions("Calculated rider exertion during paceline rotation [RiderExertionItem]:", rider_exertions, logger)

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    rider_answer_items = do_diagnostic(rider_answer_items)

    log_rider_answer_items(f"{len(riders)} riders in paceline", rider_answer_items, logger)


    return rider_answer_items

def do_diagnostic(rider_answers: defaultdict[ZsunRiderItem, RiderAnswerItem]) -> defaultdict[ZsunRiderItem, RiderAnswerItem]:
    for rider, answer in rider_answers.items():
        msg = ""
        # Step 1: Intensity factor checks
        if answer.np_intensity_factor >= 1.0:
            msg += "halt. intensity factor > 1.0. "
        elif answer.np_intensity_factor >= 0.95:
            msg += "warning. intensity factor >= 0.95. "

        # Step 2: Pull watt limit checks
        pull_limit = rider.lookup_permissable_pull_watts(answer.p1_duration)
        if answer.p1_w >= pull_limit:
            msg += "halt. pull watts exceed limit."
        elif answer.p1_w >= 0.95 * pull_limit:
            msg += "warning. pull watts >= .95 of limit."

        answer.diagnostic_message = msg
    return rider_answers

def handle_diagnostic(rider_answer_items: defaultdict[ZsunRiderItem, RiderAnswerItem],
    riders: list[ZsunRiderItem],
    pull_durations: list[float]
) -> list[float]:
    # Define the allowed pull duration steps (in seconds), descending order
    duration_steps = [240.0, 120.0, 60.0, 30.0]
    # Build a mapping from rider to their index in the list
    rider_to_index = {r: i for i, r in enumerate(riders)}
    # Copy the durations so we can modify them
    new_durations = pull_durations[:]
    for rider, answer in rider_answer_items.items():
        if answer.diagnostic_message:
            idx = rider_to_index[rider]
            current = new_durations[idx]
            answer.diagnostic_message = ""
            # Find the next lower step, if possible
            for i, step in enumerate(duration_steps):
                if current == step and i + 1 < len(duration_steps):
                    new_durations[idx] = duration_steps[i + 1]
                    break
            # If no change, leave the message as is


    return new_durations









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
    seed_speed = seed_speed * 0.9 # 90% of the slowest rider's speed
    current_speed = seed_speed

    pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone
    pull_speeds_kph = [seed_speed] * len(riders)

    last_known_good_answer : defaultdict[ZsunRiderItem, RiderAnswerItem]

    rider_answer_items : defaultdict[ZsunRiderItem, RiderAnswerItem] = populate_rider_answers(riders, pull_durations, pull_speeds_kph)

    # increase seed_speed in increments of 1 kph up to seed + 10
    for i in range(1, 10):
        #break if any rider has a diagnostic message
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            break
        else:
            # make a deep copy of rider_answer_items and assign to last_known_good_answer
            last_known_good_answer = rider_answer_items.copy()
        current_speed = seed_speed + i
        pull_speeds_kph = [current_speed] * len(riders)
        rider_answer_items = populate_rider_answers(riders, pull_durations, pull_speeds_kph)

    # continue where we left off with the new pull durations
    new_pull_duration = handle_diagnostic(rider_answer_items, riders, pull_durations)

    rider_answer_items : defaultdict[ZsunRiderItem, RiderAnswerItem] = populate_rider_answers(riders, new_pull_duration, pull_speeds_kph)

    seed_speed = current_speed - 2 # 1 kph less than the last speed
    # increase seed_speed in increments of 0.1 kph up to seed + 5kph (arbitrary)
    for i in range(1, 50):
        #break if any rider has a diagnostic message
        if any(answer.diagnostic_message for answer in rider_answer_items.values()):
            break
        else:
            # make a deep copy of rider_answer_items and assign to last_known_good_answer
            last_known_good_answer = rider_answer_items.copy()
        pull_speeds_kph = [seed_speed + i*0.1] * len(riders)
        rider_answer_items = populate_rider_answers(riders, pull_durations, pull_speeds_kph)


if __name__ == "__main__":
    main()


