from enum import Enum
from typing import List, Tuple
import numpy as np

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"


DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"


# POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217], dtype=np.float64) #Follower's in the paceline are based on ZwiftInsider's power matrix.
POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217, 202, 190, 180, 172], dtype=np.float64) #extras added arbitrarily by JGH to cater for more riders in the paceline. 

STANDARD_PULL_PERIODS_SEC_AS_LIST: list[float] = [0.0, 30.0, 60.0, 120.0, 180.0, 240.0, 300.0] # NB. the elements MUST BE IN ASCENDING ORDER. Standard pull periods (in seconds) for all pull planning N.B. be sure to list these from smallest to largest, otherwise the algorithms will not work correctly. The order of the pull periods is important for the logic that determines the best pull period for each rider. the elements in this array must be consistent with the specs in ZsunRiderItem, specifically the suite of methods def get_standard_30sec_pull_watts(..) e.t.c. and the method def get_standard_pull_watts(..).  Assuming 8 riders, I recommend max 5 pull periods, otherwise the solution space becomes too large and the algorithm takes too long to compute (more than a minute). The pull periods are in seconds, and they represent the time each rider spends at the front of the paceline during a ride. The first element (0.0) is included to represent the case where a rider does not take a pull. This function affected by STANDARD_PULL_PERIODS_SEC_AS_LIST produces the Cartesian product of the allowed pull periods for each rider. For n riders and k allowed pull periods, it generates k^n possible sequences. Each row in the returned array is a sequence of pull periods for the paceline. For instance, six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. This is a large number, but it is manageable for the algorithm to process within a reasonable time frame, especially with the filtering applied later in the process.

EXERTION_INTENSITY_FACTOR_LIMIT = 0.95 # maximum intensity factor for exertion of individuals in the paceline: 1.05 for Sirius. 0.95 for Betel

SAFE_LOWER_BOUND_KPH = 10.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 - 55 kph. round lower bound to to 10 to be safe.

CHUNK_OF_KPH_PER_ITERATION = 5.0 # The speed is increased by this chunk in each iteration of the binary search. This is an arbitrary value chosen to ensure that the search progresses quickly enough to find a constraint-busting speed within the maximum number of iterations. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical step size for the search algorithm.

SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH = 20 # the ample maximum number of attempts to find the upper bound for the binary search. This is empirically determined and may change with hardware and software improvements. The number is an arbitrary upper limit chosen to prevent the loop from running indefinitely in case a constraint-busting speed is never found. It acts as a safety net to avoid infinite loops.There is no mathematical or domain-specific reason for the value in this context. It is not derived from the number of riders, the range of speeds, or any other parameter. It is simply a "reasonable" number of attempts to find a speed that invalidates at least one rider's . 

REQUIRED_PRECISION_OF_SPEED = 0.01 # The desired precision for the speed binary search algorithm. This is the smallest difference in speed that we consider significant for the purpose of finding a constraint-busting speed. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical threshold for determining when to halt the algorithm.

MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30 # Having applied SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH Maximum number of iterations for the binary search to find a constraint-busting speed. This is an arbitrary limit chosen to prevent the search from running indefinitely. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical upper bound for the search algorithm. The algorithm typically takes 10 iterations when commencing from a safe starting base.



SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # Below this threshold, serial-processing is faster than parallel-processing.Above this threshold, parallel- processing is faster so that is what we use. The threshold is empirically determined and will be different on different machines. 

SOLUTION_FILTERING_THRESHOLD = 1024 # Somewhat arbirtary. A threshold for the number of alternative solutions we are willing to analyse by uncompromising brute force before we lose patience with the amount of time it is taking to compute. More than this and our strategy to limt the time is to apply a heuristic to prune the solution space. It is preferable to avoid filtering because filtering is a heuristic and all heuristics entail risk (albeit tiny in this case) that they will inadvertently exclude a winning solution. The Cartesian cross product of eight riders and six pull sequences generates a solution space of 1.7 million. By filtering, we prune these very nearly down to the SOLUTION_FILTERING_THRESHOLD. Compute time is about twenty seconds.

# SOLUTION CONFIGURATION
class PacelineSolutionType(Enum):
    THIRTY_SEC_PULL = "thirty_sec_pull"
    IDENTICAL_PULL = "identical_pull"
    BALANCED_INTENSITY = "balanced_intensity"
    EVERYBODY_PULL_HARD = "everybody_pull_hard"
    HANG_IN = "hang_in"
    LAST_FIVE = "last_five"
    LAST_FOUR = "last_four"


SOLUTION_CONFIG: List[Tuple[PacelineSolutionType, str, str]] = [
    (PacelineSolutionType.THIRTY_SEC_PULL,     "\nTHIRTY-SECOND PULLS PLAN", "(thirty_sec second pull for everyone)"),
    (PacelineSolutionType.IDENTICAL_PULL,      "\nIDENTICAL-PULLS PLAN",     "(identical pull for everyone)"),
    (PacelineSolutionType.BALANCED_INTENSITY,  "\nBALANCED-INTENSITY PLAN",  "(intensity is balanced. everybody pulls.)"),
    (PacelineSolutionType.EVERYBODY_PULL_HARD, "\nPUSH-HARD PLAN",           "(everybody pulls. weaker riders work hardest.)"),
    (PacelineSolutionType.HANG_IN,             "\nHANG-IN PLAN",             "(everybody rotates, maybe or maybe not pulling)"),
    (PacelineSolutionType.LAST_FIVE,           "\nLAST-FIVE RIDERS PLAN",    "(last five. everybody rotates, maybe or maybe not pulling)"),
    (PacelineSolutionType.LAST_FOUR,           "\nLAST-FOUR RIDERS PLAN",    "(last four. everybody rotates, maybe or maybe not pulling)"),
]

SOLUTION_FILENAMES = {
    PacelineSolutionType.THIRTY_SEC_PULL:    "thirty_second_pulls_plan.html",
    PacelineSolutionType.IDENTICAL_PULL:     "identical_pulls_plan.html",
    PacelineSolutionType.BALANCED_INTENSITY: "balanced_intensity_plan.html",
    PacelineSolutionType.EVERYBODY_PULL_HARD:"everybody_push_hard_plan.html",
    PacelineSolutionType.HANG_IN:            "hang_in_plan.html",
    PacelineSolutionType.LAST_FIVE:          "last_five_riders_plan.html",
    PacelineSolutionType.LAST_FOUR:          "last_four_riders_plan.html",
}

FOOTNOTES = """
    <div class="footnote">
        <sup>1</sup> Pull: Watts and duration of each rider's main pull. Higher ranking riders are prioritised for longer pulls and are located front and rear of the paceline, protecting weaker riders in the middle. Standard pulls range between 30 seconds and five minutes and corresponding pulling capabilities are based on a curve fitted to a rider's ZwiftPower data in their 3.5 - 20 minute window. Riders are not ranked according to zFTP, they are ranked according to how hard they can pull for one-minute.<br>
        <sup>2</sup> zFTP: Zwift Functional Threshold Power. zFTP metrics are displayed, but play no role in computations.<br>
        <sup>3</sup> NP: Normalized Power. Calculated from rolling-average watts using a five-second window.<br>
        <sup>4</sup> IF: Intensity factor. Normalised power divided by calculated one-hour pulling capability. One-hour capability is based on a curve fitted to a rider's ZwiftPower data in the 8 - 40-minute window and extrapolated out to one hour. This is a rider's real FTP. <br>
        <sup>5</sup> Limit: For ride plans where everybody pulls, the speed of the paceline is restricted to the pulling capability of the weakest rider and/or the intensity of the hardest-working rider. There is no protection for weaker or harder-working riders in other plans.<br>
    </div>
    """

