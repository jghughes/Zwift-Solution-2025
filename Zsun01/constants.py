import numpy as np

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"


DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"


# POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217], dtype=np.float64) #Follower's in the paceline are based on ZwiftInsider's power matrix.
POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217, 202, 190, 180, 172], dtype=np.float64) #extras added arbitrarily by JGH to cater for more riders in the paceline. 

ARRAY_OF_STANDARD_PULL_PERIODS_SEC: list[float] = [0.0, 30.0, 60.0, 120.0, 180.0, 240.0] # NB. the elements MUST BE IN ASCENDING ORDER. Standard pull periods (in seconds) for all pull planning N.B. be sure to list these from smallest to largest, otherwise the algorithms will not work correctly. The order of the pull periods is important for the logic that determines the best pull period for each rider. Assuming 8 riders, I recommend max 5 pull periods, otherwise the solution space becomes too large and the algorithm takes too long to compute (more than a minute). The pull periods are in seconds, and they represent the time each rider spends at the front of the paceline during a ride. The first element (0.0) is included to represent the case where a rider does not take a pull. This function affected by ARRAY_OF_STANDARD_PULL_PERIODS_SEC produces the Cartesian product of the allowed pull periods for each rider. For n riders and k allowed pull periods, it generates k^n possible sequences. Each row in the returned array is a sequence of pull periods for the paceline. For instance, six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. This is a large number, but it is manageable for the algorithm to process within a reasonable time frame, especially with the filtering applied later in the process.


SAFE_LOWER_BOUND_TO_COMMENCE_BINARY_SEARCH_FOR_A_CONSTRAINT_BUSTING_SPEED_KPH = 30.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 - 55 kph, but this is a safe start. ssay, 60 is the highest, therefore the afe num of iterations is 7. round it to 10 to be safe.

SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_CONSTRAINT_VIOLATING_SPEED_KPH = 10 # maximum number of attempts to find the upper bound for the binary search. This is empirically determined and may change with hardware and software improvements. The number 10 is an arbitrary upper limit chosen to prevent the loop from running indefinitely in case a constraint-busting speed is never found. It acts as a safety net to avoid infinite loops.There is no mathematical or domain-specific reason for the value 10 in this context. It is not derived from the number of riders, the range of speeds, or any other parameter. It is simply a "reasonable" number of attempts to find a speed that invalidates at least one rider's plan. 

INCREASE_IN_SPEED_PER_ITERATION_KPH = 5.0 # The speed is increased by this amount in each iteration of the binary search. This is an arbitrary value chosen to ensure that the search progresses quickly enough to find a constraint-busting speed within the maximum number of iterations. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical step size for the search algorithm.

DESIRED_PRECISION_KPH = 0.01 # The desired precision for the speed search. This is the smallest difference in speed that we consider significant for the purpose of finding a constraint-busting speed. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical threshold for determining when to stop the search.

MAX_PERMITTED_ITERATIONS = 30 # Maximum number of iterations for the binary search to find a constraint-busting speed. This is an arbitrary limit chosen to prevent the search from running indefinitely. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical upper bound for the search algorithm.


# EXERTION_INTENSITY_FACTOR = 100.0 # maximum intensity factor for exertion: 1.05 for Sirius. Betel is 0.95 or 1.00?
EXERTION_INTENSITY_FACTOR = 0.95 # maximum intensity factor for exertion: 1.05 for Sirius. Betel is 0.95 or 1.00?

SOLUTION_SPACE_SIZE_CONSTRAINT = 1024 # Empirically determined maximum number of schedules before needing filtering to impove speed to less than approx 30 sec for eight riders. This max allows up to five riders to be explored exhaustively (for up to four standard pull periods) before filtering kicks in to reduce the number of schedules evaluated. But the 30sec is sensitive to the mix of ability on the team and the slectivity of the filters to individuals concerned. It can easily be three times as much.

SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # number of schedules being evaluated. below this threshold, the serial processing is faster than parallel processing. Above this threshold, parallel processing is faster. This is empirically determined and may change with hardware and software improvements.



