# Local application imports
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional
from jgh_read_write import *
from jgh_serialization import *

# Define constants for all the serialization aliases
ZWIFTID_ALIAS = "zwiftid"
NAME_ALIAS = "name"
CP_5_SEC_ALIAS = "cp_5_sec"
CP_15_SEC_ALIAS = "cp_15_sec"
CP_30_SEC_ALIAS = "cp_30_sec"
CP_1_MIN_ALIAS = "cp_1_min"
CP_2_MIN_ALIAS = "cp_2_min"
CP_90_SEC_ALIAS = "cp_90_sec"
CP_3_MIN_ALIAS = "cp_3_min"
CP_5_MIN_ALIAS = "cp_5_min"
CP_7_MIN_ALIAS = "cp_7_min"
CP_10_MIN_ALIAS = "cp_10_min"
CP_12_MIN_ALIAS = "cp_12_min"
CP_15_MIN_ALIAS = "cp_15_min"
CP_20_MIN_ALIAS = "cp_20_min"
CP_30_MIN_ALIAS = "cp_30_min"
CP_40_MIN_ALIAS = "cp_40_min"
CP_50_MIN_ALIAS = "cp_50_min"
CP_1_HOUR_ALIAS = "cp_1_hour"
CP_75_MIN_ALIAS = "cp_75_min"
CP_90_MIN_ALIAS = "cp_90_min"
CP_2_HOUR_ALIAS = "cp_2_hour"
CP_3_HOUR_ALIAS = "cp_3_hour"
CP_4_HOUR_ALIAS = "cp_4_hour"
CP_ALIAS            = "cp"
AWC_ALIAS       = "awc"
INVERSE_CONST_ALIAS = "inverse_const"
INVERSE_EXP_ALIAS   = "inverse_exp"
PREFERRED_MODEL_ALIAS = "preferred_model"

# Define the serialization alias map
serialization_alias_map: dict[str, str] = {
    "zwiftid": ZWIFTID_ALIAS,
    "name": NAME_ALIAS,
    "cp_5_sec": CP_5_SEC_ALIAS,
    "cp_15_sec": CP_15_SEC_ALIAS,
    "cp_30_sec": CP_30_SEC_ALIAS,
    "cp_1_min": CP_1_MIN_ALIAS,
    "cp_2_min": CP_2_MIN_ALIAS,
    "cp_90_sec": CP_90_SEC_ALIAS,
    "cp_3_min": CP_3_MIN_ALIAS,
    "cp_5_min": CP_5_MIN_ALIAS,
    "cp_7_min": CP_7_MIN_ALIAS,
    "cp_10_min": CP_10_MIN_ALIAS,
    "cp_12_min": CP_12_MIN_ALIAS,
    "cp_15_min": CP_15_MIN_ALIAS,
    "cp_20_min": CP_20_MIN_ALIAS,
    "cp_30_min": CP_30_MIN_ALIAS,
    "cp_40_min": CP_40_MIN_ALIAS,
    "cp_50_min": CP_50_MIN_ALIAS,
    "cp_1_hour": CP_1_HOUR_ALIAS,
    "cp_75_min": CP_75_MIN_ALIAS,
    "cp_90_min": CP_90_MIN_ALIAS,
    "cp_2_hour": CP_2_HOUR_ALIAS,
    "cp_3_hour": CP_3_HOUR_ALIAS,
    "cp_4_hour": CP_4_HOUR_ALIAS,
    "cp": CP_ALIAS,
    "awc": AWC_ALIAS,
    "inverse_const": INVERSE_CONST_ALIAS,
    "inverse_exp": INVERSE_EXP_ALIAS,
    "preferred_model": PREFERRED_MODEL_ALIAS
}

# Define the validation alias choices map
validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwiftid": AliasChoices("zwiftid"),
    "name": AliasChoices("name"),
    "cp_5_sec": AliasChoices("cp_5_sec"),
    "cp_15_sec": AliasChoices("cp_15_sec"),
    "cp_30_sec": AliasChoices("cp_30_sec"),
    "cp_1_min": AliasChoices("cp_1_min"),
    "cp_2_min": AliasChoices("cp_2_min"),
    "cp_90_sec": AliasChoices("cp_90_sec"),
    "cp_3_min": AliasChoices("cp_3_min"),
    "cp_5_min": AliasChoices("cp_5_min"),
    "cp_7_min": AliasChoices("cp_7_min"),
    "cp_10_min": AliasChoices("cp_10_min"),
    "cp_12_min": AliasChoices("cp_12_min"),
    "cp_15_min": AliasChoices("cp_15_min"),
    "cp_20_min": AliasChoices("cp_20_min"),
    "cp_30_min": AliasChoices("cp_30_min"),
    "cp_40_min": AliasChoices("cp_40_min"),
    "cp_50_min": AliasChoices("cp_50_min"),
    "cp_1_hour": AliasChoices("cp_1_hour"),
    "cp_75_min": AliasChoices("cp_75_min"),
    "cp_90_min": AliasChoices("cp_90_min"),
    "cp_2_hour": AliasChoices("cp_2_hour"),
    "cp_3_hour": AliasChoices("cp_3_hour"),
    "cp_4_hour": AliasChoices("cp_4_hour"),
    "cp": AliasChoices("cp"),
    "awc": AliasChoices("awc"),
    "inverse_const": AliasChoices("inverse_const"),
    "inverse_exp": AliasChoices("inverse_exp"),
    "preferred_model": AliasChoices("preferred_model"),
}

# Define the Pydantic ConfigDict
configdictV1 = ConfigDict(
    alias_generator=AliasGenerator(
        alias=None,
        serialization_alias=lambda field_name: serialization_alias_map.get(field_name, field_name),
        validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name),
    )
)

preferred_config_dict = configdictV1


class ZwiftRiderCriticalPowerDTO(BaseModel):
    """
    A data transfer object representing a zwiftrider's critical power data.
    """
    zwiftid: Optional[int] = 0  # Zwift ID of the rider
    name: Optional[str] = ""  # Name of the rider
    cp_5_sec: Optional[float] = 0.0  # Critical power for 5 seconds
    cp_15_sec: Optional[float] = 0.0  # Critical power for 15 seconds
    cp_30_sec: Optional[float] = 0.0  # Critical power for 30 seconds
    cp_1_min: Optional[float] = 0.0  # Critical power for 1 minute
    cp_2_min: Optional[float] = 0.0  # Critical power for 2 minutes
    cp_90_sec: Optional[float] = 0.0  # Critical power for 90 seconds
    cp_3_min: Optional[float] = 0.0  # Critical power for 3 minutes
    cp_5_min: Optional[float] = 0.0  # Critical power for 5 minutes
    cp_7_min: Optional[float] = 0.0  # Critical power for 7 minutes
    cp_10_min: Optional[float] = 0.0  # Critical power for 10 minutes
    cp_12_min: Optional[float] = 0.0  # Critical power for 12 minutes
    cp_15_min: Optional[float] = 0.0  # Critical power for 15 minutes
    cp_20_min: Optional[float] = 0.0  # Critical power for 20 minutes
    cp_30_min: Optional[float] = 0.0  # Critical power for 30 minutes
    cp_40_min: Optional[float] = 0.0  # Critical power for 40 minutes
    cp_50_min: Optional[float] = 0.0  # Critical power for 50 minutes
    cp_1_hour: Optional[float] = 0.0  # Critical power for 1 hour
    cp_75_min: Optional[float] = 0.0  # Critical power for 75 minutes
    cp_90_min: Optional[float] = 0.0  # Critical power for 90 minutes
    cp_2_hour: Optional[float] = 0.0  # Critical power for 2 hours
    cp_3_hour: Optional[float] = 0.0  # Critical power for 3 hours
    cp_4_hour: Optional[float] = 0.0  # Critical power for 4 hours
    cp: Optional[float] = 0.0  # Critical power
    awc: Optional[float] = 0.0  # W' (work capacity above critical power)
    inverse_const: Optional[float] = 0.0  # Inverse model constant
    inverse_exp: Optional[float] = 0.0  # Inverse model exponent
    preferred_model: Optional[str] = "" # Inverse Exponential model "inverse", or Critical Power Model "cp"

    model_config = preferred_config_dict
