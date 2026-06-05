
import numpy as np
# from numpy.typing import NDArray
from scipy.optimize import newton

from constants import INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH, REQUIRED_NEWTON_SOLVER_DISTANCE_PRECISION_KM
from jgh_formulae01 import solve_for_speed_from_wattage_using_newton, calculate_watts_from_speed
from jgh_number import safe_divide
from jgh_power_curve_fit_models import decay_model_numpy
from rider_compute_item import RiderComputeItem
from slope_bucket_item import SlopeBucketItem
from route_item import RouteItem

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

def solve_for_fastest_achievable_time_by_rider_for_segment_using_newton(rider: RiderComputeItem, segment: SlopeBucketItem) -> float:
    """
    Calculate the duration in seconds for a rider to cover a given distance with a given slope,
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
            * (duration_seconds / 3600.0) - segment.bucket_length_km = 0

    Args:
        rider (RiderComputeItem): The rider whose curve coefficients are used.
        segment (SlopeBucketItem): The route segment object containing bucket_length_km and bucket_slope_pc.

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
    if segment.bucket_length_km <= 0.0:
        return 0.0

    initial_estimate_of_root_sec: float = (segment.bucket_length_km / INITIAL_VELOCITY_GUESS_FOR_NEWTON_SOLVER_KPH) * 3600.0 

    def distance_residual_km(duration_seconds: float) -> float:
        if duration_seconds < 1.0:
            duration_seconds = 1.0  # clamp: decay_model_numpy requires xdata >= 1; sub-1s durations are non-physical anyway

        watts: float = float(decay_model_numpy(np.array([duration_seconds]), decay_curve_coefficient, decay_curve_exponent)[0])
        speed_kph: float = solve_for_speed_from_wattage_using_newton(watts, rider.weight_kg, rider.height_cm, segment.bucket_slope_pc)
        return speed_kph * (duration_seconds / 3600.0) - segment.bucket_length_km

    try:
        duration_seconds: float = newton(distance_residual_km, initial_estimate_of_root_sec, tol=REQUIRED_NEWTON_SOLVER_DISTANCE_PRECISION_KM)
        # print(f"solve_for_fastest_achievable_time_by_rider_for_segment_using_newton : rider {rider.zwift_id} {rider.name} distanceKm={segment.bucket_length_km:.2f} km, initial_guess={initial_estimate_of_root_sec:.2f} sec, calculated_duration={duration_seconds:.2f} sec")
    except RuntimeError as e:
        raise ValueError(f"rider {rider.zwift_id} {rider.name} encountered a problem. solve_for_fastest_achievable_time_by_rider_for_segment_using_newton failed to converge: {e}") from e

    if duration_seconds <= 0.0:
        raise ValueError(f"rider {rider.zwift_id} {rider.name} Solver returned non-physical duration: {duration_seconds:.4f} seconds")

    return duration_seconds

def solve_for_hypothetical_route_time_at_a_mandated_power(rider: RiderComputeItem, route: RouteItem, power_watts: float) -> RouteItem:
    """
    Calculate the total duration (in seconds) to ride a route at a 
    constant mandated power.
    
    Args:
        rider (RiderComputeItem): The rider attempting the route.
        route (RouteItem): The route defined as a RouteItem object containing a list of buckets.
        power_watts (float): The constant wattage to maintain over the route.
        
    Returns:
        RouteItem: The same RouteItem object, with each bucket mutated to carry
            calculated_bucket_watts, calculated_bucket_speed_kph, and calculated_bucket_duration_sec.
    """
    # before doing anything else, we need to do a hack. if the total distance of the buckets is less than the total length of the route
    # (which is ordinarily well be), add the residual distance to the 0% slope bucket - creating a 0% bucket if there isn't one
    # 
    
    candidate_distance_km : float =  sum(bucket.bucket_length_km for bucket in route.route_slope_buckets)

    if (candidate_distance_km < route.lead_in_length_km + route.route_length_km):
        residual_distance = route.lead_in_length_km + route.route_length_km - candidate_distance_km

        #  DO a hack to deal with the fact that the route data is imperfect on https://veloviewer.com/segments but it the best we have.
        #  This code adds a 0% slope bucket with the residual distance if the total distance of the buckets is less than the total length of the route.
        zero_slope_bucket = next((bucket for bucket in route.route_slope_buckets if bucket.bucket_slope_pc == 0.0), None)
        if zero_slope_bucket:
            zero_slope_bucket.bucket_length_km += residual_distance
        else:
            route.route_slope_buckets.append(SlopeBucketItem(bucket_description="residual 0% bucket", bucket_length_km=residual_distance, bucket_slope_pc=0.0))

    for bucket in route.route_slope_buckets:
        speed_kph = solve_for_hypothetical_speed_of_rider_at_given_power(rider, power_watts, bucket.bucket_slope_pc)
        
        # Guard against zero or negative speeds breaking the duration math
        if speed_kph <= 0:
            bucket.calculated_bucket_watts = power_watts
            bucket.calculated_bucket_speed_kph = 0.0
            bucket.calculated_bucket_duration_sec = float('inf')
            return route   # early-out: inf duration flags this route as infeasible to the caller
    
        speed_meters_per_second = speed_kph / 3.6
        distance_meters = bucket.bucket_length_km * 1000.0
        
        segment_duration_sec = distance_meters / speed_meters_per_second

        bucket.calculated_bucket_watts = power_watts
        bucket.calculated_bucket_speed_kph = speed_kph
        bucket.calculated_bucket_duration_sec = segment_duration_sec
    
    return route

def solve_for_fastest_achievable_time_by_rider_for_route_using_binary_search(rider: RiderComputeItem, routeItem: RouteItem) -> RouteItem:
    """
    Finds the highest constant power output the rider can just barely sustain over a
    multi-bucket route, populates each bucket with the resulting watts, speed, and
    duration, and returns the mutated RouteItem.

    ...

    Final population:
        Each bucket is populated in-place using converged_power_watts (= upper_bound_watts):
            calculated_bucket_watts         rounded to 1 decimal place (W)
            calculated_bucket_speed_kph     rounded to 2 decimal places (kph)
            calculated_bucket_duration_sec  rounded to 1 decimal place (sec)
        If the computed speed for a bucket is zero or negative,
        calculated_bucket_speed_kph is set to 0.0 and calculated_bucket_duration_sec to inf.

    Args:
        rider (RiderComputeItem): The rider, supplying weight_kg, height_cm, and the
            fitted decay-curve coefficients jgh_60_min_curve_coefficient and
            jgh_60_min_curve_exponent.
        routeItem (RouteItem): The route, supplying an ordered list of buckets (SlopeBucketItem),
            each supplying bucket_length_km and bucket_slope_pc.

    Returns:
        RouteItem: The same RouteItem object, with each bucket mutated to carry
            calculated_bucket_watts, calculated_bucket_speed_kph, and calculated_bucket_duration_sec.
            Returns the unmodified routeItem if route_slope_buckets is empty.
            Returns the unmodified routeItem if Phase 1 exhausts its iteration cap
            without finding an upper bound.
    """
    if not routeItem.route_slope_buckets:
        return routeItem

    # Get ready
    lower_bound_watts = 5.0 # arbitrary small number to avoid zero-watt edge case in Phase 1
    upper_bound_watts = lower_bound_watts
    max_power_for_duration: float = 0.0

    # 1. Find Safe Upper Bound for binary-search

    CHUNK_OF_WATTS_PER_ITERATION = 20.0 # arbitrary
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 40 # 800 W . conservative

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):

        simulated_route = solve_for_hypothetical_route_time_at_a_mandated_power(rider, routeItem, upper_bound_watts)
        
        if any(bucket.calculated_bucket_duration_sec == float('inf') for bucket in simulated_route.route_slope_buckets):
             max_power_for_duration = 0.0 # Force loop to increase watts if we can't move forward
        else:
             simulated_total_duration_sec = sum(bucket.calculated_bucket_duration_sec for bucket in simulated_route.route_slope_buckets)
             max_power_for_duration = float(decay_model_numpy(np.array([simulated_total_duration_sec  ]), rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)[0]) 
             
        # Did we push the guess power past what the rider is capable of for the time it took?
        if upper_bound_watts > max_power_for_duration:
            break
            
        upper_bound_watts += CHUNK_OF_WATTS_PER_ITERATION
    else:
        # Failsafe: if we max out iterations finding upper bound, return the unmodified routeItem
        return routeItem        

    # 2. Do binary-search.

    REQUIRED_PRECISION_OF_WATTS = 1.0 
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 40 # conservative?

    binary_search_iterations = 0

    while (upper_bound_watts - lower_bound_watts) > REQUIRED_PRECISION_OF_WATTS and binary_search_iterations < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:
        mid_point_watts = safe_divide((lower_bound_watts + upper_bound_watts), 2)
        
        simulated_route = solve_for_hypothetical_route_time_at_a_mandated_power(rider, routeItem, mid_point_watts)
        
        if any(bucket.calculated_bucket_duration_sec == float('inf') for bucket in simulated_route.route_slope_buckets):
            max_power_for_duration = 0.0
        else:
             simulated_total_duration_sec = sum(bucket.calculated_bucket_duration_sec for bucket in simulated_route.route_slope_buckets)
             max_power_for_duration = float(decay_model_numpy(np.array([simulated_total_duration_sec  ]), rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)[0]) 

        binary_search_iterations += 1

        if mid_point_watts > max_power_for_duration:
            upper_bound_watts = mid_point_watts
        else:
            lower_bound_watts = mid_point_watts

   # 3. Populate final Route result with our solved maximum sustainable power boundary
    converged_power_watts = upper_bound_watts

    for bucket in routeItem.route_slope_buckets:
        speed_kph = solve_for_hypothetical_speed_of_rider_at_given_power(rider, converged_power_watts, bucket.bucket_slope_pc)
        bucket.calculated_bucket_watts = round(converged_power_watts, 1)
        if speed_kph <= 0:
            bucket.calculated_bucket_speed_kph = 0.0
            bucket.calculated_bucket_duration_sec = float('inf')
        else:
            duration_sec = (bucket.bucket_length_km * 1000.0) / (speed_kph / 3.6)
            bucket.calculated_bucket_duration_sec = round(duration_sec, 1)
            bucket.calculated_bucket_speed_kph = round(speed_kph, 2)

    return routeItem


