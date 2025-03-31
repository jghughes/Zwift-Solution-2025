from typing import  List, Dict, Tuple
from handy_utilities import get_all_zwiftriders
from zwiftrider_related_items import ZwiftRiderItem, RiderExertionItem, RiderAnswerItem
from jgh_formulae05 import calculate_normalized_watts
import logging





def populate_rider_answers(riders: Dict[ZwiftRiderItem, List[RiderExertionItem]]) -> Dict[ZwiftRiderItem, RiderAnswerItem]:


    answer: Dict[ZwiftRiderItem, RiderAnswerItem] = {}


    def calculate_velo_cat(rider: ZwiftRiderItem) -> Tuple[int, str]:
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

    def calculate_zwift_ftp_cat(rider: ZwiftRiderItem)-> str:
        if rider.ftp < 2.5:
            return "D"
        elif rider.ftp < 3.2:
            return "C"
        elif rider.ftp < 4.0:
            return "B"
        else:
            return "A"

    def calculate_zwift_zrs_cat(rider: ZwiftRiderItem) -> str:
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

    def calculate_ftp_wkg(rider: ZwiftRiderItem)-> float:
        return rider.ftp/rider.weight if rider.weight != 0 else 0

    def calculate_ftp_intensity_factor(rider: ZwiftRiderItem, items: List[RiderExertionItem]) -> float:
        if not items:
            return 0
        if rider.ftp == 0:
            return 0
        ftp_intensity_factor = calculate_normalized_watts(items)/rider.ftp if rider.ftp != 0 else 0
        return ftp_intensity_factor

    def extract_p1_to_pn_watts(exertions: List[RiderExertionItem]) -> Tuple[float, float, float, float, float]:
        if not exertions:
            return 0, 0, 0, 0, 0

        dict_wattages = {exertion.position: exertion.wattage for exertion in exertions}

        p1 = dict_wattages.get(0, 0)
        p2 = dict_wattages.get(1, 0)
        p3 = dict_wattages.get(2, 0)
        p4 = dict_wattages.get(3, 0)
        p_ = dict_wattages.get(4, 0)

        return p1, p2, p3, p4, p_

    def extract_pull_metrics(exertions: List[RiderExertionItem]) -> Tuple[float, float, float]:
        if not exertions:
            return 0, 0, 0

        p1_duration : float = 0
        p1_wkg : float = 0
        p1_slash_ftp : float= 0

        dict_positions = {exertion.position: exertion for exertion in exertions}

        pull_exertion = dict_positions.get(0, None)

        if pull_exertion is None:
            return 0, 0, 0

        pull_exertion = dict_positions.get(0, None)

        if pull_exertion is None:
            return 0, 0, 0

        p1_duration = pull_exertion.duration

        p1_wkg = pull_exertion.wattage / rider.weight if rider.weight != 0 else 0

        p1_slash_ftp = pull_exertion.wattage / rider.ftp if rider.ftp != 0 else 0

        return p1_duration, p1_wkg, p1_slash_ftp
       
    for rider, items in riders.items():

        p1w, p2w, p3w, p4w, pnw = extract_p1_to_pn_watts(items)

        p1_duration, p1_wkg, p1_slash_ftp = extract_pull_metrics(items)

        rider_display_object = RiderAnswerItem(
            name = rider.name,
            zrs = rider.zwift_racing_score,
            zwiftftp_cat = calculate_zwift_ftp_cat(rider),
            velo_cat = f"{calculate_velo_cat(rider)[0]} - {calculate_velo_cat(rider)[1]}",
            cp_5_min_wkg = 0,
            cp  = 0,
            ftp = rider.ftp,
            ftp_wkg  = round(calculate_ftp_wkg(rider),1),
            p1_duration = p1_duration,
            p1_wkg = round(p1_wkg, 1),
            p1_slash_ftp = round(p1_slash_ftp, 1),
            p1_w = round(p1w,0),
            p2_w = round(p2w,0),
            p3_w = round(p3w,0),
            p4_w = round(p4w,0),
            pn_w = round(pnw,0),
            ftp_intensity_factor = round(calculate_ftp_intensity_factor(rider, items),2),
            cp_intensity_factor = round(0, 2)
        )

        answer[rider] = rider_display_object

    return answer


def log_results(test_description: str, result: Dict[ZwiftRiderItem, RiderAnswerItem], logger: logging.Logger) -> None:
    
    from tabulate import tabulate
   
    logger.info(test_description)

    table = []
    for rider, z in result.items():
        table.append([z.name, z.zrs,z.zwiftftp_cat, z.velo_cat, z.cp_5_min_wkg, z.cp, z.ftp, z.ftp_wkg, z.p1_duration, z.p1_wkg, z.p1_slash_ftp, z.p1_w, z.p2_w, z.p3_w, z.p4_w, z.pn_w, z.ftp_intensity_factor, z.cp_intensity_factor])

        headers = ["Rider", "ZRS", "Zwift Cat", "Velo Cat", "CP 5 min w/kg", "CP", "FTP", "FTP w/kg", "P1 duration", "P1 w/kg", "P1/FTP", "P1 w", "P2 w", "P3 w", "P4 w", "Pn w", "FTP IF", "CP IF"]

    logger.info("\n" + tabulate(table, headers=headers, tablefmt="plain"))


def main() -> None:
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from zwiftrider_related_items import ZwiftRiderItem
    from jgh_formulae04 import populate_rider_work_assignments
    from jgh_formulae05 import populate_rider_exertions

    dict_of_zwiftrideritem = get_all_zwiftriders()

    barryb : ZwiftRiderItem = dict_of_zwiftrideritem['barryb']
    johnh : ZwiftRiderItem = dict_of_zwiftrideritem['johnh']
    lynseys : ZwiftRiderItem = dict_of_zwiftrideritem['lynseys']

    pull_speeds_kph = [42.0, 42.0, 42.0]
    pull_durations_sec = [30.0, 30.0, 30.0]
    riders : list[ZwiftRiderItem] = [barryb, johnh, lynseys]

    work_assignments = populate_rider_work_assignments(riders, pull_durations_sec, pull_speeds_kph)

    rider_exertions = populate_rider_exertions(work_assignments)

    rider_answers = populate_rider_answers(rider_exertions)

    log_results("Comparative rider wattage metrics based on single loop of the paceline (this is as far as the TTT Calculator goes I suspect):", rider_answers, logger)


if __name__ == "__main__":
    main()
