from dataclasses import dataclass
import uuid
from typing import Optional, List, Union
from dataclasses import dataclass, field
from typing import DefaultDict, Optional
from collections import defaultdict
from zsun_rider_item import ZsunItem

@dataclass
class CurveFittingResultItem:
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
    intensity_factor      : float = 0.0
    effort_constraint_violation_reason : str = ""

@dataclass
class PacelineIngredientsItem:
    riders_list                  : List[ZsunItem] = field(default_factory=list)
    sequence_of_pull_periods_sec : List[float]         = field(default_factory=list)
    pull_speeds_kph              : List[float]         = field(default_factory=list)
    max_exertion_intensity_factor: float               = 0.95 # Default to 95% of one hour power, can be overridden by caller

@dataclass
class PacelineComputationReportItem:
    guid                                        : str = field(default_factory=lambda: str(uuid.uuid4()))
    algorithm_ran_to_completion                 : bool = False
    compute_iterations_performed_count          : int  = 0
    exertion_intensity_constraint_used          : float = 0.95 # Default to 95% of one hour power, can be overridden by caller
    calculated_average_speed_of_paceline_kph    : float = 0.0
    calculated_dispersion_of_intensity_of_effort : float = 0.0
    rider_contributions                         : DefaultDict[ZsunItem, RiderContributionItem] = field(default_factory=lambda: defaultdict(RiderContributionItem))

@dataclass
class PacelineSolutionsComputationReportItem:
    guid                                  : str = field(default_factory=lambda: str(uuid.uuid4()))
    total_pull_sequences_examined         : int   = 0
    total_compute_iterations_performed    : int   = 0
    computational_time                    : float = 0.0
    thirty_sec_solution                   : Union[PacelineComputationReportItem, None] = None
    sixty_sec_solution                    : Union[PacelineComputationReportItem, None] = None
    balanced_intensity_of_effort_solution : Union[PacelineComputationReportItem, None] = None
    everybody_pull_hard_solution          : Union[PacelineComputationReportItem, None] = None
    hang_in_solution                      : Union[PacelineComputationReportItem, None] = None
    all_solutions                         : Union[List[PacelineComputationReportItem], None] = None

@dataclass
class WorthyCandidateSolutionItem:
    tag        : str                                  = ""
    speed_kph  : float                                = float('-inf')
    dispersion : float                                = float('inf')
    solution   : Optional[PacelineComputationReportItem]  = None
