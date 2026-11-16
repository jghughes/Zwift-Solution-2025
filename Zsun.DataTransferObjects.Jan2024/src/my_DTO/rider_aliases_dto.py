from typing import Any, cast

from pydantic import AliasChoices, AliasGenerator, BaseModel, ConfigDict, RootModel, field_validator

validation_alias_choices_map: dict[str, AliasChoices] = {
    "row": AliasChoices("row"),
    "zwift_id": AliasChoices("zwift_id", "zwiftId"),
    "alias_rider_stats_item": AliasChoices("alias_rider_stats_item", "full_name"),
    "alias_rider_compute_item": AliasChoices("alias_rider_compute_item", "name_racingapp"),
    "zwift_country_code3": AliasChoices("zwift_country_code3", "zwiftCountryCode3"),
    "alias_zwift_first_name": AliasChoices("alias_zwift_first_name", "firstName"),
    "alias_zwift_last_name": AliasChoices("alias_zwift_last_name", "lastName"),
    "alias_zwiftpower": AliasChoices("alias_zwiftpower", "name"),
    "alias_zwiftracing_app": AliasChoices("alias_zwiftracing_app", "name"),
}

configdictV1 = ConfigDict(
    alias_generator=AliasGenerator(
        alias=None, validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)
    )
)

preferred_config_dict = configdictV1


class RiderAliasesDTO(BaseModel):
    model_config = preferred_config_dict
    row: int = 0
    zwift_id: str = ""
    alias_rider_stats_item: str = ""
    alias_rider_compute_item: str = ""
    zwift_country_code3: str = ""
    alias_zwift_first_name: str = ""
    alias_zwift_last_name: str = ""
    alias_zwiftpower: str = ""
    alias_zwiftracing_app: str = ""

    # Validator for zwift_id to convert int to string
    @field_validator("zwift_id", mode="before")
    def convert_int_to_str(cls, value: Any) -> str:
        if isinstance(value, int):
            return str(value)
        return cast(str, value)


class RiderAliasesDtoDictModel(RootModel[dict[str, RiderAliasesDTO]]):
    pass


class RiderAliasesDtoListModel(RootModel[list[RiderAliasesDTO]]):
    pass
