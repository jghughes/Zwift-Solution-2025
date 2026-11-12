from types import UnionType
from typing import Any, Union, cast, get_args, get_origin

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field, field_validator

from jgh_string import sanitise_string


def _is_optional_float_annotation(field_type: Any) -> bool:
    origin: object = get_origin(field_type)
    return origin in (Union, UnionType) and float in get_args(field_type) and type(None) in get_args(field_type)


validation_alias_choices_map_ZwiftRacingAppDTO: dict[str, AliasChoices] = {
    "zwift_id": AliasChoices("zwift_id", "riderId"),
    "full_name": AliasChoices("full_name", "name"),
    "gender_code": AliasChoices("gender_code", "gender"),
    "country_code2": AliasChoices("country_code2", "country"),
    "age_group": AliasChoices("age_group", "age"),
    "height_cm": AliasChoices("height_cm", "height"),
    "weight_kg": AliasChoices("weight_kg", "weight"),
    "zp_race_category": AliasChoices("zp_race_category", "zpCategory"),
    "zp_FTP": AliasChoices("zp_FTP", "zpFTP"),
    "power_obj": AliasChoices("power_obj", "power"),
    "race_obj": AliasChoices("race_obj", "race"),
    "velo_obj": AliasChoices("velo_obj", "velo"),
    "timestamp": AliasChoices("timestamp", "timestamp"),
    "status": AliasChoices("status", "status"),
}
validation_alias_choices_map_PowerDTO: dict[str, AliasChoices] = {
    "wkg_5s": AliasChoices("wkg_5s", "wkg5"),
    "wkg_15s": AliasChoices("wkg_15s", "wkg15"),
    "wkg_30s": AliasChoices("wkg_30s", "wkg30"),
    "wkg_60s": AliasChoices("wkg_60s", "wkg60"),
    "wkg_120s": AliasChoices("wkg_120s", "wkg120"),
    "wkg_300s": AliasChoices("wkg_300s", "wkg300"),
    "wkg_1200s": AliasChoices("wkg_1200s", "wkg1200"),
    "w_5s": AliasChoices("w_5s", "w5"),
    "w_15s": AliasChoices("w_15s", "w15"),
    "w_30s": AliasChoices("w_30s", "w30"),
    "w_60s": AliasChoices("w_60s", "w60"),
    "w_120s": AliasChoices("w_120s", "w120"),
    "w_300s": AliasChoices("w_300s", "w300"),
    "w_1200s": AliasChoices("w_1200s", "w1200"),
    "w_CP": AliasChoices("w_CP", "CP"),
    "kJ_AWC": AliasChoices("kJ_AWC", "AWC"),
}
validation_alias_choices_map_RaceDTO: dict[str, AliasChoices] = {
    "racing_score_max30_obj": AliasChoices("racing_score_max30_obj", "max30"),
    "racing_score_max90_obj": AliasChoices("racing_score_max90_obj", "max90"),
}
validation_alias_choices_map_RatingScoreDTO: dict[str, AliasChoices] = {
    "velo_rating": AliasChoices("velo_rating", "rating"),
    "mixed_things_obj": AliasChoices("mixed_things_obj", "mixed", "open"),
}
validation_alias_choices_map_MixedDTO: dict[str, AliasChoices] = {
    "velo_cat_name": AliasChoices("velo_cat_name", "category", "name"),
    "velo_cat_num": AliasChoices("velo_cat_num", "number"),
}

# Combine all alias maps into one consolidated map
validation_alias_choices_map_consolidated: dict[str, AliasChoices] = {
    **validation_alias_choices_map_ZwiftRacingAppDTO,
    **validation_alias_choices_map_PowerDTO,
    **validation_alias_choices_map_RaceDTO,
    **validation_alias_choices_map_RatingScoreDTO,
    **validation_alias_choices_map_MixedDTO,
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            validation_alias=lambda field_name: validation_alias_choices_map_consolidated.get(field_name, field_name)))

preferred_config_dict = configdictV1

class MixedThingsDTO(BaseModel):
    model_config  = preferred_config_dict
    velo_cat_name: str | None = ""
    velo_cat_num: int | None = 0

class RatingScoreDTO(BaseModel):
    model_config  = preferred_config_dict
    velo_rating         : float | None           = 0.0 
    mixed_things_obj    : MixedThingsDTO | None  = Field(default_factory=MixedThingsDTO)

class RaceDTO(BaseModel):
    model_config  = preferred_config_dict
    racing_score_max30_obj    : RatingScoreDTO | None = Field(default_factory=RatingScoreDTO)
    racing_score_max90_obj    : RatingScoreDTO | None = Field(default_factory=RatingScoreDTO)

class PowerDTO(BaseModel):
    model_config  = preferred_config_dict
    wkg_5s          : float | None = 0.0
    wkg_15s         : float | None = 0.0
    wkg_30s         : float | None = 0.0
    wkg_60s         : float | None = 0.0
    wkg_120s        : float | None = 0.0
    wkg_300s        : float | None = 0.0
    wkg_1200s       : float | None = 0.0
    w_5s            : float | None = 0.0
    w_15s           : float | None = 0.0
    w_30s           : float | None = 0.0
    w_60s           : float | None = 0.0
    w_120s          : float | None = 0.0
    w_300s          : float | None = 0.0
    w_1200s         : float | None = 0.0
    w_CP            : float | None = 0.0  # Critical Power
    kJ_AWC           : float | None = 0.0  # Anaerobic Work Capacity

    @field_validator(
        *[
            field
            for field, field_type in __annotations__.items()
            if _is_optional_float_annotation(field_type)
        ],
    )
    def validate_float_fields(cls, value : Any) -> float | None:
        if value is None:
            return None
        try:
            # Check if the value is numeric and can be cast to a float
            return float(value)
        except (ValueError, TypeError):
            # Return None for non-float values
            return None

class ZwiftRacingAppDTO(BaseModel):
	model_config			=	preferred_config_dict
	zwift_id				:	str					=	""		# Zwift ID of the rider
	full_name				:	str | None		=	""		# Name of the rider
	gender_code				:	str | None		=	""		# Gender of the rider "M" or "F"
	country_code2			:	str | None		=	""		# Country of the rider
	age_group				:	str | None		=	""		# Age category of the rider eg 50+
	height_cm				:	float | None		=	0.0		# Height of the rider in centimeters
	weight_kg				:	float | None		=	0.0		# Weight of the rider in kilograms
	zp_race_category		:	str | None		=	""		# ZwiftPower category, such as C or D
	zp_FTP					:	float | None		=	0.0		# ZwiftPower FTP (Functional Threshold Power)
	power_obj				:	PowerDTO | None	=	Field(default_factory=PowerDTO)		# Power data of the rider
	race_obj				:	RaceDTO | None	=	Field(default_factory=RaceDTO)		# Race data of the rider
	velo_obj				:	RaceDTO | None	=	Field(default_factory=RaceDTO)		# Velo2 data of the rider
	timestamp				:	str | None		=	""		# Date when the Zwift Racing App was last_name updated

	# Validator for zwift_id to convert int to string
	@field_validator("zwift_id", mode="before")
	def convert_int_to_str(cls, value : Any) -> str:
		if isinstance(value, int):
			return str(value)
		return cast(str, value)

	# Validator for string fields - get rid of
	@field_validator("full_name", mode="before")
	def sanitise_string_field(cls, value : Any) -> str:
		if value is None:
			return ""
		return sanitise_string(value)