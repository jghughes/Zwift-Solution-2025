from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

# (No third-party imports)
from jgh_number import safe_divide
from paceline_compute_types import (
    PackageOfPacelineComputationReportItem,
    PacelineComputationReportItem,
    RiderContributionItem,
)
from jgh_enums import PacelinePlanTypeEnum
from jgh_formatting import format_number_2dp, round_to_nearest_10
from jgh_number import safe_divide
from rider_compute_item import RiderComputeItem

# import statements found in __main__ block: None

@dataclass
class RiderContributionDisplayObject():
    index                                  : int   = 0
    name                                   : str   = ""
    pretty_concatenated_racing_cat_descriptor : str   = ""
    zwift_racing_score                     : float = 0.0 
    zwift_zrs_cat                          : str   = ""
    zwiftracingapp_zpFTP_cat               : str   = ""
    zwiftracingapp_pretty_cat_descriptor   : str   = ""
    velo_zpftp_watts                       : float = 0.0 
    zwiftracingapp_zpFTP_wkg               : float = 0.0 
    pretty_zwiftracingapp_zpFTP_wkg        : str   = "" 
    speed_kph                              : float = 0.0 
    p1_duration                            : float = 0.0 
    p1_wkg                                 : float = 0.0 
    pretty_pull                            : str   = ""
    pretty_pull_comparison                 : str   = ""
    p1_ratio_to_1hr_w                      : float = 0.0 
    p1_ratio_to_zwiftracingapp_zpFTP       : float = 0.0 
    p1_w                                   : float = 0.0 
    p2_w                                   : float = 0.0 
    p3_w                                   : float = 0.0 
    p4_w                                   : float = 0.0 
    pretty_p1_2_3_4_w                      : str   = ""
    jgh_60_min_watts                       : float = 0.0 
    average_watts                          : float = 0.0 
    average_wkg                            : float = 0.0 
    pretty_average_watts                   : str   = ""
    normalised_power_watts                 : float = 0.0 
    pretty_normalised_power_watts          : str   = "" 
    intensity_factor                       : float = 0.0 
    pretty_intensity_factor                : str   = ""
    effort_constraint_violation_reason     : str   = ""
    pretty_effort_constraint_violation_reason     : str   = ""

    @staticmethod
    def calculate_zwift_racing_score_cat(rider: RiderComputeItem) -> str:
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

    @staticmethod
    def calculate_zwiftracingapp_zpFTP_cat(rider: RiderComputeItem)-> str:
        return rider.zwift_cat_open

    @staticmethod
    def calculate_zwiftracingapp_zpFTP_wkg(rider: RiderComputeItem)-> float:
        return safe_divide(rider.velo_zwiftpower_zFTP_watts,rider.weight_kg)

    @staticmethod
    def make_pretty_zwiftracingapp_cat(rider: RiderComputeItem) -> str:

        return f"{rider.velo_cat_num_30_days}-{rider.velo_cat_name_30_days}"

    @staticmethod
    def make_pretty_consolidated_racing_cat_descriptor(rider: RiderComputeItem) -> str:
        if rider.zwift_cat_open:
            answer = f"{rider.zwift_cat_open} {RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        else:
            answer = f"{" "} {RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        return answer

    @staticmethod
    def  make_pretty_zwiftracingapp_zpFTP_wkg(rider: RiderComputeItem) -> str:
        xx = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider)
        return f"{format_number_2dp(xx)}wkg"


    @staticmethod
    def make_pretty_pull(rider : RiderComputeItem, plan: RiderContributionItem) -> str:

        if plan.p1_duration == 0:
            return "------"
        duration_str = f"{int(round(plan.p1_duration)):3d}sec"
        return duration_str

    @staticmethod
    def make_pretty_pull_comparison(rider : RiderComputeItem, plan: RiderContributionItem) -> str:

        my_ftp_wkg : float = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider)
        my_ftp_wkg_rounded_as_str = f"{round(my_ftp_wkg,1)}wkg" 
        if plan.p1_duration == 0:
            return my_ftp_wkg_rounded_as_str + " " + "-----------"
        p1_wkg = f"{round(rider.get_watts_per_kg(plan.p1_w),1)}wkg"
        p1_over_zFtp_ratio = (
            f"{round(100 * safe_divide(plan.p1_w, rider.velo_zwiftpower_zFTP_watts)):>4}%"
            if rider.velo_zwiftpower_zFTP_watts != 0
            else "N/A"
        )
        return f"{my_ftp_wkg_rounded_as_str} {p1_wkg} {p1_over_zFtp_ratio}"


    @staticmethod
    def make_pretty_p1_2_3_4_w(p1_w: float, p2_w: float, p3_w: float, p4_w: float) -> str:
        def pretty(val: float) -> str:
            return "---" if round_to_nearest_10(val) == 0 else str(round_to_nearest_10(val))
        return f"{pretty(p1_w)} {pretty(p2_w)} {pretty(p3_w)} {pretty(p4_w)}"

    @staticmethod
    def make_pretty_average_watts(rider : RiderComputeItem, contribution: RiderContributionItem) -> str:

        av_wkg = rider.get_watts_per_kg(contribution.average_watts)

        return f"{round(av_wkg,1)}wkg {round(contribution.average_watts)}w"


    @staticmethod
    def from_RiderContributionItem(rider : RiderComputeItem, contribution: Optional[RiderContributionItem]) -> "RiderContributionDisplayObject":
        if contribution is None:
            return RiderContributionDisplayObject()
        return RiderContributionDisplayObject(
            name                                   = rider.name,
            pretty_concatenated_racing_cat_descriptor     = RiderContributionDisplayObject.make_pretty_consolidated_racing_cat_descriptor(rider),
            zwift_racing_score                      = rider.zwift_racing_score,
            zwift_zrs_cat                          = RiderContributionDisplayObject.calculate_zwift_racing_score_cat(rider),
            zwiftracingapp_zpFTP_cat               = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_cat(rider),
            zwiftracingapp_pretty_cat_descriptor   = RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider),
            velo_zpftp_watts                       = rider.velo_zwiftpower_zFTP_watts,
            zwiftracingapp_zpFTP_wkg               = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider),
            pretty_zwiftracingapp_zpFTP_wkg        = RiderContributionDisplayObject.make_pretty_zwiftracingapp_zpFTP_wkg(rider),
            p1_duration                            = contribution.p1_duration,
            p1_wkg                                 = safe_divide(contribution.p1_w, rider.weight_kg),
            pretty_pull                            = RiderContributionDisplayObject.make_pretty_pull(rider, contribution),
            pretty_pull_comparison                  = RiderContributionDisplayObject.make_pretty_pull_comparison(rider, contribution),
            p1_ratio_to_1hr_w                      = safe_divide(contribution.p1_w, rider.get_1_hour_curvefit_watts()),
            p1_ratio_to_zwiftracingapp_zpFTP       = safe_divide(contribution.p1_w, rider.velo_zwiftpower_zFTP_watts),
            p1_w                                   = contribution.p1_w,
            p2_w                                   = contribution.p2_w,
            p3_w                                   = contribution.p3_w,
            p4_w                                   = contribution.p4_w,     
            pretty_p1_2_3_4_w                        = RiderContributionDisplayObject.make_pretty_p1_2_3_4_w(contribution.p1_w, contribution.p2_w, contribution.p3_w, contribution.p4_w),
            jgh_60_min_watts                        = rider.get_1_hour_curvefit_watts(),
            average_watts                          = contribution.average_watts,
            average_wkg                            = safe_divide(contribution.average_watts, rider.weight_kg),
            pretty_average_watts                   = RiderContributionDisplayObject.make_pretty_average_watts(rider, contribution),
            normalised_power_watts                 = contribution.normalized_watts,
            pretty_normalised_power_watts          = f"{round(contribution.normalized_watts)}w",
            intensity_factor                       = contribution.intensity_factor,
            pretty_intensity_factor                = f"{round(100*contribution.intensity_factor)}%",
            effort_constraint_violation_reason     = contribution.effort_constraint_violation_reason,
            pretty_effort_constraint_violation_reason = contribution.effort_constraint_violation_reason if contribution.effort_constraint_violation_reason else ""
        )


    @staticmethod
    def from_RiderContributionItems(riders: Dict[RiderComputeItem, RiderContributionItem]) -> Dict[RiderComputeItem, "RiderContributionDisplayObject"]:
        if not riders:
            return {}

        answer: Dict[RiderComputeItem, RiderContributionDisplayObject] = defaultdict(RiderContributionDisplayObject)

        for rider, item in riders.items():
            rider_contribution_display_object   = RiderContributionDisplayObject.from_RiderContributionItem(rider, item)
            answer[rider]                       = rider_contribution_display_object
        
        index =1;
        for contribution_display_object in answer.values():
            contribution_display_object.index = index
            index += 1

        return answer

@dataclass
class PacelineComputationReportDisplayObject:
    guid                                        : str = ""
    display_caption_left_aligned                : str = ""
    display_caption_right_aligned               : str = ""
    algorithm_ran_to_completion                 : bool = False
    compute_iterations_performed_count          : int  = 0
    computational_time                          : float = 0.0
    exertion_intensity_constraint_used          : float = 0.95 # Default to 95% of one hour power, can be overridden by caller
    calculated_average_speed_of_paceline_kph    : float = 0.0
    calculated_dispersion_of_intensity_of_effort : float = 0.0
    rider_contributions_display_objects          : Dict[RiderComputeItem, RiderContributionDisplayObject] = field(default_factory=lambda: defaultdict(RiderContributionDisplayObject))

    @staticmethod
    def from_PacelineComputationReportItem(report: Union[PacelineComputationReportItem, None]) -> "PacelineComputationReportDisplayObject":
        if report is None:
            return PacelineComputationReportDisplayObject()

        rider_contributions_display_objects : Dict[RiderComputeItem, RiderContributionDisplayObject]  = RiderContributionDisplayObject.from_RiderContributionItems(report.rider_contributions) if report.rider_contributions else defaultdict(RiderContributionDisplayObject)
        
        answer = PacelineComputationReportDisplayObject(
            guid                                        = report.guid,
            algorithm_ran_to_completion                 = report.algorithm_ran_to_completion,
            compute_iterations_performed_count          = report.compute_iterations_performed_count,
            computational_time                          = report.computational_time,
            exertion_intensity_constraint_used          = report.exertion_intensity_constraint_used,
            calculated_average_speed_of_paceline_kph    = report.calculated_average_speed_of_paceline_kph,
            calculated_dispersion_of_intensity_of_effort = report.calculated_dispersion_of_intensity_of_effort,
            rider_contributions_display_objects         = rider_contributions_display_objects,
        )
        return answer

    @staticmethod
    def from_PacelineComputationReportItems(reports: Union[List[PacelineComputationReportItem], None]) -> List["PacelineComputationReportDisplayObject"]:
        if not reports:
            return []
        answer: List[PacelineComputationReportDisplayObject] = []
        for report in reports:
            answer.append(PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report))

        return answer

@dataclass
class PackageOfPacelineComputationReportDisplayObject:
    caption                            : str = ""
    total_pull_sequences_examined      : int = 0
    total_compute_iterations_performed : int = 0
    solutions                          : Dict[PacelinePlanTypeEnum, PacelineComputationReportDisplayObject] = field(default_factory=lambda: defaultdict(PacelineComputationReportDisplayObject))

    @staticmethod
    def from_PackageOfPacelineComputationReportItem(
        report: Union['PackageOfPacelineComputationReportItem', None]
    ) -> "PackageOfPacelineComputationReportDisplayObject":
        """
        Factory method to create a display object for all paceline solutions from a computation report item.
        Missing solutions will be present as empty PacelineComputationReportDisplayObject instances.
        """
        if report is None:
            return PackageOfPacelineComputationReportDisplayObject()

        solutions : Dict[PacelinePlanTypeEnum, PacelineComputationReportDisplayObject]  = defaultdict(PacelineComputationReportDisplayObject)

        for plan_type in PacelinePlanTypeEnum:
            solution_item           = report.dict_of_solutions.get(plan_type)
            solutions[plan_type]    = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(solution_item)

        return PackageOfPacelineComputationReportDisplayObject(
            total_pull_sequences_examined      = report.total_pull_sequences_examined,
            total_compute_iterations_performed = report.total_compute_iterations_performed,
            solutions                          = solutions,
        )
    
