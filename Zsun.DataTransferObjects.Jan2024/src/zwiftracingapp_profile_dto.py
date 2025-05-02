from pydantic import BaseModel, field_validator, AliasChoices, ConfigDict, AliasGenerator, Field
from typing import Optional, Union, Any, Dict, get_origin, get_args
from jgh_sanitise_string import sanitise_string

validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwift_id"               : AliasChoices("zwift_id", "riderId"),
    "agegroup"               : AliasChoices("agegroup", "age"),
    "fullname"               : AliasChoices("fullname", "name"),
    "height_cm"              : AliasChoices("height_cm", "height"),
    "weight_kg"              : AliasChoices("weight_kg", "weight"),
    "zp_race_category"       : AliasChoices("zp_race_category", "zpCategory"),
    "zp_FTP"                 : AliasChoices("zp_FTP", "zpFTP"),
    "powerdto"               : AliasChoices("powerdto", "power"),
    "dict_of_racedetailsdto" : AliasChoices("dict_of_racedetailsdto", "race"),
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
    information in the Zwift Racing App JSON object. It only includes powerdto-related
    elements used for import by JGH.
    """

    class PowerDTO(BaseModel):
        """
        A nested model representing the powerdto data of the rider.
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
        A data transfer object representing dict_of_racedetailsdto details.

        Attributes:
            rating (float): The dict_of_racedetailsdto rating (e.g., vELO rating).
            date (int): The date of the dict_of_racedetailsdto as a Unix timestamp.
            mixed (MixedDTO): A nested object representing mixed category details.
        """

        class MixedDTO(BaseModel):
            """
            A nested model representing the velo dict_of_racedetailsdto category details.

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
    zwift_id            : Optional[str]                      = ""   # Rider ID
    fullname            : Optional[str]                      = ""   # Name of the rider
    gender              : Optional[str]                      = ""   # Gender of the rider "M" or "F"
    country             : Optional[str]                      = ""   # Country of the rider
    agegroup            : Optional[str]                      = ""   # Age category of the rider eg 50+
    height_cm           : Optional[float]                    = 0    # Height of the rider in centimeters
    weight_kg           : Optional[float]                    = 0    # Weight of the rider in kilograms
    zp_race_category    : Optional[str]                      = ""   # ZwiftPower category, such as C or D
    zp_FTP              : Optional[float]                    = 0    # ZwiftPower FTP (Functional Threshold Power)
    powerdto            : Optional[Union[PowerDTO, Any]]                     = Field(default_factory=PowerDTO)  # Power data of the rider
    dict_of_racedetailsdto : Optional[Union[Dict[str, RaceDetailsDTO], Any]] = Field(default_factory=lambda: {
                                "last": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                                "current": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                                "max30": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                                "max90": ZwiftRacingAppProfileDTO.RaceDetailsDTO()})


    # Validator for string fields - get rid of emojis and other unwanted characters
    @field_validator("fullname", mode="before")
    def sanitise_string_field(cls, value):
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

    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"

    file_paths = help_select_filepaths_in_folder(None,".json", ZWIFTRACINGAPP_PROFILES_DIRPATH)
    logger.info(f"Found {len(file_paths)} files in {ZWIFTRACINGAPP_PROFILES_DIRPATH}")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftRacingAppProfileDTO)
            dto = cast(ZwiftRacingAppProfileDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
    
    logger.info(f"Successfully processed {file_count} files")
    logger.info(f"Encountered {error_count} errors during processing")

if __name__ == "__main__":
    main()





