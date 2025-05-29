import numpy as np

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"


DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"


POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217], dtype=np.float64) #Follower's in the paceline are based on ZwiftInsider's power matrix.


STANDARD_PULL_PERIODS_SEC: list[float] = [30.0, 60.0, 120.0, 180.0] # Constant: Standard pull periods (in seconds) for all pull planning


BINARY_SEARCH_SEED_KPH = 30.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 -55 kph, but this is a safe start.


MAX_INTENSITY_FACTOR = 1.00 # maximum intensity factor for exertion: 1.05 for Sirius. Betel is 0.95 or 1.00?



