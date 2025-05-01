from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, Field, field_validator
from typing import Optional, Union, get_origin, get_args
from jgh_sanitise_string import sanitise_string

validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwift_id"               : AliasChoices("zwift_id", "id"),
    "public_id"               : AliasChoices("public_id", "publicId"),
    "first_name"             : AliasChoices("first_name", "firstName"),
    "last_name"              : AliasChoices("last_name", "lastName"),
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
    zwift_id            : Optional[str]                      = "" # Unique identifier for the profile
    public_id           : Optional[str]                      = ""   # Public ID of the profile
    first_name          : Optional[str]                      = ""   # First name of the rider
    last_name           : Optional[str]                      = ""   # Last name of the rider
    male                : Optional[bool]                     = True # Gender of the rider (True for male, False for female)
    age_years           : Optional[float]                    = 0    # Age of the rider
    height_mm           : Optional[float]                    = 0    # Height in millimeters
    weight_grams        : Optional[float]                    = 0    # Weight in grams
    ftp                 : Optional[float]                    = 0    # Functional Threshold Power (FTP) in watts (I don't know if this is the same as their zFTP)
    competitionMetrics  : Optional[CompetitionMetricsDTO]    = Field(default_factory=CompetitionMetricsDTO)

    # Validator for zwift_id to convert int to string
    @field_validator("zwift_id", mode="before")
    def convert_int_to_str(cls, value):
        if isinstance(value, int):
            return str(value)
        return value


    # Validator for float fields
    @field_validator("age_years", "height_mm", "weight_grams", "ftp", mode="before")
    def validate_float_fields(cls, value):
        if value is None:
            return None
        try:
            # Check if the value is numeric and can be cast to a float
            return float(value)
        except (ValueError, TypeError):
            # Return None for non-float values
            return None

    # Validator for string fields
    @field_validator("public_id", "first_name", "last_name", mode="before")
    def sanitise_string_fields(cls, value):
        if value is None:
            return ""
        return sanitise_string(value)


def main():

    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    import os
    from typing import cast
    from jgh_read_write import read_filepath_as_text, help_select_filepaths_in_folder
    from jgh_serialization import JghSerialization

    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"

    file_paths = help_select_filepaths_in_folder(None,".json", ZWIFT_PROFILES_DIRPATH)
    logger.info(f"Found {len(file_paths)} files in {ZWIFT_PROFILES_DIRPATH}")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftProfileDTO)
            dto = cast(ZwiftProfileDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue

if __name__ == "__main__":
    main()
