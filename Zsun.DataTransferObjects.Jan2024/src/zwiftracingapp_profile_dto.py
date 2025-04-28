from pydantic import BaseModel, field_validator, AliasChoices, ConfigDict, AliasGenerator, Field
from typing import Optional, Union, Any, Dict

validation_alias_choices_map: dict[str, AliasChoices] = {
    "age_group"               : AliasChoices("age_group", "age"),
    "fullname"               : AliasChoices("fullname", "name"),
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
        w5:      Optional[int] = 0
        w15:     Optional[int] = 0
        w30:     Optional[int] = 0
        w60:     Optional[int] = 0
        w120:    Optional[int] = 0
        w300:    Optional[int] = 0
        w1200:   Optional[int] = 0
        CP:      Optional[float] = 0.0  # Critical Power
        AWC:     Optional[float] = 0.0  # Anaerobic Work Capacity
        compoundScore: Optional[float] = 0.0  # Compound score
        powerRating: Optional[float] = 0.0  # Power rating

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

        rating: Optional[float] = 0  # Race rating
        date: Optional[int] = 0      # Date as a Unix timestamp
        mixed: Optional[Union[MixedDTO, Any]] = Field(default_factory=MixedDTO)

    model_config = preferred_config_dict
    riderId:    Optional[str]   = ""   # Rider ID
    fullname:       Optional[str]   = ""   # Name of the rider
    gender:     Optional[str]   = ""   # Gender of the rider
    country:    Optional[str]   = ""   # Country of the rider
    age_group:  Optional[str]   = ""   # Age category of the rider
    height:     Optional[int] = 0  # Height of the rider in centimeters
    weight:     Optional[int] = 0  # Weight of the rider in kilograms
    zpCategory: Optional[str]  = ""   # ZwiftPower category, such as C or D
    zpFTP:      Optional[int] = 0  # ZwiftPower FTP (Functional Threshold Power)
    power:      Optional[Union[PowerDTO, Any]] = Field(default_factory=PowerDTO)  # Power data of the rider
    race:       Optional[Union[Dict[str, RaceDetailsDTO], Any]] = Field(default_factory=lambda: {
            "last": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
            "current": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
            "max30": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
            "max90": ZwiftRacingAppProfileDTO.RaceDetailsDTO()}
    )

    #  # Validator for numeric fields
    # @field_validator("height", "weight", "zpFTP", mode="before")
    # def validate_numeric_fields(cls, value):
    #     if value in {"--", "---", None}:
    #         return None
    #     try:
    #         if "." in str(value):
    #             return float(value)
    #         return int(value)
    #     except (ValueError, TypeError):
    #         raise ValueError(f"Invalid value for numeric field: {value}")
