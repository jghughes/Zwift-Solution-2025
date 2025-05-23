from dataclasses import dataclass
from typing import Optional, Tuple
from jgh_formatting import round_to_nearest_10

from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem

@dataclass
class RiderPullPlanDisplayObject():
    name                                   : str   = ""
    concatenated_racing_cat_descriptor     : str   = ""
    zwift_zrs                              : float = 0
    zwift_zrs_cat                          : str   = ""
    zwiftracingapp_zpFTP_cat               : str   = ""
    zwiftracingapp_pretty_cat_descriptor   : str   = ""
    zwiftracingapp_zpFTP                   : float = 0
    zwiftracingapp_zpFTP_wkg               : float = 0
    speed_kph                              : float = 0
    p1_duration                            : float = 0
    p1_wkg                                 : float = 0
    p1_ratio_to_1hr_w                      : float = 0
    p1_ratio_to_zwiftracingapp_zpFTP       : float = 0
    p1_w                                   : float = 0
    p2_w                                   : float = 0
    p3_w                                   : float = 0
    p4_w                                   : float = 0
    pretty_p2_3_4_w                        : str   = ""
    zsun_one_hour_watts                    : float = 0
    average_watts                          : float = 0
    normalised_power_watts                       : float = 0
    np_intensity_factor                    : float = 0
    diagnostic_message                     : str   = ""

    @staticmethod
    def calculate_wkg(watts: float, weight : float)-> float:
        return watts/weight if weight != 0 else 0

    @staticmethod
    def calculate_zwift_racing_score_cat(rider: ZsunRiderItem) -> str:
        if rider.zwift_zrs < 180:
            return "E"
        elif rider.zwift_zrs < 350:
            return "D"
        elif rider.zwift_zrs < 520:
            return "C"
        elif rider.zwift_zrs < 690:
            return "B"
        else:
            return "A"

    @staticmethod
    def calculate_zwiftracingapp_zpFTP_cat(rider: ZsunRiderItem)-> str:
        wkg = RiderPullPlanDisplayObject.calculate_wkg(rider.zwiftracingapp_zpFTP, rider.weight_kg)

        if wkg < 2.5:
            return "D"
        elif wkg < 3.2:
            return "C"
        elif wkg < 4.0:
            return "B"
        else:
            return "A"

    @staticmethod
    def calculate_zwiftracingapp_zpFTP_wkg(rider: ZsunRiderItem)-> float:
        wkg = RiderPullPlanDisplayObject.calculate_wkg(rider.zwiftracingapp_zpFTP, rider.weight_kg)

        return round(wkg, 2) if rider.weight_kg != 0 else 0

    @staticmethod
    def make_pretty_zwiftracingapp_cat(rider: ZsunRiderItem) -> str:

        def calculate_velo_cat(rider: ZsunRiderItem) -> Tuple[int, str]:
            if rider.gender == "f":
                if rider.zwiftracingapp_score >= 1450:
                    return 1, "Diamond"
                elif rider.zwiftracingapp_score >= 1250:
                    return 2, "Ruby"
                elif rider.zwiftracingapp_score >= 1100:
                    return 3, "Emerald"
                elif rider.zwiftracingapp_score >= 950:
                    return 4, "Sapphire"
                elif rider.zwiftracingapp_score >= 850:
                    return 5, "Amethyst"
                elif rider.zwiftracingapp_score >= 750:
                    return 6, "Platinum"
                elif rider.zwiftracingapp_score >= 650:
                    return 7, "Gold"
                elif rider.zwiftracingapp_score >= 550:
                    return 8, "Silver"
                elif rider.zwiftracingapp_score >= 400:
                    return 9, "Bronze"
                else:
                    return 10, "Copper"
            else:
                if rider.zwiftracingapp_score >= 2200:
                    return 1, "Diamond"
                elif rider.zwiftracingapp_score >= 1900:
                    return 2, "Ruby"
                elif rider.zwiftracingapp_score >= 1650:
                    return 3, "Emerald"
                elif rider.zwiftracingapp_score >= 1450:
                    return 4, "Sapphire"
                elif rider.zwiftracingapp_score >= 1300:
                    return 5, "Amethyst"
                elif rider.zwiftracingapp_score >= 1150:
                    return 6, "Platinum"
                elif rider.zwiftracingapp_score >= 1000:
                    return 7, "Gold"
                elif rider.zwiftracingapp_score >= 850:
                    return 8, "Silver"
                elif rider.zwiftracingapp_score >= 650:
                    return 9, "Bronze"
                else:
                    return 10, "Copper"

        velo_rank, velo_name = calculate_velo_cat(rider)
        return f"{velo_rank}-{velo_name}"

    @staticmethod
    def make_pretty_consolidated_racing_cat_descriptor(rider: ZsunRiderItem) -> str:
        answer = f"{rider.zwift_zrs} {RiderPullPlanDisplayObject.calculate_zwift_racing_score_cat(rider)} {RiderPullPlanDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider)} {RiderPullPlanDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        return answer

    @staticmethod
    @staticmethod
    def make_pretty_p2_3_4_w(p2_w: float, p3_w: float, p4_w: float) -> str:
        def pretty(val: float) -> str:
            return "   " if round_to_nearest_10(val) == 0 else str(round_to_nearest_10(val))
        return f"{pretty(p2_w)} {pretty(p3_w)} {pretty(p4_w)}"

    @staticmethod
    def from_RiderPullPlanItem(rider : ZsunRiderItem, plan: Optional[RiderPullPlanItem]) -> "RiderPullPlanDisplayObject":
        if plan is None:
            return RiderPullPlanDisplayObject()
        return RiderPullPlanDisplayObject(
            name                                   = rider.name,
            concatenated_racing_cat_descriptor     = RiderPullPlanDisplayObject.make_pretty_consolidated_racing_cat_descriptor(rider),
            zwift_zrs                              = rider.zwift_zrs,
            zwift_zrs_cat                          = RiderPullPlanDisplayObject.calculate_zwift_racing_score_cat(rider),
            zwiftracingapp_zpFTP_cat               = RiderPullPlanDisplayObject.calculate_zwiftracingapp_zpFTP_cat(rider),
            zwiftracingapp_pretty_cat_descriptor   = RiderPullPlanDisplayObject.make_pretty_zwiftracingapp_cat(rider),
            zwiftracingapp_zpFTP                   = rider.zwiftracingapp_zpFTP,
            zwiftracingapp_zpFTP_wkg               = RiderPullPlanDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider),
            speed_kph                              = plan.speed_kph,
            p1_duration                            = plan.p1_duration,
            p1_wkg                                 = plan.p1_w/rider.weight_kg,
            p1_ratio_to_1hr_w                      = plan.p1_w/rider.zsun_one_hour_watts,
            p1_ratio_to_zwiftracingapp_zpFTP       = plan.p1_w/rider.zwiftracingapp_zpFTP,
            p1_w                                   = plan.p1_w,
            p2_w                                   = plan.p2_w,
            p3_w                                   = plan.p3_w,
            p4_w                                   = plan.p4_w,     
            pretty_p2_3_4_w                        = RiderPullPlanDisplayObject.make_pretty_p2_3_4_w(plan.p2_w, plan.p3_w, plan.p4_w),
            zsun_one_hour_watts                    = rider.zsun_one_hour_watts,
            average_watts                          = plan.average_watts,
            normalised_power_watts                 = plan.normalized_watts,
            np_intensity_factor                    = plan.normalized_watts/rider.get_1_hour_watts(),
            diagnostic_message                     = plan.diagnostic_message
        )
