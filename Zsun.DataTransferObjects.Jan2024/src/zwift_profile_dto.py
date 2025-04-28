from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, Field
from typing import Optional


validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwiftID"               : AliasChoices("zwiftID", "id"),
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
    zwiftID           : Optional[int]    = 0   # Unique identifier for the profile
    publicId          : Optional[str]    = ""  # Public ID of the profile
    firstName         : Optional[str]    = ""  # First name of the rider
    lastName          : Optional[str]    = ""  # Last name of the rider
    male              : Optional[bool]   = True  # Gender of the rider (True for male, False for female)
    age               : Optional[int]    = 0   # Age of the rider
    height            : Optional[int]    = 0   # Height in millimeters
    weight            : Optional[int]    = 0   # Weight in grams
    ftp               : Optional[int]    = 0   # Functional Threshold Power (FTP) in watts (I don't know if this is the same as their zFTP)
    competitionMetrics : Optional[CompetitionMetricsDTO] = Field(default_factory=CompetitionMetricsDTO)