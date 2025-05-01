
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, field_validator
from typing import Optional, Union, get_origin, get_args
from jgh_sanitise_string import sanitise_string

validation_alias_choices_map: dict[str, AliasChoices] = {
    "age_group"               : AliasChoices("age_group", "age"),
    "zwift_racing_category"   : AliasChoices("zwift_racing_category", "category"),
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1

class ZwiftPowerProfileDTO(BaseModel):
    model_config             = preferred_config_dict
    zwift_id                 : Optional[str] = "" 
    profile_url              : Optional[str] = ""
    zwift_name               : Optional[str] = ""
    race_ranking             : Optional[str] = "" # wraps a float
    zwift_racing_score       : Optional[str] = "" # wraps an int
    zwift_racing_category    : Optional[str] = ""
    team                     : Optional[str] = ""
    zftp                     : Optional[str] = "" # wraps an int
    weight                   : Optional[str] = "" # wraps a float
    age_group                : Optional[str] = ""
    zpoints                  : Optional[str] = "" # wraps an int
    country                  : Optional[str] = ""
    profile_image            : Optional[str] = ""
    strava_profile           : Optional[str] = ""
    level                    : Optional[str] = "" # wraps an int

    @field_validator(
        *[
            field
            for field, field_type in __annotations__.items()
            if get_origin(field_type) is Union and str in get_args(field_type) and type(None) in get_args(field_type)
        ],
        mode="before"
    )
    def sanitise_string_fields(cls, value):
        if value is None:
            return ""
        return sanitise_string(value)

