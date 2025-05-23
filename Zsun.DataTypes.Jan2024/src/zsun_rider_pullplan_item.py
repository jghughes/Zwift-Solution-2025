from dataclasses import dataclass

@dataclass
class RiderPullPlanItem():
    speed_kph             : float = 0
    p1_duration           : float = 0
    # p1_wkg                : float = 0
    # p1_ratio_to_1hr_w     : float = 0
    p1_w                  : float = 0
    p2_w                  : float = 0
    p3_w                  : float = 0
    p4_w                  : float = 0
    # zsun_one_hour_watts   : float = 0
    # p__w                  : float = 0
    normalized_watts      : float = 0
    # np_intensity_factor   : float = 0 # denominator is 1hour watts, not zFTP
    diagnostic_message    : str = ""

