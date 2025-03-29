from pydantic import BaseModel
from typing import Optional


class ZwiftRiderCriticalPowerCurveDataTransferObject(BaseModel):
    """
    A data transfer object representing a zwiftrider's critical power curve data.
    The object can be round-tripped to and from JSON. The values of all attributes
    are preserved in the JSON serialization and deserialization.

    This class derives from Pydantic's BaseModel, making it powerful for serialization
    and validation (deserialization).

    Attributes:
        zwiftid   : int    The Zwift ID of the rider.
        name      : str    The name of the rider.
        cpw_5_sec : float  Critical power for 5 seconds.
        cpw_15_sec: float  Critical power for 15 seconds.
        cpw_30_sec: float  Critical power for 30 seconds.
        cpw_1_min : float  Critical power for 1 minute.
        cpw_2_min : float  Critical power for 2 minutes.
        cpw_3_min : float  Critical power for 3 minutes.
        cpw_5_min : float  Critical power for 5 minutes.
        cpw_10_min: float  Critical power for 10 minutes.
        cpw_12_min: float  Critical power for 12 minutes.
        cpw_15_min: float  Critical power for 15 minutes.
        cpw_20_min: float  Critical power for 20 minutes.
        cpw_30_min: float  Critical power for 30 minutes.
        cpw_40_min: float  Critical power for 40 minutes.
    """
    zwiftid   : Optional[int]   = 0    # Zwift ID of the rider
    name      : Optional[str]   = ""   # Name of the rider
    cpw_5_sec : Optional[float] = 0.0  # Critical power for 5 seconds
    cpw_15_sec: Optional[float] = 0.0  # Critical power for 15 seconds
    cpw_30_sec: Optional[float] = 0.0  # Critical power for 30 seconds
    cpw_1_min : Optional[float] = 0.0  # Critical power for 1 minute
    cpw_2_min : Optional[float] = 0.0  # Critical power for 2 minutes
    cpw_3_min : Optional[float] = 0.0  # Critical power for 3 minutes
    cpw_5_min : Optional[float] = 0.0  # Critical power for 5 minutes
    cpw_10_min: Optional[float] = 0.0  # Critical power for 10 minutes
    cpw_12_min: Optional[float] = 0.0  # Critical power for 12 minutes
    cpw_15_min: Optional[float] = 0.0  # Critical power for 15 minutes
    cpw_20_min: Optional[float] = 0.0  # Critical power for 20 minutes
    cpw_30_min: Optional[float] = 0.0  # Critical power for 30 minutes
    cpw_40_min: Optional[float] = 0.0  # Critical power for 40 minutes
