from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Any


class ZwiftRacingAppPostDTO(BaseModel):
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
        w5:      Optional[float] = 0.0
        w15:     Optional[float] = 0.0
        w30:     Optional[float] = 0.0
        w60:     Optional[float] = 0.0
        w120:    Optional[float] = 0.0
        w300:    Optional[float] = 0.0
        w1200:   Optional[float] = 0.0
        CP:      Optional[float] = 0.0  # Critical Power
        AWC:     Optional[float] = 0.0  # Anaerobic Work Capacity

    model_config = ConfigDict(
        alias_generator=None,      # No alias generator for this DTO
        populate_by_name=True      # Allow population by field names
    )
    riderId:    Optional[str]   = ""   # Rider ID
    name:       Optional[str]   = ""   # Name of the rider
    gender:     Optional[str]   = ""   # Gender of the rider
    country:    Optional[str]   = ""   # Country of the rider
    age:        Optional[str]   = ""   # Age category of the rider
    height:     Optional[float] = 0.0  # Height of the rider in centimeters
    weight:     Optional[float] = 0.0  # Weight of the rider in kilograms
    zpCategory: Optional[str]   = ""   # ZwiftPower category
    zpFTP:      Optional[float] = 0.0  # ZwiftPower FTP (Functional Threshold Power)
    power:      Optional[Union[PowerDTO, Any]] = Field(default_factory=PowerDTO)  # Power data of the rider



