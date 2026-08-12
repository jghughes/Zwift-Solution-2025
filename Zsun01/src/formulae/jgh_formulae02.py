import numpy as np
from constants import AERO_POSITION_FACTOR_DEFAULT

from jgh_power_curve_fit_models import decay_model_numpy
from jgh_number import safe_divide


from jgh_formulae01 import calculate_rider_kph_from_watts
from rider_compute_item import RiderComputeItem
from route_item import RouteItem, SlopeBucketItem


# All of the following functions are called during parallel processing. Logging forbidden

def solve_for_speed_at_standard_30sec_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    """
    speed_kph = calculate_rider_kph_from_watts(rider.get_proxy_30sec_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def solve_for_speed_at_standard_1_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    """
    speed_kph = calculate_rider_kph_from_watts(rider.get_proxy_1_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def solve_for_speed_at_standard_2_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    """
    speed_kph = calculate_rider_kph_from_watts(rider.get_proxy_2_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def solve_for_speed_at_standard_3_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    """
    speed_kph = calculate_rider_kph_from_watts(rider.get_proxy_3_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def solve_for_speed_at_standard_4_minute_pull_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    """
    speed_kph = calculate_rider_kph_from_watts(rider.get_proxy_4_minute_pull_watts(), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def solve_for_speed_at_n_second_watts(rider : RiderComputeItem, seconds: float, slope_pc: float = 0.0) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    for a specific duration in seconds.
  """
    speed_kph = calculate_rider_kph_from_watts(rider.get_n_second_curvefit_y_ordinate_watts(seconds), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def solve_for_speed_at_one_hour_watts(rider : RiderComputeItem, slope_pc: float = 0.0) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    """
    speed_kph = calculate_rider_kph_from_watts(rider.get_1_hour_curvefit_watts(), rider.weight_kg, rider.height_cm, slope_pc, AERO_POSITION_FACTOR_DEFAULT)
    return speed_kph

def _calculate_route_duration_at_constant_power(rider: RiderComputeItem, route: RouteItem, power: float) -> RouteItem:
    """
    Calculate the total duration (in seconds) to ride a route at a 
    constant mandated power.
    
    Args:
        rider (RiderComputeItem): The rider attempting the route.
        route (RouteItem): The route defined as a RouteItem object containing a list of buckets.
        power (float): The constant wattage to maintain over the route.
        
    Returns:
        RouteItem: The same RouteItem object, with each bucket mutated to carry
            calculated_bucket_watts, calculated_bucket_speed_kph, and calculated_bucket_duration_sec.
    """
    # before doing anything else, we need to do a hack. if the total distance of the buckets is less than the total length of the route
    # (which it ordinarily well be), add the residual distance to the 0% slope bucket - creating a 0% bucket if there isn't one
    
    candidate_distance_km : float =  sum(bucket.bucket_length_km for bucket in route.route_slope_buckets)

    if (candidate_distance_km < route.route_lead_in_km + route.route_length_km):
        residual_distance: float = route.route_lead_in_km + route.route_length_km - candidate_distance_km

        #  DO a hack to deal with the fact that the route data is imperfect on https://veloviewer.com/segments but it the best we have.
        #  This code adds a 0% slope bucket with the residual distance if the total distance of the buckets is less than the total length of the route.
        zero_slope_bucket: SlopeBucketItem | None = next((bucket for bucket in route.route_slope_buckets if bucket.bucket_slope_pc == 0.0), None)
        if zero_slope_bucket:
            zero_slope_bucket.bucket_length_km += residual_distance
        else:
            route.route_slope_buckets.append(SlopeBucketItem(bucket_description="residual 0% bucket", bucket_length_km=residual_distance, bucket_slope_pc=0.0))

    for bucket in route.route_slope_buckets:
        speed_kph: float = calculate_rider_kph_from_watts(power, rider.weight_kg, rider.height_cm, bucket.bucket_slope_pc, AERO_POSITION_FACTOR_DEFAULT)

        # Guard against zero or negative speeds breaking the duration math
        if speed_kph <= 0:
            bucket.calculated_bucket_watts = power
            bucket.calculated_bucket_speed_kph = 0.0
            bucket.calculated_bucket_duration_sec = float('inf')
            return route   # early-out: inf duration flags this route as infeasible to the caller

        speed_meters_per_second: float = speed_kph / 3.6
        distance_meters: float = bucket.bucket_length_km * 1000.0

        segment_duration_sec: float = distance_meters / speed_meters_per_second

        bucket.calculated_bucket_watts = power
        bucket.calculated_bucket_speed_kph = speed_kph
        bucket.calculated_bucket_duration_sec = segment_duration_sec
    
    return route

def solve_for_route_duration_at_constant_90_day_best_using_binary_search(rider: RiderComputeItem, routeItem: RouteItem, intensity_factor: float = 1.0) -> RouteItem:
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
        intensity_factor (float): The factor to apply to the rider's best 90-day power 
        for the duration of the route.
    """
    if not routeItem.route_slope_buckets:
        return routeItem

    if(rider.jgh_60_min_curve_coefficient <= 0.0 or rider.jgh_60_min_curve_exponent <= 0.0):
        return routeItem

    # Get ready
    lower_bound_watts = 0.0 
    upper_bound_watts = lower_bound_watts

    # 1. Find Safe Upper Bound for binary-search

    CHUNK_OF_WATTS_PER_ITERATION = 20.0 # arbitrary
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 40 # 800 W conservative

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):
        # Note: This mutates routeItem in-place.
        simulated_route = _calculate_route_duration_at_constant_power(rider, routeItem, upper_bound_watts)
        
        # Did the rider stall (velocity <= 0) because gravity beat their power?
        if any(bucket.calculated_bucket_duration_sec == float('inf') for bucket in simulated_route.route_slope_buckets):
             pass # Stalled! The test power is simply too low. Loop must continue to increase watts.
        else:
             simulated_total_duration_sec = sum(bucket.calculated_bucket_duration_sec for bucket in simulated_route.route_slope_buckets)
             best_90_day_power_for_duration = float(decay_model_numpy(np.array([simulated_total_duration_sec]), rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)[0]) 
             
             # Did we push the guess power past what the rider is physically capable of for this duration?
             if upper_bound_watts > best_90_day_power_for_duration * intensity_factor:
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
        simulated_route = _calculate_route_duration_at_constant_power(rider, routeItem, mid_point_watts)
        
        # Did the rider stall on this attempt?
        if any(bucket.calculated_bucket_duration_sec == float('inf') for bucket in simulated_route.route_slope_buckets):
            # Power is too low to overcome gravity. Raise the lower bound to search higher.
            lower_bound_watts = mid_point_watts
        else:
             simulated_total_duration_sec = sum(bucket.calculated_bucket_duration_sec for bucket in simulated_route.route_slope_buckets)
             best_90_day_power_for_duration = float(decay_model_numpy(np.array([simulated_total_duration_sec]), rider.jgh_60_min_curve_coefficient, rider.jgh_60_min_curve_exponent)[0]) 
             target_power_for_duration =best_90_day_power_for_duration * intensity_factor
             if mid_point_watts > target_power_for_duration:
                 upper_bound_watts = mid_point_watts
             else:
                 lower_bound_watts = mid_point_watts
                 
        binary_search_iterations += 1

   # 3. Populate final Route result with our solved maximum sustainable power boundary.
   #    We must use the LOWER bound, representing a power output the rider can actually achieve.
    for bucket in routeItem.route_slope_buckets:
        speed_kph: float = calculate_rider_kph_from_watts(lower_bound_watts,rider.weight_kg, rider.height_cm, bucket.bucket_slope_pc, AERO_POSITION_FACTOR_DEFAULT)
        bucket.calculated_bucket_watts = round(lower_bound_watts, 1)
        if speed_kph <= 0:
            bucket.calculated_bucket_speed_kph = 0.0
            bucket.calculated_bucket_duration_sec = float('inf')
        else:
            duration_sec: float = (bucket.bucket_length_km * 1000.0) / (speed_kph / 3.6)
            bucket.calculated_bucket_duration_sec = round(duration_sec, 1)
            bucket.calculated_bucket_speed_kph = round(speed_kph, 2)

    return routeItem


