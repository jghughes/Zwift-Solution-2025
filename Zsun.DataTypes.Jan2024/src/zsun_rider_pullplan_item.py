from dataclasses import dataclass

@dataclass
class RiderPullPlanItem():
    speed_kph             : float = 0
    p1_duration           : float = 0
    p1_w                  : float = 0
    p2_w                  : float = 0
    p3_w                  : float = 0
    p4_w                  : float = 0
    average_watts         : float = 0
    normalized_watts      : float = 0
    diagnostic_message    : str = ""

