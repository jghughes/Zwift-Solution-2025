from typing import Dict, List, Tuple

import numpy as np
# from numpy.typing import NDArray
from scipy.optimize import newton

from constants import INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH, REQUIRED_NEWTON_SOLVER_DISTANCE_PRECISION_KM
from jgh_formulae01 import solve_for_speed_from_wattage_using_newton, calculate_watts_from_speed
from jgh_number import safe_divide
from jgh_power_curve_fit_models import decay_model_numpy
from rider_compute_item import RiderComputeItem
from route_segment_item import RouteSegmentItem

# All of these functions are called during parallel processing. Logging forbidden

def solve_for_hypothetical_speed_of_rider_at_given_power(rider : RiderComputeItem, power: float, slope_pc: float = 0.0) -> float:
    """
    Estimate the speed (km/h) given the power (wattage) for the specified
    rider and the slope he is riding on. Wind resistance is governed by his 
    height_cm and weight_kg. Uses the Newton-Raphson solver.

    Args:
    power (float): The power in watts.
    slope_pc (float): The slope in %.

    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(power, rider.weight_kg, rider.height_cm, slope_pc)
    return speed_kph

def calculate_hypothetical_power_of_rider_at_given_speed(rider : RiderComputeItem, speed_kph: float, slope_pc: float = 0.0) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), rider weight_kg (kg) and 
    height_cm (cm), and slope (%).

    Args:
    speed (float): The speed in km/h.
    slope_pc (float): The slope is %.

    Returns:
    float: The calculated power in watts.
    """
    power = calculate_watts_from_speed(speed_kph, rider.weight_kg, rider.height_cm, slope_pc)
    return power

def solve_for_speed_at_standard_00sec_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    return solve_for_speed_at_standard_30sec_pull_watts(rider, slope_pc)

def solve_for_speed_at_standard_30sec_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_proxy_30sec_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_1_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_proxy_1_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_2_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_proxy_2_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_3_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_proxy_3_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_4_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_proxy_4_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_n_second_watts(rider : RiderComputeItem, seconds: float, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    for a specific duration in seconds.
    Args:
    seconds (float): The duration in seconds.
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_n_second_curvefit_y_ordinate_watts(seconds), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_one_hour_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_newton(rider.get_1_hour_curvefit_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_fastest_achievable_time_by_rider_for_segment_using_newton(rider: RiderComputeItem, segment: RouteSegmentItem) -> float:
    """
    Calculate the duration in seconds for a rider to cover a given segment,
    using their fitted 60-minute power-duration decay curve.

    The power-duration decay curve is evaluated by decay_model_numpy(), which
    is the single source of truth for the decay formula. Refer to that function
    for the formula definition and its parameters.

    The curve coefficients are sourced from the rider object:
        coefficient = jgh_60_min_curve_coefficient
        exponent    = jgh_60_min_curve_exponent

    This curve is applied across the full range of durations. For the
    practical range of 30-120 minutes this is the correct model.

    The problem is self-referential: duration drives power (via the decay
    curve), power drives speed (via physics), and speed drives distance.
    It is solved by Newton's method (secant variant) as a root-finding
    problem:
        distance_residual_km(duration_seconds) = speed(duration_seconds)
            * (duration_seconds / 3600.0) - segment.distance_km = 0

    Args:
        rider (RiderComputeItem): The rider whose curve coefficients are used.
        segment (RouteSegmentItem): The route segment object containing distance_km and slope_per_cent.

    Returns:
        float: The estimated duration in seconds. Returns 0.0 if the rider's
               curve has not been fitted (zero coefficient) or if the segment distance is nonsensical.
    """
    decay_curve_coefficient: float = rider.jgh_60_min_curve_coefficient
    decay_curve_exponent: float = rider.jgh_60_min_curve_exponent

    # Guard: curve has not been fitted
    if decay_curve_coefficient == 0.0 or decay_curve_exponent == 0.0:
        return 0.0

    # Guard: nonsensical distance
    if segment.distance_km <= 0.0:
        return 0.0

    slope_fraction = segment.slope_per_cent / 100.0
    initial_estimate_of_root_sec: float = (segment.distance_km / INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH) * 3600.0 

    def distance_residual_km(duration_seconds: float) -> float:
        if duration_seconds < 1.0:
            duration_seconds = 1.0  # clamp: decay_model_numpy requires xdata >= 1; sub-1s durations are non-physical anyway

        watts: float = float(decay_model_numpy(np.array([duration_seconds]), decay_curve_coefficient, decay_curve_exponent)[0])
        speed_kph: float = solve_for_speed_from_wattage_using_newton(watts, rider.weight_kg, rider.height_cm, slope_fraction)
        return speed_kph * (duration_seconds / 3600.0) - segment.distance_km

    try:
        duration_seconds: float = newton(distance_residual_km, initial_estimate_of_root_sec, tol=REQUIRED_NEWTON_SOLVER_DISTANCE_PRECISION_KM)
        print(f"solve_for_fastest_achievable_time_by_rider_for_segment_using_newton : rider {rider.zwift_id} {rider.name} distanceKm={segment.distance_km:.2f} km, initial_guess={initial_estimate_of_root_sec:.2f} sec, calculated_duration={duration_seconds:.2f} sec")
    except RuntimeError as e:
        raise ValueError(f"rider {rider.zwift_id} {rider.name} encountered a problem. solve_for_fastest_achievable_time_by_rider_for_segment_using_newton failed to converge: {e}") from e

    if duration_seconds <= 0.0:
        raise ValueError(f"rider {rider.zwift_id} {rider.name} Solver returned non-physical duration: {duration_seconds:.4f} seconds")

    return duration_seconds

def solve_for_hypothetical_route_time_at_a_mandated_power(rider: RiderComputeItem, segments: List[RouteSegmentItem], power_watts: float) -> float:
    """
    Calculate the total duration (in seconds) to ride a multi-segment route at a 
    constant mandated power.
    
    Args:
        rider (RiderComputeItem): The rider attempting the route.
        segments (List[RouteSegmentItem]): The route defined as a list of segments.
        power_watts (float): The constant wattage to maintain over the route.
        
    Returns:
        float: The sum of the durations across all segments.
    """
    total_duration_sec = 0.0
    for segment in segments:
        slope_fraction = segment.slope_per_cent / 100.0
        speed_kph = solve_for_hypothetical_speed_of_rider_at_given_power(rider, power_watts, slope_fraction)
        
        # Guard against zero or negative speeds breaking the duration math
        if speed_kph <= 0:
            return float('inf') 
            
        speed_meters_per_second = speed_kph / 3.6
        distance_meters = segment.distance_km * 1000.0
        
        segment_duration_sec = distance_meters / speed_meters_per_second
        total_duration_sec += segment_duration_sec
        
    return total_duration_sec

def solve_for_fastest_achievable_time_by_rider_for_route_using_binary_search(rider: RiderComputeItem, segments: List[RouteSegmentItem]) -> List[RouteSegmentItem]:
    """
    Solves for the optimal constant power output over a multi-segment route, 1
    mutates the segment items with the predicted performance metrics, and returns the modified list.
    
    Args:
        rider (RiderComputeItem): The rider profile containing their power curve model.
        segments (List[RouteSegmentItem]): The route defined as a list of segments.

    Returns:
        List[RouteSegmentItem]: The same list of segments, but fully populated with 
        segment_watts, segment_speed_kph, and segment_time_sec based on the optimal pace.
    """
    if not segments:
        return []

    SAFE_LOWER_BOUND_WATTS = 40.0 # pretty arbitrary. Hopefully this will be safe in all conceivable scenarios. 
    CHUNK_OF_WATTS_PER_ITERATION = 20.0 # Starting at lowest conceivable power, the watts are increased by this chunk in each iteration.
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 20 # the ample maximum number of attempts to find the upper bound for the binary search
    REQUIRED_PRECISION_OF_WATTS = 1.0 # The desired precision for the power binary search algorithm.
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30
    MAX_CONCEIVABLE_ROUTE_DURATION_SEC: float = 864000  # 10 days — beyond this, decay model extrapolation is non-physical; fall back to 1-hour power

    # 1. Setup Variables
    lowest_conceivable_power_watts = SAFE_LOWER_BOUND_WATTS 
    lower_bound_watts = lowest_conceivable_power_watts
    upper_bound_watts = lower_bound_watts

    compute_iterations_performed = 0

    # 2. Find Safe Upper Bound
    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):

        simulated_total_duration_sec = solve_for_hypothetical_route_time_at_a_mandated_power(rider, segments, upper_bound_watts)
        
        if simulated_total_duration_sec == float('inf'):
             max_power_for_duration = 0.0 # Force loop to increase watts if we can't move forward
        else:
             max_power_for_duration = (
                 rider.get_1_hour_curvefit_watts() if simulated_total_duration_sec > MAX_CONCEIVABLE_ROUTE_DURATION_SEC
                 else decay_model_numpy(simulated_total_duration_sec, rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)
             )

        # Did we push the guess power past what the rider is capable of for the time it took?
        if upper_bound_watts > max_power_for_duration:
            break
            
        upper_bound_watts += CHUNK_OF_WATTS_PER_ITERATION
        compute_iterations_performed += 1
    else:
        # Failsafe: if we max out iterations finding upper bound, return the unmodified segments
        return segments

    # 3. Binary Search
    while (upper_bound_watts - lower_bound_watts) > REQUIRED_PRECISION_OF_WATTS and compute_iterations_performed < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:
        mid_point_watts = safe_divide((lower_bound_watts + upper_bound_watts), 2)
        
        simulated_total_duration_sec = solve_for_hypothetical_route_time_at_a_mandated_power(rider, segments, mid_point_watts)
        
        if simulated_total_duration_sec == float('inf'):
            max_power_for_duration = 0.0
        else:
             max_power_for_duration = (
                 rider.get_1_hour_curvefit_watts() if simulated_total_duration_sec > MAX_CONCEIVABLE_ROUTE_DURATION_SEC
                 else decay_model_numpy(simulated_total_duration_sec, rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)
             )

        compute_iterations_performed += 1

        if mid_point_watts > max_power_for_duration:
            upper_bound_watts = mid_point_watts
        else:
            lower_bound_watts = mid_point_watts

    # 4. Final Route Result Population
    # Using the safest maximum sustainable power boundary
    converged_power_watts = upper_bound_watts

    for segment in segments:
        speed_kph = solve_for_hypothetical_speed_of_rider_at_given_power(rider, converged_power_watts, segment.slope_per_cent)
        
        segment.segment_watts = round(converged_power_watts, 1)

        if speed_kph <= 0:
            segment.segment_speed_kph = 0.0
            segment.segment_time_sec = float('inf')
        else:
            segment_duration_sec = (segment.distance_km * 1000.0) / (speed_kph / 3.6)
            segment.segment_speed_kph = round(speed_kph, 2)
            segment.segment_time_sec = round(segment_duration_sec, 1)

    return segments


