from typing import List, Dict, Any
from pydantic import BaseModel, RootModel
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, field_validator

validation_alias_choices_map: dict[str, AliasChoices] = {
	"row"									:	AliasChoices("row"),
	"zwift_id"								:	AliasChoices("zwift_id", "zwiftId"),
	"full_name"								:	AliasChoices("full_name", "fullName"),
	"zwift_country_code3"					:	AliasChoices("zwift_country_code3", "zwiftCountryCode3"),
	"age_years"								:	AliasChoices("age_years", "ageYears"),
	"height_cm"								:	AliasChoices("height_cm", "heightcm"),
	"weight_kg"								:	AliasChoices("weight_kg", "weightkg"),
	"gender_code"							:	AliasChoices("gender_code", "genderCode"),
	"cat_open"								:	AliasChoices("cat_open", "catOpen"),
	"cat_women"								:	AliasChoices("cat_women", "catWomen"),
	"level"									:	AliasChoices("level", "level"),
	"total_distance_km"						:	AliasChoices("total_distance_km", "totalDistanceKm"),
	"total_experience_points"				:	AliasChoices("total_experience_points", "totalExperiencePoints"),
	"target_experience_points"				:	AliasChoices("target_experience_points", "targetExperiencePoints"),
	"projected_accelerated_level"			:	AliasChoices("projected_accelerated_level", "projectedAcceleratedLevel"),
	"zwift_racing_score"					:	AliasChoices("zwift_racing_score", "zwiftRacingScore"),
	"zwift_ftp_w"							:	AliasChoices("zwift_ftp_w", "zwiftWattsFTP"),
	"zwift_zftp_w"							:	AliasChoices("zwift_zftp_w", "zwiftWattsZFTP"),
	"zwift_zftp_wkg"						:	AliasChoices("zwift_zftp_wkg", "zwiftWattsKgZFTP"),
	"velo_age_group"						:	AliasChoices("velo_age_group", "veloAgeGroup"),
	"velo_cat_num_30_days"					:	AliasChoices("velo_cat_num_30_days", "veloCatNum30Days"),
	"velo_cat_name_30_days"					:	AliasChoices("velo_cat_name_30_days", "veloCatName30Days"),
	"velo_rating_30_days"					:	AliasChoices("velo_rating_30_days", "veloRating30Days"),
	"wkg_05sec"								:	AliasChoices("wkg_05sec", "wkg05sec"),
	"wkg_15sec"								:	AliasChoices("wkg_15sec", "wkg15sec"),
	"wkg_30sec"								:	AliasChoices("wkg_30sec", "wkg30sec"),
	"wkg_01min"								:	AliasChoices("wkg_01min", "wkg01min"),
	"wkg_02min"								:	AliasChoices("wkg_02min", "wkg02min"),
	"wkg_03min"								:	AliasChoices("wkg_03min", "wkg03min"),
	"wkg_05min"								:	AliasChoices("wkg_05min", "wkg05min"),
	"wkg_10min"								:	AliasChoices("wkg_10min", "wkg10min"),
	"wkg_12min"								:	AliasChoices("wkg_12min", "wkg12min"),
	"wkg_15min"								:	AliasChoices("wkg_15min", "wkg15min"),
	"wkg_20min"								:	AliasChoices("wkg_20min", "wkg20min"),
	"wkg_30min"								:	AliasChoices("wkg_30min", "wkg30min"),
	"wkg_40min"								:	AliasChoices("wkg_40min", "wkg40min"),
	"wkg_60min_curvefit"					:	AliasChoices("wkg_60min_curvefit", "wkg60minCurvefit"),
	"w_05sec"								:	AliasChoices("w_05sec", "w05sec"),
	"w_15sec"								:	AliasChoices("w_15sec", "w15sec"),
	"w_30sec"								:	AliasChoices("w_30sec", "w30sec"),
	"w_01min"								:	AliasChoices("w_01min", "w01min"),
	"w_02min"								:	AliasChoices("w_02min", "w02min"),
	"w_03min"								:	AliasChoices("w_03min", "w03min"),
	"w_05min"								:	AliasChoices("w_05min", "w05min"),
	"w_10min"								:	AliasChoices("w_10min", "w10min"),
	"w_12min"								:	AliasChoices("w_12min", "w12min"),
	"w_15min"								:	AliasChoices("w_15min", "w15min"),
	"w_20min"								:	AliasChoices("w_20min", "w20min"),
	"w_30min"								:	AliasChoices("w_30min", "w30min"),
	"w_40min"								:	AliasChoices("w_40min", "w40min"),
	"w_60min_curvefit"						:	AliasChoices("w_60min_curvefit", "w60minCurvefit"),
	"frontal_area_m2"						:	AliasChoices("frontal_area_m2", "frontalAreaM2"),
	"single_segment_distance_km"			:	AliasChoices("single_segment_distance_km", "predictionDistanceKm"),
	"single_segment_watts"					:	AliasChoices("single_segment_watts", "predictionWatts"),
	"single_segment_wgk"					:	AliasChoices("single_segment_wgk", "predictionWkg"),
	"single_segment_duration_sec"			:	AliasChoices("single_segment_duration_sec", "predictionDurationSec"),
	"single_segment_duration_hh_mm_ss"		:	AliasChoices("single_segment_duration_hh_mm_ss", "predictionDurationHhMmSs"),
	"route_name"							:	AliasChoices("route_name", "routeName"),
	"route_zwift_world_name"				:	AliasChoices("route_zwift_world_name", "routeZwiftWorldName"),
	"route_description"						:	AliasChoices("route_description", "routeDescription"),
	"route_length_km"						:	AliasChoices("route_length_km", "routeLengthKm"),
	"route_elevation_m"						:	AliasChoices("route_elevation_m", "routeElevationM"),
	"route_lead_in_length_km"				:	AliasChoices("route_lead_in_length_km", "routeLeadInLengthKm"),
	"route_imposed_intensity_factor"		:	AliasChoices("route_imposed_intensity_factor", "routeImposedIntensityFactor"),
	"route_fastest_achievable_time_sec"		:	AliasChoices("route_fastest_achievable_time_sec", "routeFastestAchievableTimeSecs"),
	"route_fastest_achievable_time_hh_mm_ss":	AliasChoices("route_fastest_achievable_time_hh_mm_ss", "routeFastestAchievableTimeHhMmSs"),
	"route_power_output_watts"				:	AliasChoices("route_power_output_watts", "routePowerOutputWatts"),
	"route_power_output_wkg"				:	AliasChoices("route_power_output_wkg", "routePowerOutputWkg"),
	"timestamp"								:	AliasChoices("timestamp", "timestamp"),
}

configdictV1 = ConfigDict(alias_generator=AliasGenerator(
    alias=None,
    validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1


class RiderStatsDTO(BaseModel):
	model_config							=	preferred_config_dict
	row                                     :	int		=	0
	zwift_id								:	str		=	""
	full_name								:	str		=	""
	zwift_country_code3						:	str		=	""
	age_years								:	float	=	0.0
	height_cm								:	float	=	0.0
	weight_kg								:	float	=	0.0
	gender_code								:	str		=	""
	cat_open								:	str		=	""
	cat_women								:	str		=	""
	level									:	int		=	0
	total_distance_km						:	float	=	0.0
	total_experience_points					:	int		=	0
	target_experience_points				:	int		=	0
	projected_accelerated_level				:	int		=	0
	zwift_racing_score						:	float	=	0.0
	zwift_ftp_w								:	float	=	0.0
	zwift_zftp_w							:	float	=	0.0
	zwift_zftp_wkg							:	float	=	0.0
	zwift_cat_label							:	str		=	""
	velo_age_group							:	str		=	""
	velo_cat_num_30_days					:	int		=	0
	velo_cat_name_30_days					:	str		=	""
	velo_rating_30_days						:	float	=	0.0
	velo_cat_label							:	str		=	""
	wkg_05sec								:	float	=	0.0
	wkg_15sec								:	float	=	0.0
	wkg_30sec								:	float	=	0.0
	wkg_01min								:	float	=	0.0
	wkg_02min								:	float	=	0.0
	wkg_03min								:	float	=	0.0
	wkg_05min								:	float	=	0.0
	wkg_10min								:	float	=	0.0
	wkg_12min								:	float	=	0.0
	wkg_15min								:	float	=	0.0
	wkg_20min								:	float	=	0.0
	wkg_30min								:	float	=	0.0
	wkg_40min								:	float	=	0.0
	wkg_60min_curvefit						:	float	=	0.0
	w_05sec									:	float	=	0.0
	w_15sec									:	float	=	0.0
	w_30sec									:	float	=	0.0
	w_01min									:	float	=	0.0
	w_02min									:	float	=	0.0
	w_03min									:	float	=	0.0
	w_05min									:	float	=	0.0
	w_10min									:	float	=	0.0
	w_12min									:	float	=	0.0
	w_15min									:	float	=	0.0
	w_20min									:	float	=	0.0
	w_30min									:	float	=	0.0
	w_40min									:	float	=	0.0
	w_60min_curvefit						:	float	=	0.0
	frontal_area_m2							:	float	=	0.0
	single_segment_distance_km				:	float	=	0.0 # Distance in km for which the single_segment_duration_sec and single_segment_duration_hh_mm_ss are calculated
	single_segment_watts					:	float	=	0.0 # Predicted watts for the specified distance
	single_segment_wgk						:	float	=	0.0 # Predicted watts per kg for the specified distance
	single_segment_duration_sec				: 	float	=	0.0 # Predicted duration for a distance in km (specified in constants.py) in seconds
	single_segment_duration_hh_mm_ss		: 	str		=	"" # Predicted duration for a distance in km (specified in constants.py), must be in format HH:mm:ss
	route_name								: str = ""
	route_zwift_world_name					: str = ""
	route_description						: str = ""
	route_length_km							: float = 0.0
	route_elevation_m						: float = 0.0
	route_lead_in_length_km					: float = 0.0
	route_imposed_intensity_factor			: float = 0.0
	route_fastest_achievable_time_sec		: float = 0.0
	route_fastest_achievable_time_hh_mm_ss	: str = ""
	route_power_output_watts				: float = 0.0
	route_power_output_wkg					: float = 0.0
	timestamp								: str =	""
	# Validator for zwift_id to convert int to string
	@field_validator("zwift_id", mode="before")
	def convert_int_to_str(cls, value : Any):
		if isinstance(value, int):
			return str(value)
		return value

class RiderStatsDtoDictModel(RootModel[Dict[str, RiderStatsDTO]]):
    pass

class RiderStatsDtoListModel(RootModel[List[RiderStatsDTO]]):
    pass