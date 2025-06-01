from zsun_rider_item import ZsunRiderItem
from jgh_formulae01 import estimate_speed_from_wattage, estimate_watts_from_speed, estimate_drag_ratio_in_paceline

def calculate_kph_riding_alone(rider : ZsunRiderItem, power: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight_kg (kg), and 
    height_cm (cm) using the Newton-Raphson method.

    Args:
    power (float): The power in watts.

    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(power, rider.weight_kg, rider.height_cm)
    return speed_kph

def calculate_wattage_riding_alone(rider : ZsunRiderItem, speed: float) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), weight_kg (kg), and 
    height_cm (cm).

    Args:
    speed (float): The speed in km/h.

    Returns:
    float: The calculated power in watts.
    """
    # Calculate the power using the estimate_watts_from_speed function
    power = estimate_watts_from_speed(speed, rider.weight_kg, rider.height_cm)
    return power

def calculate_wattage_riding_in_the_paceline(rider : ZsunRiderItem, speed: float, position: int
) -> float:
    """
    Calculate the wattage required for a rider given their speed and position 
    in the peloton.

    Args:
    rider (ZsunRiderItem): The rider object.
    speed (float): The speed in km/h.
    position (int): The position in the peloton.

    Returns:
    float: The required wattage in watts.
    """
    # Calculate the base power required for the given speed
    base_power = calculate_wattage_riding_alone(rider, speed)

    # Get the power factor based on the rider's position in the peloton
    power_factor = estimate_drag_ratio_in_paceline(position)

    # Adjust the power based on the power factor
    adjusted_power = base_power * power_factor

    return round(adjusted_power, 3)

def calculate_speed_riding_in_the_paceline(rider : ZsunRiderItem, power: float, position: int
) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    and position in the peloton.

    Args:
    power (float): The power output in watts.
    position (int): The position in the peloton.

    Returns:
    float: The estimated speed in km/h.
    """
    # Get the power factor based on the rider's position in the peloton
    power_factor = estimate_drag_ratio_in_paceline(position)

    # Adjust the power based on the power factor
    adjusted_watts = power / power_factor

    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(adjusted_watts, rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_30sec_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 30-second pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_30sec_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_1_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 1-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_1_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_2_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 2-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_2_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_3_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 3-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_3_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_standard_4_minute_pull_watts(rider : ZsunRiderItem) -> float:
    """
    Calculate the speed (km/h) for a rider given their 4-minute pull power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_standard_4_minute_pull_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_n_second_watts(rider : ZsunRiderItem, seconds: float) -> float:
    """
    Calculate the speed (km/h) for a rider given their power output (watts) 
    for a specific duration in seconds.
    Args:
    seconds (float): The duration in seconds.
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_n_second_watts(seconds), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)

def calculate_speed_at_one_hour_watts(rider : ZsunRiderItem) -> float: 
    """
    Calculate the speed (km/h) for a rider given their one-hour power output (watts).
    Returns:
    float: The estimated speed in km/h.
    """
    # Estimate the speed in km/h using the estimate_speed_from_wattage function
    speed_kph = estimate_speed_from_wattage(rider.get_1_hour_watts(), rider.weight_kg, rider.height_cm)
        
    return round(speed_kph, 3)


