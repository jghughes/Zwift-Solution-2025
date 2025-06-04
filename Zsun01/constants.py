import numpy as np

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"


DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"


POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217, 202, 190, 180, 172], dtype=np.float64) #extras added arbitrarily
# POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217], dtype=np.float64) #Follower's in the paceline are based on ZwiftInsider's power matrix.


STANDARD_PULL_PERIODS_SEC: list[float] = [30.0, 60.0, 120.0, 180.0, 240.0] # Constant: Standard pull periods (in seconds) for all pull planning


BINARY_SEARCH_SEED_KPH = 30.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 -55 kph, but this is a safe start.


MAX_INTENSITY_FACTOR = 0.95 # maximum intensity factor for exertion: 1.05 for Sirius. Betel is 0.95 or 1.00?

SOLUTION_SPACE_SIZE_CONSTRAINT = 1024 # Empirically determined maximum number of schedules before needing filtering to impove speed to less than approx 30 sec for eight riders. This max allows up to five riders to be explored exhaustively (for up to four standard pull periods) before filtering kicks in to reduce the number of schedules evaluated. But the 30sec is sensitive to the mix of ability on the team and the slectivity of the filters to individuals concerned. It can easily be three times as much.

SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # number of schedules being evaluated. below this threshold, the serial processing is faster than parallel processing. Above this threshold, parallel processing is faster. This is empirically determined and may change with hardware and software improvements.



