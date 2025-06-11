from dataclasses import dataclass
from typing import Optional, List
from dataclasses import dataclass, field
from typing import DefaultDict, Optional
from collections import defaultdict
from jgh_formatting import round_to_nearest_10
from zsun_rider_item import ZsunRiderItem

@dataclass
class CurveFittingResult:
    zwift_id                     : str   = ""    # Zwift ID of the rider
    one_hour_curve_coefficient   : float = 0.0   # Coefficient for FTP modeling
    one_hour_curve_exponent      : float = 0.0   # Exponent for FTP modeling
    one_hour_curve_r_squared     : float = 0.0   # R-squared value for FTP curve fitting
    TTT_pull_curve_coefficient   : float = 0.0   # Coefficient for pull modeling
    TTT_pull_curve_exponent      : float = 0.0   # Exponent for pull modeling
    TTT_pull_curve_r_squared     : float = 0.0   # R-squared value for pull curve fitting
    CP                           : float = 0.0   # Critical power in watts
    AWC                          : float = 0.0   # Anaerobic work capacity in kilojoules
    when_curves_fitted           : str   = ""    # Timestamp indicating when the models were fitted


@dataclass(frozen=True, eq=True) 
class RiderWorkAssignmentItem:
    position    : int = 1
    duration    : float = 0.0 
    speed       : float = 0.0 


@dataclass(frozen=True, eq=True) 
class RiderExertionItem:
    current_location_in_paceline : int = 0
    speed_kph                    : float = 0.0 
    duration                     : float = 0.0 
    wattage                      : float = 0.0 
    kilojoules                   : float = 0.0   


@dataclass
class RiderContributionItem():
    speed_kph             : float = 0.0 
    p1_duration           : float = 0.0 
    p1_w                  : float = 0.0 
    p2_w                  : float = 0.0 
    p3_w                  : float = 0.0 
    p4_w                  : float = 0.0 
    p5_w                  : float = 0.0 
    p6_w                  : float = 0.0 
    p7_w                  : float = 0.0 
    p8_w                  : float = 0.0 
    average_watts         : float = 0.0 
    normalized_watts      : float = 0.0 
    invalidation_reason   : str = ""


@dataclass
class RiderContributionDisplayObject():
    name                                   : str   = ""
    concatenated_racing_cat_descriptor     : str   = ""
    zwift_zrs                              : float = 0.0 
    zwift_zrs_cat                          : str   = ""
    zwiftracingapp_zpFTP_cat               : str   = ""
    zwiftracingapp_pretty_cat_descriptor   : str   = ""
    zwiftracingapp_zpFTP                   : float = 0.0 
    zwiftracingapp_zpFTP_wkg               : float = 0.0 
    speed_kph                              : float = 0.0 
    p1_duration                            : float = 0.0 
    p1_wkg                                 : float = 0.0 
    pretty_pull                            : str   = ""
    p1_ratio_to_1hr_w                      : float = 0.0 
    p1_ratio_to_zwiftracingapp_zpFTP       : float = 0.0 
    p1_w                                   : float = 0.0 
    p2_w                                   : float = 0.0 
    p3_w                                   : float = 0.0 
    p4_w                                   : float = 0.0 
    pretty_p2_3_4_w                        : str   = ""
    zsun_one_hour_watts                    : float = 0.0 
    average_watts                          : float = 0.0 
    average_wkg                            : float = 0.0 
    pretty_average_watts                   : str   = ""
    normalised_power_watts                 : float = 0.0 
    intensity_factor                       : float = 0.0 
    invalidation_reason                     : str   = ""

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
        answer = f"{rider.zwift_cat} {RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        return answer

    @staticmethod
    def make_pretty_pull(rider : ZsunRiderItem, plan: RiderContributionItem) -> str:

        duration_str = f"{int(round(plan.p1_duration)):3d}sec"
        # if plan.p1_duration >= 100:
        #     duration_str = f"{str(round(plan.p1_duration))}sec"
        # else:
        #     duration_str = f"\u00A0{str(round(plan.p1_duration))}sec"  # Non-breaking space that tabulate will respect


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
    def make_pretty_average_watts(rider : ZsunRiderItem, contribution: RiderContributionItem) -> str:

        av_wkg = rider.get_watts_per_kg(contribution.average_watts)

        return f"{round(av_wkg,1)}wkg {round(contribution.average_watts)}w"

    @staticmethod
    def from_RiderContributionItem(rider : ZsunRiderItem, contribution: Optional[RiderContributionItem]) -> "RiderContributionDisplayObject":
        if contribution is None:
            return RiderContributionDisplayObject()
        return RiderContributionDisplayObject(
            name                                   = rider.name,
            concatenated_racing_cat_descriptor     = RiderContributionDisplayObject.make_pretty_consolidated_racing_cat_descriptor(rider),
            zwift_zrs                              = rider.zwift_zrs,
            zwift_zrs_cat                          = RiderContributionDisplayObject.calculate_zwift_racing_score_cat(rider),
            zwiftracingapp_zpFTP_cat               = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_cat(rider),
            zwiftracingapp_pretty_cat_descriptor   = RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider),
            zwiftracingapp_zpFTP                   = rider.zwiftracingapp_zpFTP,
            zwiftracingapp_zpFTP_wkg               = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider),
            speed_kph                              = contribution.speed_kph,
            p1_duration                            = contribution.p1_duration,
            p1_wkg                                 = contribution.p1_w/rider.weight_kg,
            pretty_pull                            = RiderContributionDisplayObject.make_pretty_pull(rider, contribution),
            p1_ratio_to_1hr_w                      = contribution.p1_w/rider.zsun_one_hour_watts,
            p1_ratio_to_zwiftracingapp_zpFTP       = contribution.p1_w/rider.zwiftracingapp_zpFTP,
            p1_w                                   = contribution.p1_w,
            p2_w                                   = contribution.p2_w,
            p3_w                                   = contribution.p3_w,
            p4_w                                   = contribution.p4_w,     
            pretty_p2_3_4_w                        = RiderContributionDisplayObject.make_pretty_p2_3_4_w(contribution.p2_w, contribution.p3_w, contribution.p4_w),
            zsun_one_hour_watts                    = rider.zsun_one_hour_watts,
            average_watts                          = contribution.average_watts,
            average_wkg                            = contribution.average_watts/rider.weight_kg if rider.weight_kg != 0 else 0,
            pretty_average_watts                   = RiderContributionDisplayObject.make_pretty_average_watts(rider, contribution),
            normalised_power_watts                 = contribution.normalized_watts,
            intensity_factor                    = contribution.normalized_watts/rider.get_one_hour_watts(),
            invalidation_reason                     = contribution.invalidation_reason
        )


@dataclass
class PacelineIngredientsItem:
    riders_list                  : List[ZsunRiderItem] = field(default_factory=list)
    sequence_of_pull_periods_sec : List[float]         = field(default_factory=list)
    pull_speeds_kph              : List[float]         = field(default_factory=list)
    max_exertion_intensity_factor: float               = 0.95


@dataclass
class PacelineComputationReport:
    num_compute_iterations_performed : int  = 0
    rider_contributions              : DefaultDict[ZsunRiderItem, RiderContributionItem] = field(default_factory=lambda: defaultdict(RiderContributionItem))
    rider_that_breeched_contraints   : Optional[ZsunRiderItem]  = None


@dataclass
class PacelineSolutionsComputationReport:
    candidate_rotation_sequences_count          : int   = 0
    total_compute_iterations_performed_count    : int   = 0
    computational_time                          : float = 0.0
    solutions                                   : List[PacelineComputationReport] = field(default_factory=list)



