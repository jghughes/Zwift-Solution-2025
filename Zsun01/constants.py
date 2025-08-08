import numpy as np


POWER_CURVE_IN_PACELINE = np.array([350, 267, 235, 229, 223, 197, 191, 185], dtype=np.float64) # For all the details of the studies done by Zwift Insider see:- https://zwiftinsider.com/road-bike-drafting-pd41/extras These are summarised in docs/zwiftinsider_stuff.txt. The tests were done in August 2023, measuring Pack Dynamics 4.1 for road bikes. Tests were done in an isolated event on Watopia’s Tempus Fugit route because it’s the flattest on Zwift and has a timed section (Fuego Flats Reverse, 7.1km long) which could be used to measure the speeds of each test formation precisely. Zwift Insider did a pair of test - pulling at 300W and 400W respectively. They produced near identical results in terms of percentage saving in the draft. I averaged these to derive the first four values of POWER_CURVE_IN_PACELINE and then I did a straight-line extrapolation for an additional four riders to cater for an 8 person paceline. 



STANDARD_PULL_PERIODS_SEC_AS_LIST: list[float] = [0.0, 30.0, 60.0, 120.0, 180.0, 240.0, 300.0] # NB. the elements MUST BE IN ASCENDING ORDER. Standard pull periods (in seconds) for all pull planning N.B. be sure to list these from smallest to largest, otherwise the algorithms will not work correctly. The order of the pull periods is important for the logic that determines the best pull period for each rider. the elements in this array must be consistent with the specs in ZsunItem, specifically the suite of methods def get_standard_30sec_pull_watts(..) e.t.c. and the method def get_standard_pull_watts(..).  Assuming 8 riders, I recommend max 7 pull periods, otherwise the solution space becomes too large and the algorithm takes too long to compute (more than a minute). The pull periods are in seconds, and they represent the time each rider spends at the front of the paceline during a ride. The first element (0.0) is included to represent the case where a rider does not take a pull. The functions affected by STANDARD_PULL_PERIODS_SEC_AS_LIST produce the Cartesian product of the allowed pull periods for each rider. For n riders and k allowed pull periods, it generates k^n possible sequences. Each row in the returned array is a sequence of pull periods for the paceline. For instance, six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. This is a large number, but it is manageable for the algorithm to process within a reasonable time frame, especially with the solution-space pruning applied prior to compute expensive processing. Pruning itself is compute intense, but much less intense than subsequent processing.


DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT = 1.0 # each team has its own factor. see class RepositoryOfTeams in Zsun01/src/data_repositories/team_rosters.py for details. This is the default factor used when a team does not have a specific factor defined. 


SAFE_LOWER_BOUND_KPH = 10.0 # most TTT will be 35 - 55 kph. round lower bound to to 10 to be safely below all conceivable scenarios.


CHUNK_OF_KPH_PER_ITERATION = 5.0 # Starting at SAFE_LOWER_BOUND_KPH, the speed is increased by this chunk in each iteration of the binary search. This is an arbitrary value chosen to ensure that the search progresses quickly enough to find a constraint-busting speed within the maximum number of iterations, namely SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical step size for the search algorithm.


SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH = 20 # the ample maximum number of attempts to find the upper bound for the binary search. This is empirically determined and may change with hardware and software improvements. The number is an arbitrary upper limit chosen to prevent the loop from running indefinitely in case a constraint-busting speed is never found. It acts as a safety net to avoid infinite loops.There is no mathematical or domain-specific reason for the value in this context. It is not derived from the number of riders, the range of speeds, or any other parameter. It is simply a "reasonable" number of attempts to find a speed that invalidates at least one rider's . 


REQUIRED_PRECISION_OF_SPEED = 0.01 # The desired precision for the speed binary search algorithm. This is the smallest difference in speed that we consider significant for the purpose of finding a constraint-busting speed. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical threshold for determining when to halt the algorithm. The more precise the speed, the more accurate the results will be, but it will also increase the number of iterations required to find a solution. The value is chosen to balance precision and performance, ensuring that the algorithm converges quickly while still providing a meaningful result.


MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30 # Having applied SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH Maximum allowable number of iterations for the binary search to find a constraint-busting speed. This is an arbitrary limit chosen to prevent the search from running indefinitely. The algorithm typically takes 10 iterations when commencing from a safe starting base.


SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # Below this threshold, serial-processing is faster than parallel-processing.Above this threshold, parallel-processing is faster. The threshold is empirically determined and might be different on different machines with different number physicaland virtual cores. see main01() in formula08.py for details of the determination.

ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL = 1000 # Emprically researched. See main01() in formula08.py for details of the determination. The sweet zone is 1,000 - 2,500, which keeps compute time within a 7 - 14sec time-frame for up to 6 riders. This constant is an aspirational  target. If the solution space is smaller than 1,000, we do not prune it. We use brute force to analyse and solve the solution space without compromise. If the solution space is more than 1,000, we throw the pruning algorithm at it. The algorithm breaks as soon as the pruned space dips below 1,000. if the algorithm goes all the way and the solution space is still more than 1,000, that's the end of the story. We analyse the space that remains, no matter how time-consuming. The Cartesian cross product of eight riders and seven pull sequences generates a solution space of 5.76 million which takes literally days to compute. The algorithm prunes this down to 3,003 which is maneageble (39sec compute time). 



