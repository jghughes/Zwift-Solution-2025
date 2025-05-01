from pydantic import BaseModel, field_validator, AliasChoices, ConfigDict, AliasGenerator, Field
from typing import Optional, Union, Any, Dict, get_origin, get_args
from jgh_sanitise_string import sanitise_string

validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwiftID"               : AliasChoices("zwiftID", "riderId"),
    "agegroup_title"               : AliasChoices("agegroup_title", "age"),
    "fullname"               : AliasChoices("fullname", "name"),
    "height_cm"               : AliasChoices("height_cm", "height"),
    "weight_kg"               : AliasChoices("weight_kg", "weight"),
    "zp_race_category"      : AliasChoices("zp_race_category", "zpCategory"),
    "zp_FTP"      : AliasChoices("zp_FTP", "zpFTP"),
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1

class ZwiftRacingAppProfileDTO(BaseModel):
    """
    A data transfer object representing a Zwift Racing App JSON object that contains
    post-processed data originating from ZwiftPower. This DTO ignores much of the
    information in the Zwift Racing App JSON object. It only includes power-related
    elements used for import by JGH.
    """

    class PowerDTO(BaseModel):
        """
        A nested model representing the power data of the rider.
        """
        wkg5:    Optional[float] = 0.0
        wkg15:   Optional[float] = 0.0
        wkg30:   Optional[float] = 0.0
        wkg60:   Optional[float] = 0.0
        wkg120:  Optional[float] = 0.0
        wkg300:  Optional[float] = 0.0
        wkg1200: Optional[float] = 0.0
        w5:      Optional[float] = 0
        w15:     Optional[float] = 0
        w30:     Optional[float] = 0
        w60:     Optional[float] = 0
        w120:    Optional[float] = 0
        w300:    Optional[float] = 0
        w1200:   Optional[float] = 0
        CP:      Optional[float] = 0.0  # Critical Power
        AWC:     Optional[float] = 0.0  # Anaerobic Work Capacity
        compoundScore: Optional[float] = 0.0  # Compound score
        powerRating: Optional[float] = 0.0  # Power rating

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


    class RaceDetailsDTO(BaseModel):
        """
        A data transfer object representing race details.

        Attributes:
            rating (float): The race rating (e.g., vELO rating).
            date (int): The date of the race as a Unix timestamp.
            mixed (MixedDTO): A nested object representing mixed category details.
        """

        class MixedDTO(BaseModel):
            """
            A nested model representing the velo race category details.

            Attributes:
                category (str): The name of the category (e.g., "Ruby").
                number (int): The number associated with the category.
            """
            category: Optional[str] = ""  # Name of the velo category, eg copper
            number: Optional[int] = 0    # Number associated with the velo category, eg 10

        rating  : Optional[float] = 0  # Race rating
        date    : Optional[int] = 0      # Date as a Unix timestamp
        mixed   : Optional[Union[MixedDTO, Any]] = Field(default_factory=MixedDTO)

    model_config  = preferred_config_dict
    zwiftID             : Optional[str]                      = ""   # Rider ID
    fullname            : Optional[str]                      = ""   # Name of the rider
    gender              : Optional[str]                      = ""   # Gender of the rider
    country             : Optional[str]                      = ""   # Country of the rider
    agegroup_title      : Optional[str]                      = ""   # Age category of the rider
    height_cm           : Optional[float]                    = 0    # Height of the rider in centimeters
    weight_kg           : Optional[float]                    = 0    # Weight of the rider in kilograms
    zp_race_category    : Optional[str]                      = ""   # ZwiftPower category, such as C or D
    zp_FTP              : Optional[float]                    = 0    # ZwiftPower FTP (Functional Threshold Power)
    power               : Optional[Union[PowerDTO, Any]]     = Field(default_factory=PowerDTO)  # Power data of the rider
    race                : Optional[Union[Dict[str, RaceDetailsDTO], Any]] = Field(default_factory=lambda: {
                                "last": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                                "current": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                                "max30": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                                "max90": ZwiftRacingAppProfileDTO.RaceDetailsDTO()})

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

