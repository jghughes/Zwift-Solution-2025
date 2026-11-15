from typing import Any, cast

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, RootModel, field_validator

validation_alias_choices_map: dict[str, AliasChoices] = {
    "row": AliasChoices("row"),
    "zwift_id": AliasChoices("zwift_id", "zwiftId"),
    "rider_name": AliasChoices("rider_name", "rider"),
    "team_name": AliasChoices("team_name", "team"),
}

configdictV1 = ConfigDict(
    alias_generator=AliasGenerator(
        alias=None, validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)
    )
)

preferred_config_dict = configdictV1


class TeamMemberDTO(BaseModel):
    model_config = preferred_config_dict
    row: int = 0
    zwift_id: str = ""
    rider_name: str = ""
    team_name: str = ""

    # Validator for zwift_id to convert int to string
    @field_validator("zwift_id", mode="before")
    def convert_int_to_str(cls, value: Any) -> str:
        if isinstance(value, int):
            return str(value)
        return cast(str, value)


class TeamMemberDtoDictModel(RootModel[dict[str, TeamMemberDTO]]):
    pass


class TeamMemberDtoListModel(RootModel[list[TeamMemberDTO]]):
    pass
