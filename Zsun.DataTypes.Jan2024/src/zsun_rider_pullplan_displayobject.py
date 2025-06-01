from dataclasses import dataclass
from typing import Optional

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
    pretty_pull                            : str   = ""
    p1_ratio_to_1hr_w                      : float = 0
    p1_ratio_to_zwiftracingapp_zpFTP       : float = 0
    p1_w                                   : float = 0
    p2_w                                   : float = 0
    p3_w                                   : float = 0
    p4_w                                   : float = 0
    pretty_p2_3_4_w                        : str   = ""
    zsun_one_hour_watts                    : float = 0
    average_watts                          : float = 0
    average_wkg                            : float = 0
    pretty_average_watts                   : str   = ""
    normalised_power_watts                 : float = 0
    np_intensity_factor                    : float = 0
    diagnostic_message                     : str   = ""

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
        return rider.zwift_cat

    @staticmethod
    def calculate_zwiftracingapp_zpFTP_wkg(rider: ZsunRiderItem)-> float:
        return rider.zwiftracingapp_zpFTP/rider.weight_kg if rider.weight_kg != 0 else 0

        return round(wkg, 2) if rider.weight_kg != 0 else 0

    @staticmethod
    def make_pretty_zwiftracingapp_cat(rider: ZsunRiderItem) -> str:

        return f"{rider.zwiftracingapp_cat_num}-{rider.zwiftracingapp_cat_name}"

    @staticmethod
    def make_pretty_consolidated_racing_cat_descriptor(rider: ZsunRiderItem) -> str:
        answer = f"{rider.zwift_cat} {RiderPullPlanDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        return answer

    @staticmethod
    def make_pretty_pull(rider : ZsunRiderItem, plan: RiderPullPlanItem) -> str:
        if plan.p1_duration >= 100:
            duration_str = f"{str(round(plan.p1_duration))}sec"
        else:
            duration_str = f" {str(round(plan.p1_duration))}sec"

        p1_w = f"{str(round_to_nearest_10(plan.p1_w))}w"

        p1_wkg = f"{round(rider.get_watts_per_kg(plan.p1_w),1)}wkg"

        p1_over_zFtp_ratio = f"{round(100*plan.p1_w/rider.zwiftracingapp_zpFTP)}%"

        return f"{duration_str} {p1_w} {p1_wkg} {p1_over_zFtp_ratio}"


    @staticmethod
    def make_pretty_p2_3_4_w(p2_w: float, p3_w: float, p4_w: float) -> str:
        def pretty(val: float) -> str:
            return "   " if round_to_nearest_10(val) == 0 else str(round_to_nearest_10(val))
        return f"{pretty(p2_w)}w {pretty(p3_w)}w {pretty(p4_w)}w"

    @staticmethod
    def make_pretty_average_watts(rider : ZsunRiderItem, plan: RiderPullPlanItem) -> str:

        av_wkg = rider.get_watts_per_kg(plan.average_watts)

        return f"{round(av_wkg,1)}wkg {round(plan.average_watts)}w"

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
            pretty_pull                            = RiderPullPlanDisplayObject.make_pretty_pull(rider, plan),
            p1_ratio_to_1hr_w                      = plan.p1_w/rider.zsun_one_hour_watts,
            p1_ratio_to_zwiftracingapp_zpFTP       = plan.p1_w/rider.zwiftracingapp_zpFTP,
            p1_w                                   = plan.p1_w,
            p2_w                                   = plan.p2_w,
            p3_w                                   = plan.p3_w,
            p4_w                                   = plan.p4_w,     
            pretty_p2_3_4_w                        = RiderPullPlanDisplayObject.make_pretty_p2_3_4_w(plan.p2_w, plan.p3_w, plan.p4_w),
            zsun_one_hour_watts                    = rider.zsun_one_hour_watts,
            average_watts                          = plan.average_watts,
            average_wkg                            = plan.average_watts/rider.weight_kg if rider.weight_kg != 0 else 0,
            pretty_average_watts                   = RiderPullPlanDisplayObject.make_pretty_average_watts(rider, plan),
            normalised_power_watts                 = plan.normalized_watts,
            np_intensity_factor                    = plan.normalized_watts/rider.get_1_hour_watts(),
            diagnostic_message                     = plan.diagnostic_message
        )
