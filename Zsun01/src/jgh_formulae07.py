from typing import  Dict, Tuple
from zsun_rider_item import ZsunRiderItem, RiderAnswerItem, RiderAnswerDisplayObject
from jgh_formulae06 import add_zwift_cp_and_w_prime_to_rider_answer_items, add_zwift_cp_and_w_prime_to_rider_criticalpower_items
import logging


def populate_rider_answer_displayobjects(riders: Dict[ZsunRiderItem, RiderAnswerItem]) -> Dict[ZsunRiderItem, RiderAnswerDisplayObject]:

    answer: Dict[ZsunRiderItem, RiderAnswerDisplayObject] = {}

    def calculate_zwift_zrs_cat(rider: ZsunRiderItem) -> str:
        if rider.zwift_racing_score < 180:
            return "E"
        elif rider.zwift_racing_score < 350:
            return "D"
        elif rider.zwift_racing_score < 520:
            return "C"
        elif rider.zwift_racing_score < 690:
            return "B"
        else:
            return "A"

    def calculate_zwift_ftp_cat(rider: ZsunRiderItem)-> str:

        wkg = rider.ftp/rider.weight if rider.weight != 0 else 0

        if wkg < 2.5:
            return "D"
        elif wkg < 3.2:
            return "C"
        elif wkg < 4.0:
            return "B"
        else:
            return "A"

    def calculate_wkg(watts: float, weight : float)-> float:
        return rider.ftp/rider.weight if rider.weight != 0 else 0

    def make_pretty_velo_cat(rider: ZsunRiderItem) -> str:

        def calculate_velo_cat(rider: ZsunRiderItem) -> Tuple[int, str]:
            if rider.gender == "f":
                if rider.velo_rating >= 1450:
                    return 1, "Diamond"
                elif rider.velo_rating >= 1250:
                    return 2, "Ruby"
                elif rider.velo_rating >= 1100:
                    return 3, "Emerald"
                elif rider.velo_rating >= 950:
                    return 4, "Sapphire"
                elif rider.velo_rating >= 850:
                    return 5, "Amethyst"
                elif rider.velo_rating >= 750:
                    return 6, "Platinum"
                elif rider.velo_rating >= 650:
                    return 7, "Gold"
                elif rider.velo_rating >= 550:
                    return 8, "Silver"
                elif rider.velo_rating >= 400:
                    return 9, "Bronze"
                else:
                    return 10, "Copper"
            else:
                if rider.velo_rating >= 2200:
                    return 1, "Diamond"
                elif rider.velo_rating >= 1900:
                    return 2, "Ruby"
                elif rider.velo_rating >= 1650:
                    return 3, "Emerald"
                elif rider.velo_rating >= 1450:
                    return 4, "Sapphire"
                elif rider.velo_rating >= 1300:
                    return 5, "Amethyst"
                elif rider.velo_rating >= 1150:
                    return 6, "Platinum"
                elif rider.velo_rating >= 1000:
                    return 7, "Gold"
                elif rider.velo_rating >= 850:
                    return 8, "Silver"
                elif rider.velo_rating >= 650:
                    return 9, "Bronze"
                else:
                    return 10, "Copper"

        velo_rank, velo_name = calculate_velo_cat(rider)
        return f"{velo_rank}-{velo_name}"

    def make_pretty_cat_descriptor(rider: ZsunRiderItem) -> str:
        answer = f"{rider.zwift_racing_score} {round(calculate_wkg(rider.ftp, rider.weight), 2)} {calculate_zwift_ftp_cat(rider)} {make_pretty_velo_cat(rider)}"
        # answer = f"zrs={rider.zwift_racing_score} ftp={round(calculate_wkg(rider.ftp, rider.weight), 2)} cat={calculate_zwift_ftp_cat(rider)} cat={make_pretty_velo_cat(rider)}"
        # answer = f"{rider.zwift_racing_score}({calculate_zwift_zrs_cat(rider)}) {round(calculate_wkg(rider.ftp, rider.weight), 1)}({calculate_zwift_ftp_cat(rider)}) {make_pretty_velo_cat(rider)}"
        return answer

    def make_pretty_p1_p4(answer: RiderAnswerItem) -> str:
        return f"{round(answer.p1_w)} {round(answer.p2_w)} {round(answer.p3_w)} {round(answer.p4_w)}"

    for rider, item in riders.items():
        rider_display_object = RiderAnswerDisplayObject(
            name                  = rider.name,
            pretty_cat_descriptor = make_pretty_cat_descriptor(rider),
            zrs_score             = rider.zwift_racing_score,
            zrs_cat               = calculate_zwift_zrs_cat(rider),
            zwiftftp_cat          = calculate_zwift_ftp_cat(rider),
            velo_cat              = make_pretty_velo_cat(rider),
            zwift_cp              = round(item.cp_watts),
            zwift_w_prime         = round(item.anaerobic_work_capacity),
            ftp                   = round(rider.ftp),
            ftp_wkg               = round(calculate_wkg(rider.ftp, rider.weight),1),
            speed_kph             = round(item.speed_kph, 1),
            pull_duration         = item.pull_duration,
            pull_wkg              = round(calculate_wkg(item.p1_w, rider.weight), 1),
            pull_w_over_ftp       = f"{round(item.p1_w / rider.ftp*100 if rider.ftp != 0 else 0)}%",
            p1_4                  = make_pretty_p1_p4(item),
            ftp_intensity_factor  = round(item.ftp_intensity_factor, 2),
            cp_intensity_factor   = round(0, 2)
        )
        answer[rider] = rider_display_object

    return answer

def log_results_answer_displayobjects(test_description: str, result: Dict[ZsunRiderItem, RiderAnswerDisplayObject], logger: logging.Logger) -> None:
    
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, z in result.items():
        table.append([
            z.name,
            z.pretty_cat_descriptor,
            # z.zrs_score, 
            # z.zrs_cat, 
            # z.zwiftftp_cat, 
            # z.velo_cat, 
            # z.ftp, 
            # z.ftp_wkg, 
            z.speed_kph,
            z.pull_duration, 
            z.pull_wkg, 
            z.p1_4, 
            z.pull_w_over_ftp, 
            z.ftp_intensity_factor, 
            z.cp_intensity_factor,
            z.zwift_cp, 
            z.zwift_w_prime 

        ])

    headers = ["Rider",
        "Categories",
        # "ZRS", 
        # "ZRS Cat", 
        # "FTP Cat", 
        # "Velo Cat", 
        # "FTP", 
        # "FTP w/kg",
        "kph", 
        "pull(s)", 
        "w/kg", 
        "P1-4", 
        "ftp(%)", 
        "IF(ftp)", 
        "IF(cp_watts)",
        "CP", 
        "W'" 
    ]
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from zsun_rider_item import ZsunRiderItem
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions
    from jgh_formulae06 import populate_rider_answeritems

    from handy_utilities import read_dict_of_zwiftriders, read_dict_of_cpdata

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zwiftriders(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    CPDATA_FILE_NAME = "betel_cp_data.json"

    zwiftriders_zwift_cp_data = read_dict_of_cpdata(CPDATA_FILE_NAME,ZSUN01_PROJECT_DATA_DIRPATH)

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

    rider_answer_items = populate_rider_answeritems(rider_exertions)

    zwiftrider_cp_items = add_zwift_cp_and_w_prime_to_rider_criticalpower_items(zwiftriders_zwift_cp_data)

    rider_answer_items_with_cp_and_w_prime = add_zwift_cp_and_w_prime_to_rider_answer_items(rider_answer_items, zwiftrider_cp_items)

    rider_displayobjects = populate_rider_answer_displayobjects(rider_answer_items_with_cp_and_w_prime)

    log_results_answer_displayobjects("Comparative rider metrics [RiderAnswerItem]:", rider_displayobjects, logger)


if __name__ == "__main__":
    main()
