
import numpy as np

from jgh_formulae01 import solve_for_speed_from_wattage_using_binary_search, calculate_watts_from_speed
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
    height_cm and weight_kg. Uses the binary search solver.

    Args:
    power (float): The power in watts.
    slope_pc (float): The slope in %.

    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_binary_search(power, rider.weight_kg, rider.height_cm, slope_pc)
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
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_proxy_30sec_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_1_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_proxy_1_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_2_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_proxy_2_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_3_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_proxy_3_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_standard_4_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_proxy_4_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
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
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_n_second_curvefit_y_ordinate_watts(seconds), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_speed_at_one_hour_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    speed_kph = solve_for_speed_from_wattage_using_binary_search(rider.get_1_hour_curvefit_watts(), rider.weight_kg, rider.height_cm, slope_pc)
        
    return speed_kph

def solve_for_fastest_achievable_time_by_rider_for_segment_using_binary_search(rider: RiderComputeItem, segment: SlopeBucketItem) -> float:
    """
    Calculate the duration in seconds for a rider to cover a given distance with a given slope,
    using their fitted 60-minute power-duration decay curve, using a binary search root-finder.

    Args:
        rider (RiderComputeItem): The rider whose curve coefficients are used.
        segment (SlopeBucketItem): The route segment object.

    Returns:
        float: The estimated duration in seconds. Returns 0.0 if the rider's
               curve has not been fitted or if the segment distance is nonsensical.
               Raises ValueError if the segment is physically impossible (stalls indefinitely).
    """
    decay_curve_coefficient: float = rider.jgh_60_min_curve_coefficient
    decay_curve_exponent: float = rider.jgh_60_min_curve_exponent

    # Guard: curve has not been fitted
    if decay_curve_coefficient == 0.0 or decay_curve_exponent == 0.0:
        return 0.0

    # Guard: nonsensical distance
    if segment.bucket_length_km <= 0.0:
        return 0.0

    lower_bound_sec: float = 1.0  # sub-1s durations aren't valid for decay formula
    upper_bound_sec: float = 0.0
    
    # 1. Phase 1 - Find an Upper Bound
    # Step duration upward until the distance covered exceeds the target distance.
    t_guess: float = 1.0
    MAX_PHASE_1_ITERATIONS = 50
    
    for _ in range(MAX_PHASE_1_ITERATIONS):
        watts = float(decay_model_numpy(np.array([t_guess]), decay_curve_coefficient, decay_curve_exponent)[0])
        
        try:
            speed_kph = solve_for_speed_from_wattage_using_binary_search(watts, rider.weight_kg, rider.height_cm, segment.bucket_slope_pc)
        except ValueError:
            speed_kph = 0.0

        if speed_kph <= 0:
            # We reached a duration where required power dropped so low the rider couldn't overcome gravity!
            # If they stall before covering the distance, completing this segment is physically impossible.
            raise ValueError(
                f"Rider {rider.zwift_id} {rider.name} stalled on segment (len: {segment.bucket_length_km:.2f}km, "
                f"slope: {segment.bucket_slope_pc:.1f}%). Segment duration exceeds their endurance curve capacity."
            )
            
        dist_km = speed_kph * (t_guess / 3600.0)
        
        if dist_km >= segment.bucket_length_km:
            upper_bound_sec = t_guess
            break
            
        lower_bound_sec = t_guess
        t_guess *= 2.0
    else:
        raise ValueError(f"Rider {rider.zwift_id} {rider.name} Phase 1 failed to bound the segment duration up to {t_guess}s.")

    # 2. Phase 2 - Binary Search
    REQUIRED_PRECISION_SEC = 0.1
    MAX_PHASE_2_ITERATIONS = 60
    
    iterations = 0
    while (upper_bound_sec - lower_bound_sec) > REQUIRED_PRECISION_SEC and iterations < MAX_PHASE_2_ITERATIONS:
        mid_sec = safe_divide((lower_bound_sec + upper_bound_sec), 2.0)
        iterations += 1
        
        watts = float(decay_model_numpy(np.array([mid_sec]), decay_curve_coefficient, decay_curve_exponent)[0])
        
        try:
            speed_kph = solve_for_speed_from_wattage_using_binary_search(watts, rider.weight_kg, rider.height_cm, segment.bucket_slope_pc)
        except ValueError:
            speed_kph = 0.0
            
        if speed_kph <= 0.0:
            # Rider stalls at `mid_sec`. Power is too low, so the time guess is TOO LONG. We must shorten it.
            upper_bound_sec = mid_sec
        else:
            dist_km = speed_kph * (mid_sec / 3600.0)
            if dist_km > segment.bucket_length_km:
                # We went too far. That means we don't need this much time.
                upper_bound_sec = mid_sec
            else:
                # We didn't travel far enough. We need to allow for more time (which drops power).
                lower_bound_sec = mid_sec

    # Return the upper bound to ensure a provably achievable physical time state.
    # (upper_bound_sec models slightly more time, producing slightly lower power,
    # ensuring the rider absolutely can complete the distance).
    return round(upper_bound_sec, 2)


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
        Each bucket is populated in-place using converged_power_watts (= lower_bound_watts):
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

    # 1. Find Safe Upper Bound for binary-search

    CHUNK_OF_WATTS_PER_ITERATION = 20.0 # arbitrary
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 40 # 800 W conservative

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):
        # Note: This mutates routeItem in-place. The implicit distance-correction hack inside 
        # this helper will execute securely on the first iteration and skip thereafter.
        simulated_route = solve_for_hypothetical_route_time_at_a_mandated_power(rider, routeItem, upper_bound_watts)
        
        # Did the rider stall (velocity <= 0) because gravity beat their power?
        if any(bucket.calculated_bucket_duration_sec == float('inf') for bucket in simulated_route.route_slope_buckets):
             pass # Stalled! The test power is simply too low. Loop must continue to increase watts.
        else:
             simulated_total_duration_sec = sum(bucket.calculated_bucket_duration_sec for bucket in simulated_route.route_slope_buckets)
             max_power_for_duration = float(decay_model_numpy(np.array([simulated_total_duration_sec]), rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)[0]) 
             
             # Did we push the guess power past what the rider is physically capable of for this duration?
             if upper_bound_watts > max_power_for_duration:
                 break
            
        upper_bound_watts += CHUNK_OF_WATTS_PER_ITERATION
    else:
        # Failsafe: if we max out iterations finding upper bound, return the routeItem as-is.
        return routeItem        

    # 2. Do binary-search.

    REQUIRED_PRECISION_OF_WATTS = 1.0 
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 40 # conservative?

    binary_search_iterations = 0

    while (upper_bound_watts - lower_bound_watts) > REQUIRED_PRECISION_OF_WATTS and binary_search_iterations < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:
        mid_point_watts = safe_divide((lower_bound_watts + upper_bound_watts), 2)
        
        simulated_route = solve_for_hypothetical_route_time_at_a_mandated_power(rider, routeItem, mid_point_watts)
        
        # Did the rider stall on this attempt?
        if any(bucket.calculated_bucket_duration_sec == float('inf') for bucket in simulated_route.route_slope_buckets):
            # Power is too low to overcome gravity. Raise the lower bound to search higher.
            lower_bound_watts = mid_point_watts
        else:
             simulated_total_duration_sec = sum(bucket.calculated_bucket_duration_sec for bucket in simulated_route.route_slope_buckets)
             max_power_for_duration = float(decay_model_numpy(np.array([simulated_total_duration_sec]), rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)[0]) 

             if mid_point_watts > max_power_for_duration:
                 upper_bound_watts = mid_point_watts
             else:
                 lower_bound_watts = mid_point_watts
                 
        binary_search_iterations += 1

   # 3. Populate final Route result with our solved maximum sustainable power boundary.
   # CRITICAL FIX: We must use the LOWER bound, representing a power output the rider can actually achieve.
    converged_power_watts = lower_bound_watts

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

