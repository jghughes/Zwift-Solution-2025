from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Dict, List, Any, Union
from jgh_read_write import *
from jgh_serialization import *
from jgh_sanitise_string import sanitise_string

class ZwiftPowerGraphInformationDTO(BaseModel):
    """
    A data transfer object representing a Zwift Power Graph JSON object.
    """

    class InfoItemDTO(BaseModel):
        """
        Represents a line-item in the 'info' list. A nested class.
        """
        name      : Optional[str]         = ""    # Name of the item
        effort_id : Optional[Union[str, int]] = ""    # Effort ID (string or integer)
        hide      : Optional[bool]        = False # Whether to hide the item

    class EffortItemDTO(BaseModel):
        """
        Represents a line-item in the lists that are the values of the three
        keys in the 'efforts' dictionary. A nested class.
        """
        x    : Optional[int] = 0    # X-coordinate
        y    : Optional[int] = 0    # Y-coordinate
        date : Optional[int] = 0    # Date as a Unix timestamp
        zid  : Optional[str] = ""   # Zwift ID

    info                          : Optional[Union[List[InfoItemDTO], Any]] = Field(default_factory=list)  # List of InfoItemDTO
    efforts                       : Optional[Union[Dict[str, List[EffortItemDTO]], Any]] = Field(default_factory=dict)  # Efforts dictionary
    events                        : Optional[Union[Dict[str, Any], Any]] = Field(default_factory=dict)  # Events dictionary
    zwiftpower_watts_last_updated : Optional[str] = ""  # Last updated timestamp for ZwiftPower watts


class ZwiftPower90DayBestGraphDTO(BaseModel):
    """
    A data transfer object representing a Zwift rider's critical power data - derived from the data recorded on ZwiftPower.
    """
    zwiftid : Optional[str]  = ""   # Unique identifier for the rider
    name    : Optional[str]  = ""   # Rider's name (sanitize for emojis and special characters)
    cp_1    : Optional[float] = 0.0
    cp_2    : Optional[float] = 0.0
    cp_3    : Optional[float] = 0.0
    cp_4    : Optional[float] = 0.0
    cp_5    : Optional[float] = 0.0
    cp_6    : Optional[float] = 0.0
    cp_7    : Optional[float] = 0.0
    cp_8    : Optional[float] = 0.0
    cp_9    : Optional[float] = 0.0
    cp_10   : Optional[float] = 0.0
    cp_11   : Optional[float] = 0.0
    cp_12   : Optional[float] = 0.0
    cp_13   : Optional[float] = 0.0
    cp_14   : Optional[float] = 0.0
    cp_15   : Optional[float] = 0.0
    cp_16   : Optional[float] = 0.0
    cp_17   : Optional[float] = 0.0
    cp_18   : Optional[float] = 0.0
    cp_19   : Optional[float] = 0.0
    cp_20   : Optional[float] = 0.0
    cp_21   : Optional[float] = 0.0
    cp_22   : Optional[float] = 0.0
    cp_23   : Optional[float] = 0.0
    cp_24   : Optional[float] = 0.0
    cp_25   : Optional[float] = 0.0
    cp_26   : Optional[float] = 0.0
    cp_27   : Optional[float] = 0.0
    cp_28   : Optional[float] = 0.0
    cp_29   : Optional[float] = 0.0
    cp_30   : Optional[float] = 0.0
    cp_35   : Optional[float] = 0.0
    cp_40   : Optional[float] = 0.0
    cp_45   : Optional[float] = 0.0
    cp_50   : Optional[float] = 0.0
    cp_55   : Optional[float] = 0.0
    cp_60   : Optional[float] = 0.0
    cp_70   : Optional[float] = 0.0
    cp_80   : Optional[float] = 0.0
    cp_90   : Optional[float] = 0.0
    cp_100  : Optional[float] = 0.0
    cp_110  : Optional[float] = 0.0
    cp_120  : Optional[float] = 0.0
    cp_150  : Optional[float] = 0.0
    cp_180  : Optional[float] = 0.0
    cp_210  : Optional[float] = 0.0
    cp_240  : Optional[float] = 0.0
    cp_270  : Optional[float] = 0.0
    cp_300  : Optional[float] = 0.0
    cp_330  : Optional[float] = 0.0
    cp_360  : Optional[float] = 0.0
    cp_390  : Optional[float] = 0.0
    cp_420  : Optional[float] = 0.0
    cp_450  : Optional[float] = 0.0
    cp_480  : Optional[float] = 0.0
    cp_510  : Optional[float] = 0.0
    cp_540  : Optional[float] = 0.0
    cp_570  : Optional[float] = 0.0
    cp_600  : Optional[float] = 0.0
    cp_660  : Optional[float] = 0.0
    cp_720  : Optional[float] = 0.0
    cp_780  : Optional[float] = 0.0
    cp_840  : Optional[float] = 0.0
    cp_900  : Optional[float] = 0.0
    cp_960  : Optional[float] = 0.0
    cp_1020 : Optional[float] = 0.0
    cp_1080 : Optional[float] = 0.0
    cp_1140 : Optional[float] = 0.0
    cp_1200 : Optional[float] = 0.0
    cp_1320 : Optional[float] = 0.0
    cp_1440 : Optional[float] = 0.0
    cp_1560 : Optional[float] = 0.0
    cp_1680 : Optional[float] = 0.0
    cp_1800 : Optional[float] = 0.0
    cp_1920 : Optional[float] = 0.0
    cp_2040 : Optional[float] = 0.0
    cp_2160 : Optional[float] = 0.0
    cp_2280 : Optional[float] = 0.0
    cp_2400 : Optional[float] = 0.0
    cp_2520 : Optional[float] = 0.0
    cp_2640 : Optional[float] = 0.0
    cp_2760 : Optional[float] = 0.0
    cp_2880 : Optional[float] = 0.0
    cp_3000 : Optional[float] = 0.0
    cp_3120 : Optional[float] = 0.0
    cp_3240 : Optional[float] = 0.0
    cp_3360 : Optional[float] = 0.0
    cp_3480 : Optional[float] = 0.0
    cp_3600 : Optional[float] = 0.0
    cp_3900 : Optional[float] = 0.0
    cp_4200 : Optional[float] = 0.0
    cp_4500 : Optional[float] = 0.0
    cp_4800 : Optional[float] = 0.0
    cp_5100 : Optional[float] = 0.0
    cp_5400 : Optional[float] = 0.0
    cp_5700 : Optional[float] = 0.0
    cp_6000 : Optional[float] = 0.0
    cp_6300 : Optional[float] = 0.0
    cp_6600 : Optional[float] = 0.0
    cp_7200 : Optional[float] = 0.0

    # Validator for zwiftID to convert incoming int to str
    @field_validator("zwiftid", mode="before")
    def validate_zwiftID(cls, value):
        if value is None:
            return ""
        return str(value)

    # Validator for all string fields
    @field_validator("name", mode="before")
    def sanitize_string_fields(cls, value):
        if value is None:
            return ""
        return sanitise_string(value)