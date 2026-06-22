from dataclasses import dataclass

from typing import Optional
import numpy as np
from constants import AERO_POSITION_FACTOR_DEFAULT
import warnings

from jgh_formulae01 import calculate_rider_kph_from_watts
from jgh_number import safe_divide
from rider_compute_dto import RiderComputeDTO   
from zwift_id_base import FrozenZwiftIdBase

from jgh_power_curve_fit_models import decay_model_numpy

# this domain model is instantiated in model_builders.py

@dataclass(frozen=True, eq=True)  # immutable and hashable, we use this as a dictionary key everywhere
class RiderComputeItem(FrozenZwiftIdBase):
    """
    A frozen data class representing a Zwift rider.
    Can be used as a cache key or dictionary key, or in a set.
    """
    name							: str		= ""		# Name of the rider
    zwift_country_code3				: str		= ""		# 2 letter name of country
    weight_kg						: float		= 0.0		# Weight of the rider in kilograms
    height_cm						: float		= 0.0		# Height of the rider in centimeters
    gender							: str		= ""		# Gender of the rider
    age_years						: float		= 0.0		# Age of the rider in years
    age_group						: str		= ""		# Age group of the rider
    zwift_FTP_watts					: float		= 0.0		# Originates in Zwift profile
    velo_zwiftpower_zFTP_watts		: float		= 0.0		# Originates in Zwiftracingapp profile
    # jgh_60_min_watts				: float		= 0.0		# Calculated by JGH
    zwift_racing_score				: float		= 0.0		# Zwift racing score
    zwift_cat_open					: str		= ""		# A+, A, B, C, D, E
    zwift_cat_women					: str		= ""		# A+, A, B, C, D, E
    velo_rating_30_days				: float		= 0.0		# Velo rating we all use
    velo_cat_num_30_days			: int		= 0			# Velo category 1 to 10
    velo_cat_name_30_days			: str		= ""		# Copper, Silver, Gold etc
    jgh_60_min_curve_coefficient	: float		= 0.0		# Coefficient for FTP modeling
    jgh_60_min_curve_exponent		: float		= 0.0		# Exponent for FTP modeling
    jgh_TTT_pull_curve_coefficient	: float		= 0.0		# Coefficient for pull modeling
    jgh_TTT_pull_curve_exponent		: float		= 0.0		# Exponent for pull modeling
    jgh_TTT_pull_curve_fit_r_squared: float		= 0.0		# R-squared value for the curve fit of the FTP data
    jgh_when_curves_fitted			: str		= ""		# Timestamp indicating when the models were fitted, must be ISO 8601 format YYYY-MM-DDTHH:mm:ss.sssZ

    @staticmethod
    def to_dataTransferObject(item: Optional["RiderComputeItem"]) -> RiderComputeDTO:
        if item is None:
            return RiderComputeDTO()
        return RiderComputeDTO  (
            zwift_id							= item.zwift_id,
            name_racingapp						= item.name,
            zwift_country_code3					= item.zwift_country_code3,
            zwift_weight_kg						= item.weight_kg,
            zwift_height_cm						= item.height_cm,
            zwift_gender						= item.gender,
            zwift_age_years						= item.age_years,
            velo_age_group						= item.age_group,
            zwift_FTP_watts						= item.zwift_FTP_watts,
            velo_zwiftpower_zFTP_watts			= item.velo_zwiftpower_zFTP_watts,
            jgh_60_min_watts					= round(item.get_1_hour_curvefit_watts()),
            jgh_60_min_km_0pc_slope			    = round(item.get_1_hour_distance_km_on_slope(0.0),1),
            jgh_60_min_km_2pc_slope			    = round(item.get_1_hour_distance_km_on_slope(2.0),1),
	        jgh_60_min_km_4pc_slope			    = round(item.get_1_hour_distance_km_on_slope(4.0),1),
            zwift_racing_score					= item.zwift_racing_score,
            zwift_cat_open						= item.zwift_cat_open,
            zwift_cat_women						= item.zwift_cat_women,
            velo_rating_30_days					= item.velo_rating_30_days,
            velo_cat_num_30_days				= item.velo_cat_num_30_days,
            velo_cat_name_30_days				= item.velo_cat_name_30_days,
            jgh_60_min_curve_coefficient		= item.jgh_60_min_curve_coefficient,
            jgh_60_min_curve_exponent			= item.jgh_60_min_curve_exponent,
            jgh_ttt_pull_curve_coefficient		= item.jgh_TTT_pull_curve_coefficient,
            jgh_ttt_pull_curve_exponent			= item.jgh_TTT_pull_curve_exponent,
            jgh_ttt_pull_curve_fit_r_squared	= item.jgh_TTT_pull_curve_fit_r_squared,
            jgh_when_curves_fitted				= item.jgh_when_curves_fitted,
        )

    @staticmethod
    def from_dataTransferObject(dto: Optional[RiderComputeDTO]) -> "RiderComputeItem":
        if dto is None:
            return RiderComputeItem
        return RiderComputeItem(
            zwift_id							= dto.zwift_id or "",
            name								= dto.name_racingapp or "",
            zwift_country_code3					= dto.zwift_country_code3 or "",
            weight_kg							= dto.zwift_weight_kg or 0.0,
            height_cm							= dto.zwift_height_cm or 0.0,
            gender								= dto.zwift_gender or "",
            age_years							= dto.zwift_age_years or 0.0,
            age_group							= dto.velo_age_group or "",
            zwift_FTP_watts						= dto.zwift_FTP_watts or 0.0,
            velo_zwiftpower_zFTP_watts			= dto.velo_zwiftpower_zFTP_watts or 0.0,
            # jgh_60_min_watts					= dto.jgh_60_min_watts or 0.0,
            zwift_racing_score					= dto.zwift_racing_score or 0.0,
            zwift_cat_open						= dto.zwift_cat_open or "",
            zwift_cat_women						= dto.zwift_cat_women or "",
            velo_rating_30_days					= dto.velo_rating_30_days or 0.0,
            velo_cat_num_30_days				= dto.velo_cat_num_30_days or 0,
            velo_cat_name_30_days				= dto.velo_cat_name_30_days or "",
            jgh_60_min_curve_coefficient		= dto.jgh_60_min_curve_coefficient or 0.0,
            jgh_60_min_curve_exponent			= dto.jgh_60_min_curve_exponent or 0.0,
            jgh_TTT_pull_curve_coefficient		= dto.jgh_ttt_pull_curve_coefficient or 0.0,
            jgh_TTT_pull_curve_exponent			= dto.jgh_ttt_pull_curve_exponent or 0.0,
            jgh_TTT_pull_curve_fit_r_squared	= dto.jgh_ttt_pull_curve_fit_r_squared or 0.0,
            jgh_when_curves_fitted				= dto.jgh_when_curves_fitted or "",
        )

    def get_velo_zwiftpower_zFTP_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.velo_zwiftpower_zFTP_watts,80.0) # arbitrary default 80kg
        return safe_divide(self.velo_zwiftpower_zFTP_watts,self.weight_kg)

    def get_proxy_30sec_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.get_proxy_30sec_pull_watts(),80.0) # arbitrary default 80kg
        return safe_divide(self.get_proxy_30sec_pull_watts(),self.weight_kg)

    def get_proxy_1_minute_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.get_proxy_1_minute_pull_watts(),80.0) # arbitrary default 80kg
        return safe_divide(self.get_proxy_1_minute_pull_watts(),self.weight_kg)

    def get_proxy_40_minute_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.get_40_minute_curvefit_watts(),80.0) # arbitrary default 80kg
        return safe_divide(self.get_40_minute_curvefit_watts(),self.weight_kg)

    def get_1_hour_curve_fit_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.get_1_hour_curvefit_watts(),80.0) # arbitrary default 80kg
        return safe_divide(self.get_1_hour_curvefit_watts(),self.weight_kg)

    def get_zwiftracingapp_zpFTP_wkg(self) -> float:
        if self.weight_kg == 0:
            return safe_divide(self.velo_zwiftpower_zFTP_watts,80.0) # arbitrary default 80kg
        return safe_divide(self.velo_zwiftpower_zFTP_watts,self.weight_kg)

    def get_proxy_pull_watts(self, seconds : float)-> float:

        permissable_watts = self.get_1_hour_curvefit_watts() # default

        if seconds == 0:
            permissable_watts = self.get_proxy_30sec_pull_watts()
        if seconds == 30:
            permissable_watts = self.get_proxy_30sec_pull_watts()
        if seconds == 60:
            permissable_watts = self.get_proxy_1_minute_pull_watts()
        if seconds == 120:
            permissable_watts = self.get_proxy_2_minute_pull_watts()
        if seconds == 180:
            permissable_watts = self.get_proxy_3_minute_pull_watts()
        if seconds == 240:
            permissable_watts = self.get_proxy_4_minute_pull_watts()
         
        return permissable_watts

    def get_proxy_30sec_pull_watts(self) -> float:
        # apply 3.5 minute watts
        pull_short = decay_model_numpy(np.array([210]), self.jgh_TTT_pull_curve_coefficient, self.jgh_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([210]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = max(pull_short[0], one_hour[0])
        return answer

    def get_proxy_1_minute_pull_watts(self) -> float:
        # apply 5 minute watts
        pull_medium = decay_model_numpy(np.array([300]), self.jgh_TTT_pull_curve_coefficient, self.jgh_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([300]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = max(pull_medium[0], one_hour[0])
        return answer

    def get_proxy_2_minute_pull_watts(self) -> float:
        # # apply 12 minute watts
        pull_long = decay_model_numpy(np.array([720]), self.jgh_TTT_pull_curve_coefficient, self.jgh_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([720]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = max(pull_long[0], one_hour[0])
        return answer

    def get_proxy_3_minute_pull_watts(self) -> float:
        # apply 15 minute watts
        pull_long = decay_model_numpy(np.array([900]), self.jgh_TTT_pull_curve_coefficient, self.jgh_TTT_pull_curve_exponent)
        one_hour = decay_model_numpy(np.array([900]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = max(pull_long[0], one_hour[0])
        return answer

    def get_proxy_4_minute_pull_watts(self) -> float:
        # apply 18 minute watts
        one_hour = decay_model_numpy(np.array([1080]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_proxy_5_minute_pull_watts(self) -> float:
        # apply 20 minute watts
        one_hour = decay_model_numpy(np.array([1200]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_40_minute_curvefit_watts(self) -> float:
        one_hour = decay_model_numpy(np.array([2400]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_50_minute_curvefit_watts(self) -> float:
        one_hour = decay_model_numpy(np.array([3000]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer = one_hour[0]
        return answer

    def get_1_hour_curvefit_watts(self) -> float:
        ftp = decay_model_numpy(np.array([3_600]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        answer =  ftp[0]
        return answer

    def get_1_hour_curvefit_wkg(self) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide( self.get_1_hour_curvefit_watts(), self.weight_kg)

    def get_1_hour_distance_km_on_slope(self, slope_pc : float) -> float:
        try:
            speed_kmh: float = calculate_rider_kph_from_watts(self.get_1_hour_curvefit_watts(), self.weight_kg, self.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
        except RuntimeError as e:
            warnings.warn(f"Error computing get_1_hour_distance_km_on_slope for rider {self.zwift_id} {self.name}: calculate_rider_kph_from_watts failed to converge: {e}. defaulting to 0.0")
            speed_kmh = 0.0

        return speed_kmh

    def get_watts_per_kg(self, wattage : float) -> float:
        if self.weight_kg == 0:
            return 0.0
        return safe_divide(wattage,self.weight_kg)

    def get_n_second_curvefit_y_ordinate_watts(self, seconds: float) -> float:
        one_hour_curve = decay_model_numpy(np.array([seconds]), self.jgh_60_min_curve_coefficient, self.jgh_60_min_curve_exponent)
        if seconds < 900:
            pull_curve = decay_model_numpy(np.array([seconds]), self.jgh_TTT_pull_curve_coefficient, self.jgh_TTT_pull_curve_exponent)
            answer = max(pull_curve[0], one_hour_curve[0])
        elif seconds >= 900 and seconds < 1200:
            pull_curve = decay_model_numpy(np.array([seconds]), self.jgh_TTT_pull_curve_coefficient, self.jgh_TTT_pull_curve_exponent)
            t = (seconds - 900) / 300.0 # Linear transition from max(...) at 900s to one_hour_curve[0] at 1200s
            start_val = max(pull_curve[0], one_hour_curve[0])
            end_val = one_hour_curve[0]
            answer = (1 - t) * start_val + t * end_val
        else: 
            answer = one_hour_curve[0]

        return answer

    def get_when_curvefit_done(self) -> str:
        return self.jgh_when_curves_fitted




