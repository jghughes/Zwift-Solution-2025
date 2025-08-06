from dataclasses import dataclass,  asdict
from typing import Optional
import numpy as np
from jgh_number import safe_divide
from zsun_rider_dto import ZsunDTO 
from jgh_power_curve_fit_models import decay_model_numpy

@dataclass(frozen=True, eq=True)  # immutable and hashable, we use this as a dictionary key everywhere
class ZsunItem:
    """
    A frozen data class representing a Zwift rider.
    Can be used as a cache key or dictionary key, or in a set.
    """

    zwift_id                          : str   = ""    # Zwift ID of the rider
    name                              : str   = ""    # Name of the rider
    weight_kg                         : float = 0.0   # Weight of the rider in kilograms
    height_cm                         : float = 0.0   # Height of the rider in centimeters
    gender                            : str   = ""    # Gender of the rider
    age_years                         : float = 0.0   # Age of the rider in years
    age_group                          : str   = ""    # Age group of the rider
    zwift_ftp                         : float = 0.0   # Originates in Zwift profile
    zwiftpower_zFTP                   : float = 0.0   # Originates in Zwiftpower profile
    zwiftracingapp_zpFTP              : float = 0.0   # Originates in Zwiftracingapp profile
    zsun_one_hour_watts               : float = 0.0   # Calculated by JGH
    zsun_CP                           : float = 0.0   # Critical power in watts
    zsun_AWC                          : float = 0.0   # Critical power W' in kilojoules
    zwift_zrs                         : float = 0.0   # Zwift racing score
    zwift_cat                         : str   = ""    # A+, A, B, C, D, E
    zwiftracingapp_score              : float = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num            : int   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name           : str   = ""    # Copper, Silver, Gold etc
    zwiftracingapp_CP                 : float = 0.0   # Critical power in watts
    zwiftracingapp_AWC                : float = 0.0   # Anaerobic work capacity in kilojoules
    zsun_one_hour_curve_coefficient   : float = 0.0   # Coefficient for FTP modeling
    zsun_one_hour_curve_exponent      : float = 0.0   # Exponent for FTP modeling
    zsun_TTT_pull_curve_coefficient   : float = 0.0   # Coefficient for pull modeling
    zsun_TTT_pull_curve_exponent      : float = 0.0   # Exponent for pull modeling
    zsun_TTT_pull_curve_fit_r_squared : float = 0.0   # R-squared value for the curve fit of the FTP data
    zsun_when_curves_fitted           : str   = ""    # Timestamp indicating when the models were fitted

    @staticmethod
    def create(zwiftid: str, name: str, weight_kg: float, height_cm: float, gender: str, 
        zwiftpower_zFTP: float, zwift_zrs: int, zwiftracingapp_cat_num: int
    ) -> 'ZsunItem':
        """
        Create a ZsunItem instance with the given parameters

        Args:
           zwift_id            (int)  : The Zwift ID of the rider.
            name               (str)  : The name of the rider.
            weight_kg             (float): The weight_kg of the rider in kilograms.
            height_cm             (float): The height_cm of the rider in centimeters.
            gender             (Gender): The gender of the rider.
            zwiftpower_zFTP                (float): Functional Threshold Power in watts.
            zwift_zrs (int)  : Zwift racing score.
            zwiftracingapp_cat_num        (int)  : Velo rating.
    
        Returns:
            ZsunItem: A ZsunItem instance with the given parameters.
        """

        instance = ZsunItem(
            zwift_id=zwiftid,
            name=name,
            weight_kg=weight_kg,
            height_cm=height_cm,
            gender=gender,
            zwiftpower_zFTP=zwiftpower_zFTP,
            zwift_zrs=zwift_zrs,
            zwiftracingapp_cat_num=zwiftracingapp_cat_num
        )

        return instance

    def get_strength_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.get_standard_1_minute_pull_watts(),80.0) # arbitrary default 80kg
        return safe_divide(self.get_standard_1_minute_pull_watts(),self.weight_kg)

    def get_standard_pull_watts(self, seconds : float)-> float:

        permissable_watts = self.get_one_hour_watts() # default

        if seconds == 0:
            permissable_watts = self.get_standard_30sec_pull_watts()
        if seconds == 30:
            permissable_watts = self.get_standard_30sec_pull_watts()
        if seconds == 60:
            permissable_watts = self.get_standard_1_minute_pull_watts()
        if seconds == 120:
            permissable_watts = self.get_standard_2_minute_pull_watts()
        if seconds == 180:
            permissable_watts = self.get_standard_3_minute_pull_watts()
        if seconds == 240:
            permissable_watts = self.get_standard_4_minute_pull_watts()
         
        return permissable_watts

    def get_standard_00sec_pull_watts(self) -> float:
        return self.get_standard_30sec_pull_watts()

    def get_standard_30sec_pull_watts(self) -> float:
        # apply 3.5 minute watts
        pull_short = decay_model_numpy(np.array([210]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([210]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_short[0], one_hour[0])
        return answer

    def get_standard_1_minute_pull_watts(self) -> float:
        # apply 5 minute watts
        pull_medium = decay_model_numpy(np.array([300]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([300]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_medium[0], one_hour[0])
        return answer

    def get_standard_2_minute_pull_watts(self) -> float:
        # # apply 12 minute watts
        pull_long = decay_model_numpy(np.array([720]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([720]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_long[0], one_hour[0])
        return answer

    def get_standard_3_minute_pull_watts(self) -> float:
        # apply 15 minute watts
        pull_long = decay_model_numpy(np.array([900]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([900]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = max(pull_long[0], one_hour[0])
        return answer

    def get_standard_4_minute_pull_watts(self) -> float:
        # apply 18 minute watts
        one_hour = decay_model_numpy(np.array([1080]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_standard_5_minute_pull_watts(self) -> float:
        # apply 20 minute watts
        one_hour = decay_model_numpy(np.array([1200]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_one_hour_watts(self) -> float:

        ftp = decay_model_numpy(np.array([3_600]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)

        answer =  ftp[0]

        return answer

    def get_one_hour_wkg(self) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide( self.get_one_hour_watts(), self.weight_kg)

    def get_watts_per_kg(self, wattage : float) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide(wattage,self.weight_kg)

    def get_n_second_watts(self, seconds: float) -> float:

        one_hour_curve = decay_model_numpy(np.array([seconds]), self.zsun_one_hour_curve_coefficient, self.zsun_one_hour_curve_exponent)

        if seconds < 900:
            pull_curve = decay_model_numpy(np.array([seconds]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
            answer = max(pull_curve[0], one_hour_curve[0])

        elif seconds >= 900 and seconds < 1200:
            pull_curve = decay_model_numpy(np.array([seconds]), self.zsun_TTT_pull_curve_coefficient, self.zsun_TTT_pull_curve_exponent)
            # Linear transition from max(...) at 900s to one_hour_curve[0] at 1200s
            t = (seconds - 900) / 300.0
            start_val = max(pull_curve[0], one_hour_curve[0])
            end_val = one_hour_curve[0]
            answer = (1 - t) * start_val + t * end_val
        else: 
            answer = one_hour_curve[0]

        return answer

    def get_critical_power_watts(self) -> float:
        return self.zsun_CP

    def get_anaerobic_work_capacity_kj(self) -> float:
        return safe_divide(self.zsun_AWC,1_000.0)

    def get_zwiftracingapp_zpFTP_wkg(self) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide(self.zwiftracingapp_zpFTP, self.weight_kg)

    def get_when_models_fitted(self) -> str:
        return self.zsun_when_curves_fitted

    @staticmethod
    def to_dataTransferObject(item: Optional["ZsunItem"]) -> ZsunDTO:
        if item is None:
            return ZsunDTO()
        return ZsunDTO(
            zwift_id                          = item.zwift_id,
            name                              = item.name,
            weight_kg                         = item.weight_kg,
            height_cm                         = item.height_cm,
            gender                            = item.gender,
            age_years                         = item.age_years,
            age_group                          = item.age_group,
            zwift_ftp                         = item.zwift_ftp,
            zwiftpower_zFTP                   = item.zwiftpower_zFTP,
            zwiftracingapp_zpFTP              = item.zwiftracingapp_zpFTP,
            zsun_one_hour_watts               = item.get_one_hour_watts(),
            zsun_CP                           = item.zsun_CP,
            zsun_AWC                          = item.zsun_AWC,
            zwift_zrs                         = item.zwift_zrs,
            zwift_cat                         = item.zwift_cat,
            zwiftracingapp_score              = item.zwiftracingapp_score,
            zwiftracingapp_cat_num            = item.zwiftracingapp_cat_num,
            zwiftracingapp_cat_name           = item.zwiftracingapp_cat_name,
            zwiftracingapp_CP                 = item.zwiftracingapp_CP,
            zwiftracingapp_AWC                = item.zwiftracingapp_AWC,
            zsun_one_hour_curve_coefficient   = item.zsun_one_hour_curve_coefficient,
            zsun_one_hour_curve_exponent      = item.zsun_one_hour_curve_exponent,
            zsun_TTT_pull_curve_coefficient   = item.zsun_TTT_pull_curve_coefficient,
            zsun_TTT_pull_curve_exponent      = item.zsun_TTT_pull_curve_exponent,
            zsun_TTT_pull_curve_fit_r_squared = item.zsun_TTT_pull_curve_fit_r_squared,
            zsun_when_curves_fitted           = item.zsun_when_curves_fitted,
        )

    @staticmethod
    def from_dataTransferObject(dto: Optional[ZsunDTO]) -> "ZsunItem":
        if dto is None:
            return ZsunItem()
        return ZsunItem(
            zwift_id                          = dto.zwift_id or "",
            name                              = dto.name or "",
            weight_kg                         = dto.weight_kg or 0.0,
            height_cm                         = dto.height_cm or 0.0,
            gender                            = dto.gender or "",
            age_years                         = dto.age_years or 0.0,
            age_group                          = dto.age_group or "",
            zwift_ftp                         = dto.zwift_ftp or 0.0,
            zwiftpower_zFTP                   = dto.zwiftpower_zFTP or 0.0,
            zwiftracingapp_zpFTP              = dto.zwiftracingapp_zpFTP or 0.0,
            zsun_one_hour_watts               = dto.zsun_one_hour_watts or 0.0,
            zsun_CP                           = dto.zsun_CP or 0.0,
            zsun_AWC                          = dto.zsun_AWC or 0.0,
            zwift_zrs                         = dto.zwift_zrs or 0.0,
            zwift_cat                         = dto.zwift_cat or "",
            zwiftracingapp_score              = dto.zwiftracingapp_score or 0.0,
            zwiftracingapp_cat_num            = dto.zwiftracingapp_cat_num or 0,
            zwiftracingapp_cat_name           = dto.zwiftracingapp_cat_name or "",
            zwiftracingapp_CP                 = dto.zwiftracingapp_CP or 0.0,
            zwiftracingapp_AWC                = dto.zwiftracingapp_AWC or 0.0,
            zsun_one_hour_curve_coefficient   = dto.zsun_one_hour_curve_coefficient or 0.0,
            zsun_one_hour_curve_exponent      = dto.zsun_one_hour_curve_exponent or 0.0,
            zsun_TTT_pull_curve_coefficient   = dto.zsun_TTT_pull_curve_coefficient or 0.0,
            zsun_TTT_pull_curve_exponent      = dto.zsun_TTT_pull_curve_exponent or 0.0,
            zsun_TTT_pull_curve_fit_r_squared = dto.zsun_TTT_pull_curve_fit_r_squared or 0.0,
            zsun_when_curves_fitted           = dto.zsun_when_curves_fitted or "",
        )


