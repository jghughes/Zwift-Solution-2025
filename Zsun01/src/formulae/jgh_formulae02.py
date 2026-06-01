from typing import Dict, List, Tuple

import numpy as np
# from numpy.typing import NDArray
from scipy.optimize import newton

from constants import INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH, REQUIRED_NEWTON_SOLVER_DISTANCE_PRECISION_KM, CHUNK_OF_WATTS_PER_ITERATION, SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH, REQUIRED_PRECISION_OF_WATTS, MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION
from jgh_formulae01 import solve_for_speed_from_wattage, calculate_watts_from_speed
from jgh_number import safe_divide
from jgh_power_curve_fit_models import decay_model_numpy
from rider_compute_item import RiderComputeItem

# All of these functions are called during parallel processing. Logging forbidden

def solve_for_speed_riding_solo(rider : RiderComputeItem, power: float, slope: float = 0.0) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight_kg (kg), and 
    height_cm (cm) using the Newton-Raphson method.

    Args:
    power (float): The power in watts.

    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(power, rider.weight_kg, rider.height_cm, slope)
    return speed_kph

def calculate_power_riding_solo(rider : RiderComputeItem, speed: float, slope: float = 0.0) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), weight_kg (kg), and 
    height_cm (cm).

    Args:
    speed (float): The speed in km/h.

    Returns:
    float: The calculated power in watts.
    """
    power = calculate_watts_from_speed(speed, rider.weight_kg, rider.height_cm, slope)
    return power

def solve_for_speed_at_standard_00sec_pull_watts(rider : RiderComputeItem, slope: float = 0.0) -> float:
    return solve_for_speed_at_standard_30sec_pull_watts(rider, slope)

def solve_for_speed_at_standard_30sec_pull_watts(rider : RiderComputeItem, slope: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_proxy_30sec_pull_watts(), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def solve_for_speed_at_standard_1_minute_pull_watts(rider : RiderComputeItem, slope: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_proxy_1_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def solve_for_speed_at_standard_2_minute_pull_watts(rider : RiderComputeItem, slope: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_proxy_2_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def solve_for_speed_at_standard_2_minute_pull_watts(rider : RiderComputeItem, slope: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_proxy_3_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def solve_for_speed_at_standard_4_minute_pull_watts(rider : RiderComputeItem, slope: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_proxy_4_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def solve_for_speed_at_n_second_watts(rider : RiderComputeItem, seconds: float, slope: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    for a specific duration in seconds.
    Args:
    seconds (float): The duration in seconds.
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_n_second_curvefit_y_ordinate_watts(seconds), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def solve_for_speed_at_one_hour_watts(rider : RiderComputeItem, slope: float = 0.0) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage(rider.get_1_hour_curvefit_watts(), rider.weight_kg, rider.height_cm, slope)
        
    return speed_kph

def calculate_route_time_for_constant_power(rider: RiderComputeItem, segments: List[Tuple[float, float]], power_watts: float) -> float:
    """
    Calculate the total duration (in seconds) required to ride a multi-segment route at a constant power output.
    
    Args:
        rider (RiderComputeItem): The rider attempting the route.
        segments (List[Tuple[float, float]]): A list of tuples, each containing (distance_km, slope_fraction).
        power_watts (float): The constant wattage to maintain over the route.
        
    Returns:
        float: The sum of the durations across all segments.
    """
    total_duration_sec = 0.0
    for distance_km, slope in segments:
        speed_kph = solve_for_speed_riding_solo(rider, power_watts, slope)
        
        # Guard against zero or negative speeds breaking the duration math
        if speed_kph <= 0:
            return float('inf') 
            
        speed_meters_per_second = speed_kph / 3.6
        distance_meters = distance_km * 1000.0
        
        segment_duration_sec = distance_meters / speed_meters_per_second
        total_duration_sec += segment_duration_sec
        
    return total_duration_sec

def solve_for_duration_on_single_segment (rider: RiderComputeItem, distanceKm: float, slope: float = 0.0) -> float:
    """
    Calculate the duration in seconds for a rider to cover a given distance
    in kilometres, using their fitted 60-minute power-duration decay curve.

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
            * (duration_seconds / 3600.0) - distanceKm = 0

    Args:
        rider (RiderComputeItem): The rider whose curve coefficients are used.
        distanceKm (float): The target distance in kilometres.
        slope (float): Road slope as a ratio (e.g., 0.05 for 5%). Defaults to 0.0.

    Returns:
        float: The estimated duration in seconds. Returns 0.0 if the rider's
               curve has not been fitted (zero coefficient).
    """
    decay_curve_coefficient: float = rider.jgh_60_min_curve_coefficient
    decay_curve_exponent: float = rider.jgh_60_min_curve_exponent

    # Guard: curve has not been fitted
    if decay_curve_coefficient == 0.0 or decay_curve_exponent == 0.0:
        return 0.0

    # Guard: nonsensical distance
    if distanceKm <= 0.0:
        return 0.0

    initial_estimate_of_root_sec: float = (distanceKm / INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH) * 3600.0 

    def distance_residual_km(duration_seconds: float) -> float:
        if duration_seconds < 1.0:
            duration_seconds = 1.0  # clamp: decay_model_numpy requires xdata >= 1; sub-1s durations are non-physical anyway


        watts: float = float(decay_model_numpy(np.array([duration_seconds]), decay_curve_coefficient, decay_curve_exponent)[0])
        speed_kph: float = solve_for_speed_from_wattage(watts, rider.weight_kg, rider.height_cm, slope)
        return speed_kph * (duration_seconds / 3600.0) - distanceKm

    try:
        duration_seconds: float = newton(distance_residual_km, initial_estimate_of_root_sec, tol=REQUIRED_NEWTON_SOLVER_DISTANCE_PRECISION_KM)
        print(f"solve_for_duration_on_single_segment : rider {rider.zwift_id} {rider.name} distanceKm={distanceKm:.2f} km, initial_guess={initial_estimate_of_root_sec:.2f} sec, calculated_duration={duration_seconds:.2f} sec")
    except RuntimeError as e:
        raise ValueError(f"rider {rider.zwift_id} {rider.name} encountered a problem. solve_for_duration_on_single_segment  failed to converge: {e}") from e

    if duration_seconds <= 0.0:
        raise ValueError(f"rider {rider.zwift_id} {rider.name} Solver returned non-physical duration: {duration_seconds:.4f} seconds")

    return duration_seconds

def solve_for_duration_on_multi_segment_route(rider: RiderComputeItem, segments: List[Tuple[float, float]]) -> List[Tuple[float, float, float]]:
    """
    Solves for the optimal constant power output over a multi-segment route and returns the duration details.
    
    This function uses a binary search pattern parallel to the paceline solvers found elsewhere 
    in the solution, adapted for Wattage bounds against a rider's duration curve.

    Args:
        rider (RiderComputeItem): The rider profile containing their power curve model.
        segments (List[Tuple[float, float]]): A list of tuples, each containing (distance_km, slope_fraction).

    Returns:
        List[Tuple[float, float, float]]: A simulated route breakdown containing 
        (distance_km, slope_fraction, segment_duration_sec) for the optimized sustainable power.
    """
    if not segments:
        return []

    # 1. Setup Variables
    lowest_conceivable_power_watts = 50.0  
    lower_bound_watts = lowest_conceivable_power_watts
    upper_bound_watts = lower_bound_watts

    # 2. Find Safe Upper Bound
    compute_iterations_performed = 0
    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH):
        simulated_total_duration_sec = calculate_route_time_for_constant_power(rider, segments, upper_bound_watts)
        
        # Guard against mathematically impossible infinite times on steep inclines at low bounds
        if simulated_total_duration_sec == float('inf'):
             max_power_for_duration = 0.0 # Force loop to increase watts if we can't move forward
        else:
             max_power_for_duration = rider.get_1_hour_curvefit_watts() if simulated_total_duration_sec > 864000 else decay_model_numpy(simulated_total_duration_sec, rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)

        # Did we push the guess power past what the rider is capable of for the time it took?
        if upper_bound_watts > max_power_for_duration:
            break
            
        upper_bound_watts += CHUNK_OF_WATTS_PER_ITERATION
        compute_iterations_performed += 1
    else:
        # Failsafe: if we max out iterations finding upper bound, return simple empty
        return []

    # 3. Binary Search
    while (upper_bound_watts - lower_bound_watts) > REQUIRED_PRECISION_OF_WATTS and compute_iterations_performed < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:
        mid_point_watts = safe_divide((lower_bound_watts + upper_bound_watts), 2)
        
        simulated_total_duration_sec = calculate_route_time_for_constant_power(rider, segments, mid_point_watts)
        
        if simulated_total_duration_sec == float('inf'):
            max_power_for_duration = 0.0
        else:
             max_power_for_duration = rider.get_1_hour_curvefit_watts() if simulated_total_duration_sec > 864000 else decay_model_numpy(simulated_total_duration_sec, rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)

        compute_iterations_performed += 1

        if mid_point_watts > max_power_for_duration:
            upper_bound_watts = mid_point_watts
        else:
            lower_bound_watts = mid_point_watts

    # 4. Final generation with the converged sustainable power guess (upper_bound is safest constraint)
    converged_power_watts = upper_bound_watts
    final_route_result: List[Tuple[float, float, float]] = []

    for distance_km, slope in segments:
        speed_kph = solve_for_speed_riding_solo(rider, converged_power_watts, slope)
        
        if speed_kph <= 0:
            final_route_result.append((distance_km, slope, float('inf')))
            continue
            
        segment_duration_sec = (distance_km * 1000.0) / (speed_kph / 3.6)
        final_route_result.append((distance_km, slope, segment_duration_sec))
        
    return final_route_result



