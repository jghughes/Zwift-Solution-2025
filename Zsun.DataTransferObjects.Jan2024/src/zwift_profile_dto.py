from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, Field, field_validator
from typing import Optional, Union, get_origin, get_args
from jgh_sanitise_string import sanitise_string

validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwiftID"               : AliasChoices("zwiftID", "id"),
    "age_years"               : AliasChoices("age_years", "age"),
    "height_mm"               : AliasChoices("height_mm","height"),
    "weight_grams"               : AliasChoices("weight_grams","weight"),
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1


class ZwiftProfileDTO(BaseModel):
    """
    A data transfer object representing a Zwift profile JSON object.
    Only a subset of the fields is used, as the full profile contains many more attributes.
    """

    class CompetitionMetricsDTO(BaseModel):
        """
        A nested DTO for the competition metrics of a Zwift profile.

        Attributes:
            racingScore (float): The racing score of the rider.
            category (str): The racing category of the rider.
            categoryWomen (str): The racing category for women.
        """
        racingScore   : Optional[float] = 0.0
        category      : Optional[str]  = ""
        categoryWomen : Optional[str]  = ""

    model_config = preferred_config_dict
    zwiftID             : Optional[str]                      = ""   # Unique identifier for the profile
    publicId            : Optional[str]                      = ""   # Public ID of the profile
    firstName           : Optional[str]                      = ""   # First name of the rider
    lastName            : Optional[str]                      = ""   # Last name of the rider
    male                : Optional[bool]                     = True # Gender of the rider (True for male, False for female)
    age_years           : Optional[float]                    = 0    # Age of the rider
    height_mm           : Optional[float]                    = 0    # Height in millimeters
    weight_grams        : Optional[float]                    = 0    # Weight in grams
    ftp                 : Optional[float]                    = 0    # Functional Threshold Power (FTP) in watts (I don't know if this is the same as their zFTP)
    competitionMetrics  : Optional[CompetitionMetricsDTO]    = Field(default_factory=CompetitionMetricsDTO)

    @field_validator(
        *[
            field
            for field, field_type in __annotations__.items()
            if get_origin(field_type) is Union and float in get_args(field_type) and type(None) in get_args(field_type)
        ],
    )
    def validate_float_fields(cls, value):
        if value is None:
            return None
        try:
            # Check if the value is numeric and can be cast to a float
            return float(value)
        except (ValueError, TypeError):
            # Return None for non-float values
            return None

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
