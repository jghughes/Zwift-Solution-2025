from dataclasses import dataclass
from zwift_id_base import ZwiftIdBase
from regression_modelling_dto import RegressionModellingDTO

@dataclass
class RegressionModellingItem(ZwiftIdBase):
    name							: str	= ""	# Name of the rider
    gender							: str	= ""	# Gender of the rider
    weight_kg						: float	= 0.0
    height_cm						: float	= 0.0
    age_years						: float	= 0.0	# Age of the rider in years
    zwift_racing_score				: float	= 0.0	# Zwift racing score
    zwift_cat_open					: str	= ""	# A+, A, B, C, D, E
    zwift_ftp_watts					: float	= 0.0
    jgh_60_min_watts				: float	= 0.0
    jgh_40_minute_watts			    : float	= 0.0
    velo_zpftp_watts			    : float	= 0.0
    velo_rating_30_days		        : float	= 0.0	# Velo score typically over 1000
    velo_cat_num_30_days		    : int	= 0		# Velo rating 1 to 10
    velo_cat_name_30_days		    : str	= ""	# Copper, Silver, Gold etc
    bp_5							: float	= 0.0
    bp_15							: float	= 0.0
    bp_30							: float	= 0.0
    bp_60							: float	= 0.0
    bp_180							: float	= 0.0
    bp_300							: float	= 0.0
    bp_600							: float	= 0.0
    bp_720							: float	= 0.0
    bp_900							: float	= 0.0
    bp_1200							: float	= 0.0
    bp_1800							: float	= 0.0
    bp_2400							: float	= 0.0
    jgh_60_min_curve_coefficient	: float	= 0.0
    jgh_60_min_curve_exponent		: float	= 0.0

    @staticmethod
    def from_dataTransferObject(dto: RegressionModellingDTO) -> "RegressionModellingItem":
        return RegressionModellingItem(
            zwift_id						= dto.zwift_id or "",
            name							= dto.name or "",
            gender							= dto.gender or "",
            weight_kg						= dto.weight_kg or 0.0,
            height_cm						= dto.height_cm or 0.0,
            age_years						= dto.age_years or 0.0,
            zwift_racing_score				= dto.zwift_racing_score or 0.0,
            zwift_cat_open					= dto.zwift_cat_open or "",
            zwift_ftp_watts					= dto.zwift_ftp_watts or 0.0,
            jgh_60_min_watts				= dto.jgh_60_min_watts or 0.0,
            jgh_40_minute_watts			    = dto.jgh_40_minute_watts or 0.0,
            velo_zpftp_watts			    = dto.velo_zpftp_watts or 0.0,
            velo_rating_30_days		        = dto.velo_rating_30_days or 0.0,
            velo_cat_num_30_days		    = dto.velo_cat_num_30_days or 0,
            velo_cat_name_30_days		    = dto.velo_cat_name_30_days or "",
            bp_5							= dto.bp_5 or 0.0,
            bp_15							= dto.bp_15 or 0.0,
            bp_30							= dto.bp_30 or 0.0,
            bp_60							= dto.bp_60 or 0.0,
            bp_180							= dto.bp_180 or 0.0,
            bp_300							= dto.bp_300 or 0.0,
            bp_600							= dto.bp_600 or 0.0,
            bp_720							= dto.bp_720 or 0.0,
            bp_900							= dto.bp_900 or 0.0,
            bp_1200							= dto.bp_1200 or 0.0,
            bp_1800							= dto.bp_1800 or 0.0,
            bp_2400							= dto.bp_2400 or 0.0,
            jgh_60_min_curve_coefficient	= dto.jgh_60_min_curve_coefficient or 0.0,
            jgh_60_min_curve_exponent		= dto.jgh_60_min_curve_exponent or 0.0        
            )

    @staticmethod
    def to_dataTransferObject(item: "RegressionModellingItem") -> RegressionModellingDTO:
        return RegressionModellingDTO(
            zwift_id							= item.zwift_id,
            name								= item.name,
            gender								= item.gender,
            weight_kg							= item.weight_kg,
            height_cm							= item.height_cm,
            age_years							= item.age_years,
            zwift_racing_score					= item.zwift_racing_score,
            zwift_cat_open						= item.zwift_cat_open,
            zwift_ftp_watts						= item.zwift_ftp_watts,
            jgh_60_min_watts					= item.jgh_60_min_watts,
            jgh_40_minute_watts				    = item.jgh_40_minute_watts,
            velo_zpftp_watts				    = item.velo_zpftp_watts,
            velo_rating_30_days			        = item.velo_rating_30_days,
            velo_cat_num_30_days			    = item.velo_cat_num_30_days,
            velo_cat_name_30_days			    = item.velo_cat_name_30_days,
            bp_5								= item.bp_5,
            bp_15								= item.bp_15,
            bp_30								= item.bp_30,
            bp_60								= item.bp_60,
            bp_180								= item.bp_180,
            bp_300								= item.bp_300,
            bp_600								= item.bp_600,
            bp_720								= item.bp_720,
            bp_900								= item.bp_900,
            bp_1200								= item.bp_1200,
            bp_1800								= item.bp_1800,
            bp_2400								= item.bp_2400,
            jgh_60_min_curve_coefficient		= item.jgh_60_min_curve_coefficient,
            jgh_60_min_curve_exponent			= item.jgh_60_min_curve_exponent                    
        )
