import numpy as np


# POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217], dtype=np.float64) #Follower's in the paceline are based on ZwiftInsider's power matrix.
POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217, 202, 190, 180, 172], dtype=np.float64) #extras added arbitrarily by JGH to cater for more riders in the paceline. 


STANDARD_PULL_PERIODS_SEC_AS_LIST: list[float] = [0.0, 30.0, 60.0, 120.0, 180.0, 240.0, 300.0] # NB. the elements MUST BE IN ASCENDING ORDER. Standard pull periods (in seconds) for all pull planning N.B. be sure to list these from smallest to largest, otherwise the algorithms will not work correctly. The order of the pull periods is important for the logic that determines the best pull period for each rider. the elements in this array must be consistent with the specs in ZsunItem, specifically the suite of methods def get_standard_30sec_pull_watts(..) e.t.c. and the method def get_standard_pull_watts(..).  Assuming 8 riders, I recommend max 5 pull periods, otherwise the solution space becomes too large and the algorithm takes too long to compute (more than a minute). The pull periods are in seconds, and they represent the time each rider spends at the front of the paceline during a ride. The first element (0.0) is included to represent the case where a rider does not take a pull. This function affected by STANDARD_PULL_PERIODS_SEC_AS_LIST produces the Cartesian product of the allowed pull periods for each rider. For n riders and k allowed pull periods, it generates k^n possible sequences. Each row in the returned array is a sequence of pull periods for the paceline. For instance, six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. This is a large number, but it is manageable for the algorithm to process within a reasonable time frame, especially with the filtering applied later in the process.


EXERTION_INTENSITY_FACTOR_LIMIT = 0.95 # maximum intensity factor for exertion of individuals in the paceline: 1.05 for Sirius. 0.95 for Betel


SAFE_LOWER_BOUND_KPH = 10.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 - 55 kph. round lower bound to to 10 to be safe.


CHUNK_OF_KPH_PER_ITERATION = 5.0 # The speed is increased by this chunk in each iteration of the binary search. This is an arbitrary value chosen to ensure that the search progresses quickly enough to find a constraint-busting speed within the maximum number of iterations. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical step size for the search algorithm.


SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH = 20 # the ample maximum number of attempts to find the upper bound for the binary search. This is empirically determined and may change with hardware and software improvements. The number is an arbitrary upper limit chosen to prevent the loop from running indefinitely in case a constraint-busting speed is never found. It acts as a safety net to avoid infinite loops.There is no mathematical or domain-specific reason for the value in this context. It is not derived from the number of riders, the range of speeds, or any other parameter. It is simply a "reasonable" number of attempts to find a speed that invalidates at least one rider's . 


REQUIRED_PRECISION_OF_SPEED = 0.01 # The desired precision for the speed binary search algorithm. This is the smallest difference in speed that we consider significant for the purpose of finding a constraint-busting speed. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical threshold for determining when to halt the algorithm.


MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30 # Having applied SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH Maximum number of iterations for the binary search to find a constraint-busting speed. This is an arbitrary limit chosen to prevent the search from running indefinitely. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical upper bound for the search algorithm. The algorithm typically takes 10 iterations when commencing from a safe starting base.


SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # Below this threshold, serial-processing is faster than parallel-processing.Above this threshold, parallel-processing is faster, so that is what we use. The threshold is empirically determined and will be different on different machines. see main01() in formula08.py for details of the determination.

ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL = 1000 # Somewhat arbitary. Emprically detemined. See main01() in formula08.py for details of the determination. The sweet zone is 1,000 - 2,500, which keeps compute time within a 7 - 14sec zone for up to 6 riders. A threshold for the number of alternative solutions we are willing to analyse by uncompromising brute force before we lose patience with the amount of time taken to compute. More than this and our strategy to limt the time is to apply a heuristic to prune the solution space. The Cartesian cross product of eight riders and seven pull sequences generates a solution space of 5.76 million which would take literally days to compute. By pruning, we prune these very nearly down to 3,003 which is maneageble at 39sec. 



