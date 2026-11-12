from typing import Any, cast

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, Field, field_validator

validation_alias_choices_map_ZwiftPowerGraphWattsDTO: dict[str, AliasChoices] = {
    "zwift_id": AliasChoices("zwift_id", "zwift_id"),
    "efforts_obj": AliasChoices("efforts_obj", "efforts"),
}

validation_alias_choices_map_EffortDTO: dict[str, AliasChoices] = {
    "x_ordinate_seconds": AliasChoices("x_ordinate_seconds", "x"),
    "y_ordinate_watts": AliasChoices("y_ordinate_watts", "y"),
}

validation_alias_choices_map_consolidated: dict[str, AliasChoices] = {
    **validation_alias_choices_map_EffortDTO,
    **validation_alias_choices_map_ZwiftPowerGraphWattsDTO,
}

configdictV1 = ConfigDict(
    alias_generator=AliasGenerator(
        alias=None,
        validation_alias=lambda field_name: validation_alias_choices_map_consolidated.get(field_name, field_name),
    )
)

preferred_config_dict = configdictV1


class EffortDTO(BaseModel):
    model_config = preferred_config_dict
    x_ordinate_seconds: int = 0
    y_ordinate_watts: int = 0


class ZwiftPowerGraphWattsDTO(BaseModel):
    model_config = preferred_config_dict
    zwift_id: str = ""
    efforts_obj: dict[str, list[EffortDTO]] | None = Field(
        default_factory=dict[str, list[EffortDTO]]
    )  # Efforts dictionary

    # Validator for zwift_id to convert int to string
    @field_validator("zwift_id", mode="before")
    def convert_int_to_str(cls, value: Any) -> str:
        if isinstance(value, int):
            return str(value)
        return cast(str, value)
