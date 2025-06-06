from dataclasses import dataclass
from typing import Optional, List
from dataclasses import dataclass, field
from typing import DefaultDict, Optional
from collections import defaultdict
from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem

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
class PullPlanSolution:
    compute_iterations_count      : int
    rider_pull_plans              : DefaultDict[ZsunRiderItem, RiderPullPlanItem]
    limiting_rider                : Optional[ZsunRiderItem]

@dataclass
class OptimalPullPlansResult:
    total_num_of_all_pull_plan_period_schedules : int   = 0
    total_compute_iterations_count              : int   = 0
    computational_time                          : float = 0.0
    solutions                                   : List[PullPlanSolution] = field(default_factory=list)


@dataclass
class PullPlanComputationResult:
    num_compute_iterations_done : int  = 0
    rider_pull_plans            : DefaultDict[ZsunRiderItem, RiderPullPlanItem] = field(default_factory=lambda: defaultdict(RiderPullPlanItem))
    limiting_rider              : Optional[ZsunRiderItem]  = None

@dataclass
class PullPlanComputationParams:
    riders_list                  : List[ZsunRiderItem] = field(default_factory=list)
    standard_pull_periods_sec    : List[float]         = field(default_factory=list)
    pull_speeds_kph              : List[float]         = field(default_factory=list)
    max_exertion_intensity_factor: float               = 0.95