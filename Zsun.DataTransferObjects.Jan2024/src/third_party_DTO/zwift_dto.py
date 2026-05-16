from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, Field, field_validator
from typing import Optional, Any
from jgh_string import sanitise_string


validation_alias_choices_map_ZwiftDTO: dict[str, AliasChoices] = {
	"zwift_id"					:	AliasChoices("zwift_id", "id"),
	"first_name"				:	AliasChoices("first_name", "firstName"),
	"last_name"					:	AliasChoices("last_name", "lastName"),
	"country_code3"				:	AliasChoices("country_code3", "countryAlpha3"),
	"is_male"					:	AliasChoices("is_male", "male"),
	"age_years"					:	AliasChoices("age_years", "age"),
	"height_mm"					:	AliasChoices("height_mm", "height"),
	"weight_grams"				:	AliasChoices("weight_grams", "weight"),
	"ftp_on_zwift"				:	AliasChoices("ftp_on_zwift", "ftp"),
	"achievement_level"			:	AliasChoices("achievement_level", "achievementLevel"),
	"total_distance_meters"		:	AliasChoices("total_distance_meters", "totalDistance"),
	"total_experience_points"	:	AliasChoices("total_experience_points", "totalExperiencePoints"),
	"target_experience_points"	:	AliasChoices("target_experience_points", "targetExperiencePoints"),
	"competition_metrics"		:	AliasChoices("competition_metrics", "competitionMetrics"),
}

validation_alias_choices_map_CompetitionMetricsDTO: dict[str, AliasChoices] = {
	"zwift_racing_score"		:	AliasChoices("zwift_racing_score", "racingScore"),
	"zwift_category_open"		:	AliasChoices("zwift_category_open", "category"),
	"zwift_category_women"		:	AliasChoices("zwift_category_women", "categoryWomen"),
}

validation_alias_choices_map_consolidated: dict[str, AliasChoices] = {
    **validation_alias_choices_map_ZwiftDTO,
    **validation_alias_choices_map_CompetitionMetricsDTO,
}


configdictV1 = ConfigDict(alias_generator=AliasGenerator(
    alias=None,
    validation_alias=lambda field_name: validation_alias_choices_map_consolidated.get(field_name, field_name)))

preferred_config_dict = configdictV1

class CompetitionMetricsDTO(BaseModel):
	model_config = preferred_config_dict
	zwift_racing_score		: Optional[float]	= 0.0
	zwift_category_open		: Optional[str]		= ""
	zwift_category_women	: Optional[str]		= ""

class ZwiftDTO(BaseModel):
	model_config	=	preferred_config_dict
	zwift_id					:	str								=	""	# Zwift ID of the rider
	first_name					:	Optional[str]					=	""	# First name of the rider
	last_name					:	Optional[str]					=	""	# Last name of the rider
	country_code3				:	Optional[str]					=	""	# eg USA, GBR, AUS
	is_male						:	Optional[bool]					=	True	# Gender of the rider (True for male, False for female)
	age_years					:	Optional[float]					=	0	# Age of the rider
	height_mm					:	Optional[float]					=	0	# Height in millimeters
	weight_grams				:	Optional[float]					=	0	# Weight in grams
	ftp_on_zwift				:	Optional[float]					=	0	# This is not zFTP, it is FTP
	achievement_level			:	Optional[int]					=	0	# Zwift achievement level. Note: what we think of as level 100, has two extra places in the Zwift json i.e. 100 == 10_000. so will need to divide by 100 and round down eventually to get the level we are familiar with.
	total_distance_meters		:	Optional[float]					=	0	# Total distance ridden in meters
	total_experience_points		:	int								=	0
	target_experience_points	:	int								=	0	# Experience points needed to reach the accelerated achievement level
	competition_metrics			:	Optional[CompetitionMetricsDTO]	=	Field(default_factory=CompetitionMetricsDTO)

	# Validator for zwift_id to convert int to string
	@field_validator("zwift_id", mode="before")
	def convert_int_to_str(cls, value : Any):
		if isinstance(value, int):
			return str(value)
		return value

	# Validator for string fields - get rid of emojis and other unwanted characters
	@field_validator("first_name", "last_name", mode="before")
	def sanitise_string_field(cls, value: Any):
		if value is None:
			return ""
		return sanitise_string(value)