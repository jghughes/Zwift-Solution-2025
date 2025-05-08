# omnibus_profile_dto


from pydantic import BaseModel, field_validator, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional

validation_alias_choices_map: dict[str, AliasChoices] = {

    "zwift_id"               : AliasChoices("zwift_id", "riderId"),
    "age_group"               : AliasChoices("age_group", "age"),
    "zwift_racing_category"   : AliasChoices("zwift_racing_category", "category"),
    "zftp"   : AliasChoices("zftp", "zpFTP"),
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1

class OmnibusProfileDTO(BaseModel):
    model_config = preferred_config_dict

    # General attributes
    zwift_id                : Optional[str]  = None
    profile_url             : Optional[str]  = None
    zwift_name              : Optional[str]  = None
    race_ranking            : Optional[str]  = None
    zwift_racing_score      : Optional[str]  = None
    zwift_racing_category   : Optional[str]  = None
    team                    : Optional[str]  = None
    zftp                    : Optional[str]  = None
    weight                  : Optional[str]  = None
    age_group               : Optional[str]  = None
    zpoints                 : Optional[str]  = None
    country                 : Optional[str]  = None
    profile_image           : Optional[str]  = None
    strava_profile          : Optional[str]  = None
    level                   : Optional[str]  = None

    # Additional attributes
    gender                  : Optional[str]  = ""    # Gender of the rider
    country                 : Optional[str]  = ""    # Country of the rider
    age                     : Optional[str]  = ""    # Age category of the rider
    height                  : Optional[float] = 0.0  # Height of the rider in centimeters
    zpCategory              : Optional[str]  = ""    # ZwiftPower category
    zpFTP                   : Optional[float] = 0.0  # ZwiftPower FTP (Functional Threshold Power)
    velo_rating             : Optional[int]  = 0     # Velo rating

    # Power attributes
    wkg5                    : Optional[float] = 0.0
    wkg15                   : Optional[float] = 0.0
    wkg30                   : Optional[float] = 0.0
    wkg60                   : Optional[float] = 0.0
    wkg120                  : Optional[float] = 0.0
    wkg300                  : Optional[float] = 0.0
    wkg1200                 : Optional[float] = 0.0
    w5                      : Optional[float] = 0.0
    w15                     : Optional[float] = 0.0
    w30                     : Optional[float] = 0.0
    w60                     : Optional[float] = 0.0
    w120                    : Optional[float] = 0.0
    w300                    : Optional[float] = 0.0
    w1200                   : Optional[float] = 0.0
    CP                      : Optional[float] = 0.0  # Critical Power
    AWC                     : Optional[float] = 0.0  # Anaerobic Work Capacity

    # Curve and adjustment attributes
    pull_adjustment_watts   : Optional[float] = 0.0
    critical_power          : Optional[float] = 0.0
    critical_power_w_prime  : Optional[float] = 0.0
    one_hour_curve_coefficient   : Optional[float] = 0.0
    one_hour_curve_exponent      : Optional[float] = 0.0
    TTT_pull_curve_coefficient  : Optional[float] = 0.0
    TTT_pull_curve_exponent     : Optional[float] = 0.0
    when_curves_fitted      : Optional[str]   = ""
    functional_threshold_power : Optional[float] = 0.0

    # Combined validator for numeric fields
    @field_validator("zwift_id", "race_ranking", "zwift_racing_score", "zftp", "weight", "zpoints", "level", mode="before")
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
