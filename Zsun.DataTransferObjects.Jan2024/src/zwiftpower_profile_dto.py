
from pydantic import BaseModel, field_validator, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional

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
    model_config = preferred_config_dict
    zwift_id: Optional[str] = None
    profile_url: Optional[str] = None
    zwift_name: Optional[str] = None
    race_ranking: Optional[str] = None
    zwift_racing_score: Optional[str] = None
    zwift_racing_category: Optional[str] = None
    team: Optional[str] = None
    zftp: Optional[str] = None
    weight: Optional[str] = None
    age_group: Optional[str] = None
    zpoints: Optional[str] = None
    country: Optional[str] = None
    profile_image: Optional[str] = None
    strava_profile: Optional[str] = None
    level: Optional[str] = None

   # Combined validator for numeric fields
    @field_validator("zwift_id", "race_ranking", "zwift_racing_score", "zftp", "weight","zpoints", "level", mode="before")
    def validate_numeric_fields(cls, value):
        if value in {"--", "---", None}:
            return None
        try:
            # Convert valid numeric strings to float or int and back to string
            if "." in value:
                return str(float(value))  # Handle float values
            return str(int(value))  # Handle integer values
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value for numeric field: {value} in JSON element representing Zwift_id : {cls.zwift_id}")

    # # Validator to sanitize string fields by removing invalid characters, reducing spaces, and stripping
    # @field_validator("zwift_name", "profile_url", "team", "country", "profile_image", "strava_profile", mode="before")
    # def sanitize_string_fields(cls, value):
    #     if value is None:
    #         return value
    #     try:
    #         # Encode to UTF-8 and decode back, ignoring invalid characters
    #         sanitized_value = value.encode("utf-8", errors="ignore").decode("utf-8")
    #         # Reduce multiple spaces to a single space
    #         sanitized_value = re.sub(r'\s+', ' ', sanitized_value)
    #         # Strip leading and trailing spaces
    #         return sanitized_value.strip()
    #     except Exception as e:
    #         raise ValueError(f"Error sanitizing string field: {value}. Error: {e}")