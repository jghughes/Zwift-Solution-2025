from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, Field, field_validator
from typing import Optional
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

    # Validator for numeric fields
    @field_validator("age_years", "height_mm", "weight_grams", "ftp", mode="before")
    def validate_numeric_fields(cls, value):
        if value is None:
            return None
        try:
            # Check if the value is numeric
            return float(value)
        except (ValueError, TypeError):
            # Return None for non-numeric values
            return None

    # Validator for zwiftID to convert int to str
    @field_validator("zwiftID", mode="before")
    def validate_zwiftID(cls, value):
        if value is None:
            return ""
        return str(value)

    # Validator for boolean fields
    @field_validator("male", mode="before")
    def validate_boolean_fields(cls, value):
        if value is None:
            return False  # Default to False if the value is None
        if isinstance(value, bool):
            return value  # Return the value if it's already a boolean
        if isinstance(value, str):
            # Convert common string representations of booleans
            if value.lower() in {"true", "1", "yes"}:
                return True
            if value.lower() in {"false", "0", "no"}:
                return False
        raise ValueError(f"Invalid value for boolean field: {value}")


    # # Validator for all string fields
    @field_validator("publicId", "firstName", "lastName", mode="before")
    def sanitize_string_fields(cls, value):
        if value is None:
            return ""
        return sanitise_string(value)
