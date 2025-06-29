from dataclasses import dataclass, field
from typing import Optional, List, Union, DefaultDict
from collections import defaultdict
from jgh_formatting import round_to_nearest_10, format_number_2dp
from  jgh_number import safe_divide
from zsun_rider_item import ZsunRiderItem
from computation_classes import RiderContributionItem, PacelineComputationReportItem, PacelineSolutionsComputationReportItem
from constants import PacelineSolutionType

@dataclass
@dataclass
class RiderContributionDisplayObject():
    name                                   : str   = ""
    pretty_concatenated_racing_cat_descriptor     : str   = ""
    zwift_zrs                              : float = 0.0 
    zwift_zrs_cat                          : str   = ""
    zwiftracingapp_zpFTP_cat               : str   = ""
    zwiftracingapp_pretty_cat_descriptor   : str   = ""
    zwiftracingapp_zpFTP                   : float = 0.0 
    zwiftracingapp_zpFTP_wkg               : float = 0.0 
    pretty_zwiftracingapp_zpFTP_wkg        : str = "" 
    speed_kph                              : float = 0.0 
    p1_duration                            : float = 0.0 
    p1_wkg                                 : float = 0.0 
    pretty_pull                            : str   = ""
    pretty_pull_suffix                     : str   = ""
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
    pretty_normalised_power_watts          : str   = "" 
    intensity_factor                       : float = 0.0 
    pretty_intensity_factor                : str   = ""
    effort_constraint_violation_reason     : str   = ""
    pretty_effort_constraint_violation_reason     : str   = ""

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
        return safe_divide(rider.zwiftracingapp_zpFTP,rider.weight_kg)

    @staticmethod
    def make_pretty_zwiftracingapp_cat(rider: ZsunRiderItem) -> str:

        return f"{rider.zwiftracingapp_cat_num}-{rider.zwiftracingapp_cat_name}"

    @staticmethod
    def make_pretty_consolidated_racing_cat_descriptor(rider: ZsunRiderItem) -> str:
        if rider.zwift_cat:
            answer = f"{rider.zwift_cat} {RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        else:
            answer = f"{" "} {RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider)}"
        return answer

    @staticmethod
    def  make_pretty_zwiftracingapp_zpFTP_wkg(rider: ZsunRiderItem) -> str:
        xx = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider)
        return f"{format_number_2dp(xx)}wkg"


    @staticmethod
    def make_pretty_pull(rider : ZsunRiderItem, plan: RiderContributionItem) -> str:

        if plan.p1_duration == 0:
            return "            "
            # return "   0sec   0w"

        duration_str = f"{int(round(plan.p1_duration)):3d}sec"

        p1_w = f"{str(round_to_nearest_10(plan.p1_w))}"

        return f"{p1_w} {duration_str}"

    @staticmethod
    def make_pretty_pull_suffix(rider : ZsunRiderItem, plan: RiderContributionItem) -> str:
        if plan.p1_duration == 0:
            return "           "
            # return "   0wkg  0%"

        p1_wkg = f"{round(rider.get_watts_per_kg(plan.p1_w),1)}wkg"

        p1_over_zFtp_ratio = f"{round(100*plan.p1_w/rider.zwiftracingapp_zpFTP):>4}%"

        return f"{p1_wkg} {p1_over_zFtp_ratio}"


    @staticmethod
    def make_pretty_p2_3_4_w(p2_w: float, p3_w: float, p4_w: float) -> str:
        def pretty(val: float) -> str:
            return "   " if round_to_nearest_10(val) == 0 else str(round_to_nearest_10(val))
        return f"{pretty(p2_w)} {pretty(p3_w)} {pretty(p4_w)}"

    @staticmethod
    def make_pretty_average_watts(rider : ZsunRiderItem, contribution: RiderContributionItem) -> str:

        av_wkg = rider.get_watts_per_kg(contribution.average_watts)

        return f"{round(contribution.average_watts)} {round(av_wkg,1)}wkg"


    @staticmethod
    def from_RiderContributionItem(rider : ZsunRiderItem, contribution: Optional[RiderContributionItem]) -> "RiderContributionDisplayObject":
        if contribution is None:
            return RiderContributionDisplayObject()
        return RiderContributionDisplayObject(
            name                                   = rider.name,
            pretty_concatenated_racing_cat_descriptor     = RiderContributionDisplayObject.make_pretty_consolidated_racing_cat_descriptor(rider),
            zwift_zrs                              = rider.zwift_zrs,
            zwift_zrs_cat                          = RiderContributionDisplayObject.calculate_zwift_racing_score_cat(rider),
            zwiftracingapp_zpFTP_cat               = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_cat(rider),
            zwiftracingapp_pretty_cat_descriptor   = RiderContributionDisplayObject.make_pretty_zwiftracingapp_cat(rider),
            zwiftracingapp_zpFTP                   = rider.zwiftracingapp_zpFTP,
            zwiftracingapp_zpFTP_wkg               = RiderContributionDisplayObject.calculate_zwiftracingapp_zpFTP_wkg(rider),
            pretty_zwiftracingapp_zpFTP_wkg        = RiderContributionDisplayObject.make_pretty_zwiftracingapp_zpFTP_wkg(rider),
            p1_duration                            = contribution.p1_duration,
            p1_wkg                                 = contribution.p1_w/rider.weight_kg,
            pretty_pull                            = RiderContributionDisplayObject.make_pretty_pull(rider, contribution),
            pretty_pull_suffix                     = RiderContributionDisplayObject.make_pretty_pull_suffix(rider, contribution),
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
            pretty_normalised_power_watts          = f"{round(contribution.normalized_watts)}",
            intensity_factor                       = contribution.intensity_factor,
            pretty_intensity_factor                = f"{round(100*contribution.intensity_factor,1)}%",
            effort_constraint_violation_reason     = contribution.effort_constraint_violation_reason,
            pretty_effort_constraint_violation_reason = contribution.effort_constraint_violation_reason if contribution.effort_constraint_violation_reason else ""
        )


    @staticmethod
    def from_RiderContributionItems(riders: DefaultDict[ZsunRiderItem, RiderContributionItem]) -> DefaultDict[ZsunRiderItem, "RiderContributionDisplayObject"]:
        if not riders:
            return DefaultDict(RiderContributionDisplayObject)

        answer: DefaultDict[ZsunRiderItem, RiderContributionDisplayObject] = defaultdict(RiderContributionDisplayObject)

        for rider, item in riders.items():
            rider_contribution_display_object = RiderContributionDisplayObject.from_RiderContributionItem(rider, item)
            answer[rider] = rider_contribution_display_object

        return answer


@dataclass
class PacelineComputationReportDisplayObject:
    guid                                        : str = ""
    algorithm_ran_to_completion                 : bool = False
    compute_iterations_performed_count          : int  = 0
    exertion_intensity_constraint_used          : float = 0.95 # Default to 95% of one hour power, can be overridden by caller
    calculated_average_speed_of_paceline_kph    : float = 0.0
    calculated_dispersion_of_intensity_of_effort : float = 0.0
    display_caption                              :  str = ""
    rider_contributions_display_objects          : DefaultDict[ZsunRiderItem, RiderContributionDisplayObject] = field(default_factory=lambda: defaultdict(RiderContributionDisplayObject))

    @staticmethod
    def from_PacelineComputationReportItem(report: Union[PacelineComputationReportItem, None]) -> "PacelineComputationReportDisplayObject":
        if report is None:
            return PacelineComputationReportDisplayObject()

        rider_contributions_display_objects : DefaultDict[ZsunRiderItem, RiderContributionDisplayObject]  = RiderContributionDisplayObject.from_RiderContributionItems(report.rider_contributions) if report.rider_contributions else defaultdict(RiderContributionDisplayObject)
        
        answer = PacelineComputationReportDisplayObject(
            guid                                        = report.guid,
            algorithm_ran_to_completion                 = report.algorithm_ran_to_completion,
            compute_iterations_performed_count          = report.compute_iterations_performed_count,
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
class PacelineSolutionsComputationReportDisplayObject:
    guid                               : str = ""
    total_pull_sequences_examined      : int = 0
    total_compute_iterations_performed : int = 0
    computational_time                 : float = 0.0
    solutions                          :  DefaultDict[PacelineSolutionType, PacelineComputationReportDisplayObject] = field(default_factory=lambda: defaultdict(PacelineComputationReportDisplayObject))

    @staticmethod
    def from_PacelineSolutionsComputationReportItem(
        report: Union['PacelineSolutionsComputationReportItem', None]
    ) -> "PacelineSolutionsComputationReportDisplayObject":
        """
        Factory method to create a display object for all paceline solutions from a computation report item.
        Missing solutions will be present as empty PacelineComputationReportDisplayObject instances.
        """
        if report is None:
            return PacelineSolutionsComputationReportDisplayObject()

        solutions = defaultdict(PacelineComputationReportDisplayObject)
        solutions[PacelineSolutionType.THIRTY_SEC_PULL     ] = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.thirty_sec_solution)
        solutions[PacelineSolutionType.IDENTICAL_PULL      ] = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.identical_pull_solution)
        solutions[PacelineSolutionType.BALANCED_INTENSITY  ] = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.balanced_intensity_of_effort_solution)
        solutions[PacelineSolutionType.EVERYBODY_PULL_HARD ] = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.everybody_pull_hard_solution)
        solutions[PacelineSolutionType.FASTEST             ] = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.hang_in_solution)
        # LAST_FIVE and LAST_FOUR must be set externally

        return PacelineSolutionsComputationReportDisplayObject(
            guid                               = report.guid,
            total_pull_sequences_examined      = report.total_pull_sequences_examined,
            total_compute_iterations_performed = report.total_compute_iterations_performed,
            computational_time                 = report.computational_time,
            solutions                          = solutions,
        )
    
    #     guid                                                : str = ""
#     total_pull_sequences_examined                       : int   = 0
#     total_compute_iterations_performed                  : int   = 0
#     computational_time                                  : float = 0.0
#     thirty_sec_solution_display_object                   : Union[PacelineComputationReportDisplayObject, None] = None
#     identical_pull_solution_display_object               : Union[PacelineComputationReportDisplayObject, None] = None
#     balanced_intensity_of_effort_solution_display_object : Union[PacelineComputationReportDisplayObject, None] = None
#     everybody_pull_hard_solution_display_object          : Union[PacelineComputationReportDisplayObject, None] = None
#     hang_in_solution_display_object                      : Union[PacelineComputationReportDisplayObject, None] = None
#     last_five_solution_display_object                    : Union[PacelineComputationReportDisplayObject, None] = None
#     last_four_solution_display_object                    : Union[PacelineComputationReportDisplayObject, None] = None
#     # thirty_sec_solution_display_title                  :  str = ""
#     # identical_pull_solution_display_title              :  str = ""
#     # balanced_intensity_of_effort_solution_display_title:  str = ""
#     # everybody_pull_hard_solution_display_title         :  str = ""
#     # hang_in_solution_display_title                     :  str = ""
#     # last_five_solution_display_title                   :  str = ""
#     # last_four_solution_display_title                   :  str = ""



#     @staticmethod
#     def from_PacelineSolutionsComputationReportItem(report: Union[PacelineSolutionsComputationReportItem, None]) -> "PacelineSolutionsComputationReportDisplayObject":
#         if report is None:
#             return PacelineSolutionsComputationReportDisplayObject()
        
#         answer = PacelineSolutionsComputationReportDisplayObject(
#             guid                                                 = report.guid,
#             total_pull_sequences_examined                        = report.total_pull_sequences_examined,
#             total_compute_iterations_performed                   = report.total_compute_iterations_performed,
#             computational_time                                   = report.computational_time,
#             thirty_sec_solution_display_object                   = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.thirty_sec_solution),
#             identical_pull_solution_display_object               = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.identical_pull_solution),
#             balanced_intensity_of_effort_solution_display_object = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.balanced_intensity_of_effort_solution),
#             everybody_pull_hard_solution_display_object          = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.everybody_pull_hard_solution),
#             hang_in_solution_display_object                      = PacelineComputationReportDisplayObject.from_PacelineComputationReportItem(report.hang_in_solution),
#             )

#         # NB. last_five_solution_display_object and last_four_solution_display_object are not set in the original report, they are computed separately. they must be set by the caller if needed.
#         # ditto all the display titles

#         return answer

