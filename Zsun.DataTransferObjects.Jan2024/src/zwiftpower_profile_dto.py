
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, field_validator
from typing import Optional
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


    # Validator for string fields - get rid of emojis and other unwanted characters
    @field_validator("zwift_name", mode="before")
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

    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"

    file_paths = help_select_filepaths_in_folder(None,".json", ZWIFTPOWER_PROFILES_DIRPATH)
    logger.info(f"Found {len(file_paths)} files in {ZWIFTPOWER_PROFILES_DIRPATH}")
    file_count = 0
    error_count = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        logger.info(f"Processing file: {file_name}")
        inputjson = read_filepath_as_text(file_path)
        file_count += 1
        try:
            dto = JghSerialization.validate(inputjson, ZwiftPowerProfileDTO)
            dto = cast(ZwiftPowerProfileDTO, dto)
        except Exception as e:
            error_count += 1
            logger.error(f"{error_count} serialization error in file: {file_name}.\nException: {e}\n")
            logger.error(f"{error_count} serialisation error. Skipping file: {file_name}")
            continue
    
    logger.info(f"Successfully processed {file_count} files")
    logger.info(f"Encountered {error_count} errors during processing")

if __name__ == "__main__":
    main()



