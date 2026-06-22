import numpy as np

COEFFICIENT_g: float = 9.81  # gravity (m/s^2)
COEFFICIENT_rho: float = 1.225  # air density at sea level (kg/m^3)
COEFFICIENT_Cd: float = 0.63  # typical for road cyclist
COEFFICIENT_Crr: float = 0.004  # typical for road tires
COEFFICIENT_bike_weight_kg = 8.0 # The standard weight of the bike in kilograms. This is a constant value used in calculations related to the total weight of the rider and bike combination. 

#The above coefficients are based on the physics of cycling and take into account various factors such as air resistance, rolling resistance, and gravitational forces. The values are typical for a road cyclist on flat terrain, and they are used in the calculations to estimate the power required to maintain a certain speed. See jgh_formulae00.py, test01() for details of the speeds measured by ZwiftInsider in August 2023 at 300W and 400W. He is 183cm, and 75kg. 


AERO_POSITION_FACTOR_HOODS = 1.7 # all these aero parameters come from ChatGPT, but i feel this one ties back to what ZwiftInsider used in his individual road tests
AERO_POSITION_FACTOR_TT = 1.05
AERO_POSITION_FACTOR_SUPERTUCK = 0.75
AERO_POSITION_FACTOR_FULLTUCK = 0.55
AERO_POSITION_FACTOR_DEFAULT = AERO_POSITION_FACTOR_HOODS # for Brute and ITT, this seems to produce the most sensible results that pass the smell-test.
# AERO_POSITION_FACTOR_DEFAULT = AERO_POSITION_FACTOR_TT # for Brute, this is too aggressive and neuters wind resistance and the benefits of drafting.

DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT = 1.0 # each TTT team has its own factor depending on the calibre of the team. see class RepositoryOfTeamRosters in Zsun01/src/data_repositories/repository_of_team_rosters.py for details. This is the default factor used in the unliely event that a team does not have a specific factor defined. 

DEFAULT_INTENSITY_FACTOR_FOR_ROUTES_AND_SEGMENTS = 1.0 # This is the default intensity factor used for single-rider routes when no specific factor is defined. 1.0 means a 90-day best. 0.9 is practically achievable.

# SINGLE_SEGMENT_PREDICTION_DISTANCE_KM = 3.52 # A standard segment as a simple benchmark. See model_builders.py and repository_of_riders. Tempus Fugit=19.6 km inc lead-in. Alpe du Zwift=12.2 km. The Grade KOM=3.52
DEFAULT_PACELINE_SLOPE_PC: float = 0.0

POWER_CURVE_IN_PACELINE = np.array([400, 309, 277, 268, 261, 255, 250, 245], dtype=np.float64) # For all the details of the studies done by Zwift Insider see:- https://zwiftinsider.com/tt-drafting-pd41/ and https://zwiftinsider.com/road-bike-drafting-pd41/ These are summarised in docs/zwiftinsider_stuff.txt. The tests were done in August 2023, measuring Pack Dynamics 4.1. Tests were done in an isolated event on Watopias Tempus Fugit route because its the flattest on Zwift and has a timed section (Fuego Flats Reverse, 7.1km long) which could be used to measure the speeds of each test formation precisely. Zwift Insider did a pair of tests - pulling at 300W and 400W respectively. They produced near identical results in terms of percentage saving in the draft. The curve I chose is the TTT curve for pulling @400W for 46.47 kph. 

PULL_DURATION_OPTIONS_SEC: tuple[float] = [0.0, 30.0, 60.0, 90.0, 120.0, 180.0, 240.0] # NB. the elements MUST BE IN ASCENDING ORDER otherwise the algorithms will not work correctly. The list can be truncated to reduce compute time,maybe to handle larger groups of riders for example, but the values of the elements are fixed, they MUST NOT BE CHANGED otherwise the algorithms will generate nonesense. The values in this array map to the code in RiderComputeItem.get_proxy_pull_watts(..), which in turn maps to the values of RiderComputeItem.get_proxy_30sec_pull_watts(), RiderComputeItem.get_proxy_1_minute_pull_watts(), RiderComputeItem.get_proxy_2_minute_pull_watts(), RiderComputeItem.get_proxy_3_minute_pull_watts(), and RiderComputeItem.get_proxy_4_minute_pull_watts(). These methods are where the magic of curve-fitting comes together with the empirical experience of DaveK as a regular TTT racer. Each method is based parameters for what DaveK feels he can achieve in terms of repeated efforts and over/under intervals in a race. Assuming 8 riders, I recommend max 7 pull periods, otherwise the solution space becomes too large and the algorithm takes too long to compute (more than a minute). The pull periods are in seconds, and they represent the time each rider spends at the front of the paceline during a ride. The first_name element (0.0) is included to represent the case where a rider does not take a pull. The functions affected by PULL_DURATION_OPTIONS_SEC produce the Cartesian product of the allowed pull periods for each rider. For n riders and k allowed pull periods, it generates k^n possible sequences. Each row in the returned array is a sequence of pull periods for the paceline. For instance, six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. This is a large number, but it is manageable for the algorithm to process within a reasonable time frame, especially with the solution-space pruning applied prior to compute expensive processing. Pruning itself is compute intense, but much less intense than subsequent processing.



SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # Below this threshold, serial-processing is faster than parallel-processing.Above this threshold, parallel-processing is faster. The threshold is empirically determined and might be different on different machines with different number physicaland virtual cores. see test01() in formula08.py for details of the determination.

ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL = 1000 # Emprically researched. See test01() in formula08.py for details of the determination. The sweet zone is 1,000 - 2,500, which keeps compute time within a 7 - 14sec time-frame for up to 6 riders. This constant is an aspirational  target. If the solution space is smaller than 1,000, we do not prune it. We use brute force to analyse and solve the solution space without compromise. If the solution space is more than 1,000, we throw the pruning algorithm at it. The algorithm breaks as soon as the pruned space dips below 1,000. if the algorithm goes all the way and the solution space is still more than 1,000, that's the end of the story. We analyse the space that remains, no matter how time-consuming. The Cartesian cross product of eight riders and seven pull sequences generates a solution space of 5.76 million which takes literally days to compute. The algorithm prunes this down to 3,003 which is manageable (39sec compute time). 







