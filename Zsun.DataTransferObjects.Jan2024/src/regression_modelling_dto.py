from dataclasses import dataclass
from typing import Optional


@dataclass
class RegressionModellingDTO:
    zwift_id                   : Optional[str]   = ""    # Zwift ID of the rider
    name                       : Optional[str]   = ""    # Name of the rider
    gender                     : Optional[str]   = ""    # Gender of the rider
    weight_kg                  : Optional[float] = 0.0
    height_cm                  : Optional[float] = 0.0
    age_years                  : Optional[float] = 0.0   # Age of the rider in years
    zwift_zrs                  : Optional[float] = 0.0     # Zwift racing score
    zwift_cat                  : Optional[str]   = ""    # A+, A, B, C, D, E
    zwift_ftp                  : Optional[float]  = 0.0    
    zsun_one_hour_watts        : Optional[float]  = 0.0
    zsun_40_minute_watts       : Optional[float]  = 0.0
    zwiftracingapp_zpFTP       : Optional[float] = 0.0
    zwiftracingapp_score       : Optional[float] = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num     : Optional[int]   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name    : Optional[Optional[str]] = ""    # Copper, Silver, Gold etc
    bp_5    : Optional[float] = 0.0
    bp_15   : Optional[float] = 0.0
    bp_30   : Optional[float] = 0.0
    bp_60   : Optional[float] = 0.0
    bp_180  : Optional[float] = 0.0
    bp_300  : Optional[float] = 0.0
    bp_600  : Optional[float] = 0.0
    bp_720  : Optional[float] = 0.0
    bp_900  : Optional[float] = 0.0
    bp_1200 : Optional[float] = 0.0
    bp_1800 : Optional[float] = 0.0
    bp_2400 : Optional[float] = 0.0
    zsun_one_hour_curve_coefficient : Optional[float] = 0.0
    zsun_one_hour_curve_exponent : Optional[float] = 0.0

