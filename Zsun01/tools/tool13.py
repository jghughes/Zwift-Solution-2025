import time
from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunriderItems
from jgh_formulae03 import arrange_riders_in_optimal_order
from jgh_formulae06 import log_pull_plan
from jgh_formulae08 import fmtc, format_hms, permitted_pull_durations, calculate_lower_bound_pull_speed, calculate_lower_bound_speed_at_one_hour_watts, make_a_pull_plan_with_a_sensible_top_speed, search_for_optimal_pull_plans

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
lynsey_segal = '383480' #ftp 201
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
    cory_cook,
    # dave_konicek,
    # david_evanetich,
    # giao_nguyen,
    # husky_crone,
    john_hughes,
    # josh_neil,
    # lynsey_segal,
    # mark_brzezinski,
    # matt_steeve,
    melissa_warwick,
    # meridith_leubner,
    # richard_mann,
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


def main():
    dict_of_zsunrideritems = read_dict_of_zsunriderItems(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)


    riders : list[ZsunRiderItem] = []
    for riderID in riderIDS:
        riders.append(dict_of_zsunrideritems[riderID])

    riders = arrange_riders_in_optimal_order(riders)

    r01,r01_duration,r01_speed =calculate_lower_bound_pull_speed(riders)
    r02,r02_duration,r02_speed = calculate_lower_bound_speed_at_one_hour_watts(riders)

    logger.info(f"\nPaceline speed constraints:-")
    logger.info(f"Slowest conceivable pull      :  {round(r01_speed,1)} kph @ {round(r01.get_permitted_4_minute_pull_watts())} Watts ({round(r01.get_permitted_4_minute_pull_watts()/r01.weight_kg, 1)} W/kg) by {r01.name} for a pull of {round(r01_duration)} seconds.")
    logger.info(f"Slowest conceivable one hour  :  {round(r02_speed, 1)} kph @ {round(r02.get_1_hour_watts())} Watts ({round(r02.get_1_hour_watts()/r02.weight_kg, 1)} W/kg) by {r02.name}.")

    seed_speed = round(min(r01_speed, r02_speed),1) # 1 decimal place i.e. a float not an int
    plain_vanilla_pull_durations = [60.0] * len(riders) # seed: 60 seconds for everyone for Simplest case execute as a team
    seed_speed_array = [seed_speed] * len(riders)

    iterations, rider_answer_items, halted_rider = make_a_pull_plan_with_a_sensible_top_speed(riders, plain_vanilla_pull_durations, seed_speed_array)
    log_pull_plan(f"\n\nSIMPLEST PLAN: {round(rider_answer_items[halted_rider].speed_kph)} kph", rider_answer_items, logger)

    start_time = time.time()
    (solutions, total_alternatives, total_iterations) = search_for_optimal_pull_plans(riders, permitted_pull_durations, seed_speed)
    elapsed_time = time.time() - start_time

    solution01, solution02 = solutions
    iterations, rider_answer_items, halted_rider = solution02
    log_pull_plan(f"\n\nFAIREST PLAN: {round(rider_answer_items[halted_rider].speed_kph)} kph", rider_answer_items, logger)
    iterations, rider_answer_items, halted_rider = solution01
    log_pull_plan(f"\n\nFASTEST PLAN: {round(rider_answer_items[halted_rider].speed_kph)} kph", rider_answer_items, logger)
    
    logger.info(f"\n\n\nReport: did {fmtc(total_iterations)} iterations to evaluate {fmtc(total_alternatives)} alternatives in {format_hms(elapsed_time)} \n\n")

if __name__ == "__main__":
    main()


