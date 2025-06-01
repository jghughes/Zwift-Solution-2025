from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union

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

