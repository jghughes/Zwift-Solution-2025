from dataclasses import dataclass

@dataclass
class CriticalPowerCurveItem:
    """
    A data class representing a zwiftrider's critical power curve data.
    
    Attributes:
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
    cpw_5_sec : float  = 0.0
    cpw_15_sec: float  = 0.0
    cpw_30_sec: float  = 0.0
    cpw_1_min : float  = 0.0
    cpw_2_min : float  = 0.0
    cpw_3_min : float  = 0.0
    cpw_5_min : float  = 0.0
    cpw_10_min: float  = 0.0
    cpw_12_min: float  = 0.0
    cpw_15_min: float  = 0.0
    cpw_20_min: float  = 0.0
    cpw_30_min: float  = 0.0
    cpw_40_min: float  = 0.0

