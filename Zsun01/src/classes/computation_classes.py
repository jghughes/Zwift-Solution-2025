from dataclasses import dataclass
from ftplib import error_perm

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


# @dataclass(frozen=True, eq=True) 
# class RiderTeamItem:
#     """
#     """
#     riders_working: list[ZsunRiderItem] = field(default_factory=list)
#     riders_resting: list[ZsunRiderItem] = field(default_factory=list)

#     @staticmethod
#     def create(riders: list[ZsunRiderItem]) -> "RiderTeamItem":
#         riders.sort(key=lambda x: x.calculate_strength_wkg(), reverse=True)
#         # assign rank to rank attr sarting with 1
#         for i, rider in enumerate(riders):
#             rider.rank = i + 1
#         team = RiderTeamItem(riders_working=riders, riders_resting=[])
#         return team

#     def sort_riders(self) -> None:
#         riders_working.sort(key=lambda x: x.calculate_strength_wkg(), reverse=True)
#         riders_resting.sort(key=lambda x: x.calculate_strength_wkg(), reverse=True)

#     def demote_rider_from_working_to_resting(self, rider: ZsunRiderItem) -> None:
#         riders_resting.append(rider)
#         riders_working.remove(rider)
#         sort_riders()

#     def promote_rider_from_resting_to_working(self, rider: ZsunRiderItem) -> None:
#         riders_working.append(rider)
#         riders_resting.remove(rider)
#         sort_riders()


@dataclass(frozen=True, eq=True) 
class RiderWorkAssignmentItem:
    position: int = 1
    duration: float = 0
    speed: float = 0


@dataclass(frozen=True, eq=True) 
class RiderExertionItem:
    current_location_in_paceline: int = 0
    speed_kph: float = 0
    duration: float = 0
    wattage: float = 0
    kilojoules: float = 0


@dataclass
class RiderPullPlanItem():
    speed_kph             : float = 0
    p1_duration           : float = 0
    p1_wkg                : float = 0
    p1_ratio_to_1hr_w     : float = 0
    p1_w                  : float = 0
    p2_w                  : float = 0
    p3_w                  : float = 0
    p4_w                  : float = 0
    p__w                  : float = 0
    np_intensity_factor   : float = 0
    diagnostic_message    : str = ""
    

    
@dataclass
class RiderPullPlanDisplayObject():
    name                  : str   = ""
    pretty_cat_descriptor : str   = ""
    zrs_score             : float = 0
    zrs_cat               : str   = ""
    zwiftftp_cat          : str   = ""
    velo_cat              : str   = ""
    zwift_cp              : float = 0
    zwift_w_prime         : float = 0
    zftp                   : float = 0
    ftp_wkg               : float = 0
    speed_kph             : float = 0
    p1_duration         : float = 0
    p1_wkg              : float = 0
    p1_ratio_to_1hr_w   : str   = ""
    p1_4                  : str   = ""
    np_intensity_factor    : float = 0

    
@dataclass(frozen=True, eq=True)
class RiderAggregateEffortItem:
    total_duration: float = 0
    average_speed: float = 0
    total_distance: float = 0
    weighted_average_watts: float = 0
    normalized_average_watts: float = 0
    instantaneous_peak_wattage: float = 0
    position_at_peak_wattage: int = 0
    total_kilojoules_at_weighted_watts: float = 0
    total_kilojoules_at_normalized_watts: float = 0


@dataclass(frozen=True, eq=True) # immutable and hashable
class RiderStressItem():
    zftp: float = 0
    normalised_power: float = 0
    intensity_factor: float = 0

    peak_watts_divided_by_ftp_watts: float = 0
    position_at_peak_wattage : int = 0
    total_normalized_kilojoules_divided_by_ftp_kilojoules: float = 0


