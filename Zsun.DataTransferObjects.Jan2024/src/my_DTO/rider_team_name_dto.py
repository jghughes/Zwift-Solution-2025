from typing import Any, cast

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, RootModel, field_validator

validation_alias_choices_map: dict[str, AliasChoices] = {
	"row"				:	AliasChoices("row"),
	"zwift_id"			:	AliasChoices("zwift_id", "zwiftId"),
	"full_rider_name"	:	AliasChoices("full_rider_name", "rider"),
	"team_name"			:	AliasChoices("team_name", "team"),
}

configdictV1 = ConfigDict(alias_generator=AliasGenerator(
    alias=None,
    validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1


class RiderTeamNameDTO(BaseModel):
	model_config = preferred_config_dict
	row						:	int		=	0
	zwift_id				:	str		=	""
	full_rider_name			:	str		=	""
	team_name				:	str		=	""
	# Validator for zwift_id to convert int to string
	@field_validator("zwift_id", mode="before")
	def convert_int_to_str(cls, value : Any) -> str:
		if isinstance(value, int):
			return str(value)
		return cast(str, value)

class RiderTeamNameDtoDictModel(RootModel[dict[str, RiderTeamNameDTO]]):
    pass

class RiderTeamNameDtoListModel(RootModel[list[RiderTeamNameDTO]]):
    pass