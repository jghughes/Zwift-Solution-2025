from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, field_validator
from typing import Optional, Any

validation_alias_choices_map: dict[str, AliasChoices] = {
	"person_id"				:	AliasChoices("person_id", "zwift_id"),
	"nickname"				:	AliasChoices("nickname", "zwift_name"),
	"team_name"				:	AliasChoices("team_name", "team"),
	"zftp_from_somewhere"	:	AliasChoices("zftp_from_somewhere", "zftp"),
	"age_bracket"			:	AliasChoices("age_bracket", "age"),
}

configdictV1 = ConfigDict(
	alias_generator=AliasGenerator(
		alias=None,
		validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name))
)

preferred_config_dict = configdictV1

class ZwiftPowerProfileDTO(BaseModel):
	model_config				=	preferred_config_dict
	person_id					:	str				=	""		# Zwift ID of the rider
	nickname						:	Optional[str]	=	""		# usually a moniker, whatever is in the HUD from time to time
	team_name					:	Optional[str]	=	""		# Team name
	zftp_from_somewhere			:	Optional[str]	=	""		# wraps an int
	age_bracket					:	Optional[str]	=	""		# Age bracket

	@field_validator("zftp_from_somewhere", mode="before")
	def sanitise_wrapped_numerics(cls, value : Any):
		if value is None:
			return "0"
		try:
			# Attempt to cast the value to a float
			float(value)
			# If the cast succeeds, return the string unchanged
			return value
		except ValueError:
			# If the cast fails, return "0"
			return "0"