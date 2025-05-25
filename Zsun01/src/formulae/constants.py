STANDARD_PULL_PERIODS_SEC: list[float] = [30.0, 60.0, 120.0, 180.0, 240.0] # Constant: Permitted pull periods (in seconds) for all pull planning
BINARY_SEARCH_SEED_KPH = 30.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 -55 kph, but this is a safe start.
MAX_INTENSITY_FACTOR = 1.05 # maximum intensity factor for exertion for Sirius. Betel is 0.95

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

