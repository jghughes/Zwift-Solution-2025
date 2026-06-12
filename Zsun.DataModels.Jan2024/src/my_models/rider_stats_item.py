
from dataclasses import dataclass

from jgh_formulae00 import calculate_frontal_area
from zwift_id_base import ZwiftIdBase
from typing import Optional
from rider_stats_dto import RiderStatsDTO

# this domain model is instantiated in model_constructors.py

@dataclass
class RiderStatsItem(ZwiftIdBase):
	name						:	str		=	""
	zwift_country_code3			:	str		=	""
	age							:	float	=	0.0
	height_cm					:	float	=	0.0
	weight_kg					:	float	=	0.0
	gender_code					:	str		=	""
	cat_open					:	str		=	""
	cat_women					:	str		=	""
	achievement_level			:	int		=	0
	total_distance_km           :	float	=	0.0
	total_experience_points		:	int		=	0
	rider_score					:	int		=	0
	projected_accelerated_level:	int		=	0
	zwift_racing_score			:	float	=	0.0
	zwift_ftp_w					:	float	=	0.0
	zwift_zftp_w				:	float	=	0.0
	zwift_zftp_wkg				:	float	=	0.0
	zwift_cat_label				:	str		=	""
	velo_age_group				:	str		=	""
	velo_cat_num_30_days		:	int		=	0
	velo_cat_name_30_days		:	str		=	""
	velo_rating_30_days			:	float	=	0.0
	velo_cat_label				:	str		=	""
	wkg_05sec					:	float	=	0.0
	wkg_15sec					:	float	=	0.0
	wkg_30sec					:	float	=	0.0
	wkg_01min					:	float	=	0.0
	wkg_02min					:	float	=	0.0
	wkg_03min					:	float	=	0.0
	wkg_05min					:	float	=	0.0
	wkg_10min					:	float	=	0.0
	wkg_12min					:	float	=	0.0
	wkg_15min					:	float	=	0.0
	wkg_20min					:	float	=	0.0
	wkg_30min					:	float	=	0.0
	wkg_40min					:	float	=	0.0
	wkg_60min_curvefit			:	float	=	0.0
	w_05sec						:	float	=	0.0
	w_15sec						:	float	=	0.0
	w_30sec						:	float	=	0.0
	w_01min						:	float	=	0.0
	w_02min						:	float	=	0.0
	w_03min						:	float	=	0.0
	w_05min						:	float	=	0.0
	w_10min						:	float	=	0.0
	w_12min						:	float	=	0.0
	w_15min						:	float	=	0.0
	w_20min						:	float	=	0.0
	w_30min						:	float	=	0.0
	w_40min						:	float	=	0.0
	w_60min_curvefit			:	float	=	0.0
	# frontal_area_m2				:	float	=	0.0
	# single_segment_duration_sec			: float	=	0.0 # Predicted duration for a distance in km (specified in constants.py) in seconds
	# single_segment_watts				: float =	0.0 # Predicted watts for the specified distance
	# single_segment_wgk					: float =	0.0 # Predicted watts per kg for the specified distance
	# single_segment_duration_hh_mm_ss	: str	=	"" # Predicted duration for a distance in km (specified in constants.py), must be in format HH:mm:ss
	# single_segment_distance_km			: float =	0.0 # Distance in km for which the single_segment_duration_sec and single_segment_duration_hh_mm_ss are calculated
	route_name								: str = ""
	route_zwift_world_name					: str = ""
	route_description						: str = ""
	route_length_km							: float = 0.0
	route_elevation_m						: float = 0.0
	route_lead_in_length_km					: float = 0.0
	route_imposed_intensity_factor			: float = 0.0
	route_fastest_achievable_time_sec		: float = 0.0
	route_fastest_achievable_time_hh_mm_ss	: str = ""
	route_power_output_watts				: float = 0
	route_power_output_wkg				: float = 0.0
	timestamp					:	str		=	"" # Timestamp indicating when the models were fitted, must be ISO 8601 format YYYY-MM-DDTHH:mm:ss.sssZ

	@staticmethod
	def to_dataTransferObject(item: Optional["RiderStatsItem"]) -> RiderStatsDTO:
		if item is None:
			return RiderStatsDTO()
		return RiderStatsDTO(
			zwift_id					= item.zwift_id,
			full_name					= item.name,
			zwift_country_code3			= item.zwift_country_code3,
			age_years					= item.age,
			height_cm					= item.height_cm,
			weight_kg					= item.weight_kg,
			gender_code					= item.gender_code,
			cat_open					= item.cat_open,
			cat_women					= item.cat_women,
			level						= item.achievement_level,
			total_distance_km           = item.total_distance_km,
			total_experience_points		= item.total_experience_points,
			target_experience_points	= item.rider_score,
			projected_accelerated_level	= item.projected_accelerated_level,
			zwift_racing_score			= item.zwift_racing_score,
			zwift_ftp_w					= int(item.zwift_ftp_w),
			zwift_zftp_w				= int(item.zwift_zftp_w),
			zwift_zftp_wkg				= round(item.zwift_zftp_wkg, 2),
			zwift_cat_label				= item.zwift_cat_label,
			velo_age_group				= item.velo_age_group,
			velo_cat_num_30_days		= item.velo_cat_num_30_days,
			velo_cat_name_30_days		= item.velo_cat_name_30_days,
			velo_rating_30_days			= item.velo_rating_30_days,
			velo_cat_label				= item.velo_cat_label,
			wkg_05sec					= round(item.wkg_05sec, 2),
			wkg_15sec					= round(item.wkg_15sec, 2),
			wkg_30sec					= round(item.wkg_30sec, 2),
			wkg_01min					= round(item.wkg_01min, 2),
			wkg_02min					= round(item.wkg_02min, 2),
			wkg_03min					= round(item.wkg_03min, 2),
			wkg_05min					= round(item.wkg_05min, 2),
			wkg_10min					= round(item.wkg_10min, 2),
			wkg_12min					= round(item.wkg_12min, 2),
			wkg_15min					= round(item.wkg_15min, 2),
			wkg_20min					= round(item.wkg_20min, 2),
			wkg_30min					= round(item.wkg_30min, 2),
			wkg_40min					= round(item.wkg_40min, 2),
			wkg_60min_curvefit			= round(item.wkg_60min_curvefit, 2),
			w_05sec						= int(item.w_05sec),
			w_15sec						= int(item.w_15sec),
			w_30sec						= int(item.w_30sec),
			w_01min						= int(item.w_01min),
			w_02min						= int(item.w_02min),
			w_03min						= int(item.w_03min),
			w_05min						= int(item.w_05min),
			w_10min						= int(item.w_10min),
			w_12min						= int(item.w_12min),
			w_15min						= int(item.w_15min),
			w_20min						= int(item.w_20min),
			w_30min						= int(item.w_30min),
			w_40min						= int(item.w_40min),
			w_60min_curvefit			= int(item.w_60min_curvefit),
			route_name								= item.route_name,
			route_zwift_world_name					= item.route_zwift_world_name,
			route_description						= item.route_description,
			route_length_km							= item.route_length_km,
			route_elevation_m						= item.route_elevation_m,
			route_lead_in_length_km					= item.route_lead_in_length_km,
			route_imposed_intensity_factor			= item.route_imposed_intensity_factor,
			route_fastest_achievable_time_sec		= item.route_fastest_achievable_time_sec,
			route_fastest_achievable_time_hh_mm_ss	= item.route_fastest_achievable_time_hh_mm_ss,
			route_power_output_watts				= item.route_power_output_watts,
			route_power_output_wkg					= item.route_power_output_wkg,
			timestamp					= item.timestamp,
		)

	@staticmethod
	def from_dataTransferObject(dto: Optional[RiderStatsDTO]) -> "RiderStatsItem":
		if dto is None:
			return RiderStatsItem()
		item = RiderStatsItem()
		item.zwift_id					= dto.zwift_id
		item.name						= dto.full_name
		item.zwift_country_code3		= dto.zwift_country_code3
		item.age						= dto.age_years
		item.height_cm					= dto.height_cm
		item.weight_kg					= dto.weight_kg
		item.gender_code				= dto.gender_code
		item.cat_open					= dto.cat_open
		item.cat_women					= dto.cat_women
		item.achievement_level			= dto.level
		item.total_experience_points    = dto.total_experience_points
		item.rider_score                = dto.target_experience_points
		item.projected_accelerated_level= dto.projected_accelerated_level
		item.zwift_racing_score			= dto.zwift_racing_score
		item.zwift_ftp_w				= dto.zwift_ftp_w
		item.zwift_zftp_w				= dto.zwift_zftp_w
		item.zwift_zftp_wkg				= dto.zwift_zftp_wkg
		item.zwift_cat_label			= dto.zwift_cat_label
		item.velo_age_group				= dto.velo_age_group
		item.velo_cat_num_30_days		= dto.velo_cat_num_30_days
		item.velo_cat_name_30_days		= dto.velo_cat_name_30_days
		item.velo_rating_30_days		= dto.velo_rating_30_days
		item.velo_cat_label				= dto.velo_cat_label
		item.wkg_05sec					= dto.wkg_05sec
		item.wkg_15sec					= dto.wkg_15sec
		item.wkg_30sec					= dto.wkg_30sec
		item.wkg_01min					= dto.wkg_01min
		item.wkg_02min					= dto.wkg_02min
		item.wkg_03min					= dto.wkg_03min
		item.wkg_05min					= dto.wkg_05min
		item.wkg_10min					= dto.wkg_10min
		item.wkg_12min					= dto.wkg_12min
		item.wkg_15min					= dto.wkg_15min
		item.wkg_20min					= dto.wkg_20min
		item.wkg_30min					= dto.wkg_30min
		item.wkg_40min					= dto.wkg_40min
		item.wkg_60min_curvefit			= dto.wkg_60min_curvefit
		item.w_05sec					= dto.w_05sec
		item.w_15sec					= dto.w_15sec
		item.w_30sec					= dto.w_30sec
		item.w_01min					= dto.w_01min
		item.w_02min					= dto.w_02min
		item.w_03min					= dto.w_03min
		item.w_05min					= dto.w_05min
		item.w_10min					= dto.w_10min
		item.w_12min					= dto.w_12min
		item.w_15min					= dto.w_15min
		item.w_20min					= dto.w_20min
		item.w_30min					= dto.w_30min
		item.w_40min					= dto.w_40min
		item.w_60min_curvefit			= dto.w_60min_curvefit
		item.route_name								= dto.route_name
		item.route_zwift_world_name					= dto.route_zwift_world_name
		item.route_description						= dto.route_description
		item.route_length_km						= dto.route_length_km
		item.route_elevation_m						= dto.route_elevation_m
		item.route_lead_in_length_km				= dto.route_lead_in_length_km
		item.route_imposed_intensity_factor			= dto.route_imposed_intensity_factor
		item.route_fastest_achievable_time_sec		= dto.route_fastest_achievable_time_sec
		item.route_fastest_achievable_time_hh_mm_ss	= dto.route_fastest_achievable_time_hh_mm_ss
		item.route_power_output_watts				= dto.route_power_output_watts
		item.route_power_output_wkg					= dto.route_power_output_wkg
		item.timestamp					= dto.timestamp
		return item

