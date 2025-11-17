from typing import Dict, List
from pydantic import BaseModel, RootModel

# this class belongs to me, so I don't need the paraphenalia 
# for pydantic validation_alias_choices_map, etc

class RegressionModellingDTO(BaseModel):
    zwift_id: str = ""
    name                            : str           = ""    # Name of the rider
    gender                          : str           = ""    # Gender of the rider
    weight_kg                       : float         = 0.0
    height_cm                       : float         = 0.0
    age_years                       : float         = 0.0   # Age of the rider in years
    zwift_racing_score              : float         = 0.0   # Zwift racing score
    zwift_cat_open                  : str           = ""    # A+, A, B, C, D, E
    zwift_ftp_watts                 : float         = 0.0
    jgh_60_min_watts              : float         = 0.0
    jgh_40_minute_watts             : float         = 0.0
    velo_zpftp_watts                : float         = 0.0
    velo_rating_30_days             : float         = 0.0   # Velo score typically over 1000
    velo_cat_num_30_days            : int           = 0     # Velo rating 1 to 10
    velo_cat_name_30_days           : str           = ""    # Copper, Silver, Gold etc
    bp_5                            : float         = 0.0
    bp_15                           : float         = 0.0
    bp_30                           : float         = 0.0
    bp_60                           : float         = 0.0
    bp_180                          : float         = 0.0
    bp_300                          : float         = 0.0
    bp_600                          : float         = 0.0
    bp_720                          : float         = 0.0
    bp_900                          : float         = 0.0
    bp_1200                         : float         = 0.0
    bp_1800                         : float         = 0.0
    bp_2400                         : float         = 0.0
    jgh_60_min_curve_coefficient  : float         = 0.0
    jgh_60_min_curve_exponent     : float         = 0.0

class RegressionModellingDTODictModel(RootModel[Dict[str, RegressionModellingDTO]]):
    pass

class RegressionModellingDTOListModel(RootModel[List[RegressionModellingDTO]]):
    pass

