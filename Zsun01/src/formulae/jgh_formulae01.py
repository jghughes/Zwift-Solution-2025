"""
Cycling Paceline Utility Formulae
=================================

This module provides utility functions for cycling paceline analysis,
including speed, power, energy, and drag estimations. It leverages
core physics models and constants from the project to support
simulation and optimization of rider performance in a paceline.

Key Features:
-------------
- Triangulates speed, time, and distance for cycling segments.
- Estimates drag reduction ratios for riders in different paceline
  positions using ZwiftInsider's power matrix.
- Calculates energy expenditure in kilojoules from wattage and time.
- Computes required power for a given speed, weight, and height.
- Estimates steady-state speed from rider wattage, weight, and height.

Functions:
----------
- triangulate_speed_time_and_distance(kph, seconds, meters):
  Calculate the missing parameter given the other two.
- estimate_drag_ratio_in_paceline(position):
  Estimate the drag reduction factor for a rider's position.
- estimate_kilojoules_from_wattage_and_time(wattage, duration):
  Compute energy expenditure in kilojoules.
- estimate_watts_from_speed(kph, weight, height):
  Calculate required power for a given speed.
- estimate_speed_from_wattage(wattage, weight, height):
  Estimate speed from rider wattage.

Notes:
------
- All calculations use SI units unless otherwise specified.
- Logging is disabled in functions called during parallel processing.

Example Usage:
--------------
    speed = estimate_speed_from_wattage(300, 75, 183)
    watts = estimate_watts_from_speed(40, 75, 183)
    drag_factor = estimate_drag_ratio_in_paceline(3)
"""


from constants import (
    COEFFICIENT_Cd,
    COEFFICIENT_Crr,
    COEFFICIENT_gradient,
    POWER_CURVE_IN_PACELINE,
    COEFFICIENT_bike_weight_kg,
)
from jgh_formulae00 import frontal_area, solve_speed_from_power, solve_power_from_speed

# All of these functions are called during parallel processing. Logging forbidden

def triangulate_speed_time_and_distance(kph: float, seconds: float, meters: float) -> tuple[float, float, float]:
    """
    Calculate the missing parameter (speed, time, or distance) given the other two.

    Args:
    kph (float): The speed in kilometers per hour.
    seconds (float): The time in seconds.
    meters (float): The distance in meters.

    Returns:
    tuple: The calculated speed (km/h), time (seconds), and distance (meters), rounded to 3 decimal places.
    """
    # Check for invalid input values
    if kph < 0 or seconds < 0 or meters < 0:
        raise ValueError("None of the input parameters can be less than zero.")

    # Check that exactly one parameter is zero
    zero_count = sum([kph == 0, seconds == 0, meters == 0])
    if zero_count != 1:
        raise ValueError("One and only one parameter must be zero.")

    # Calculate the missing parameter
    if kph == 0:
        # Calculate speed in km/h
        kph = (meters / 1000.0) / (seconds / 3600.0)
    elif seconds == 0:
        # Calculate time in seconds
        seconds = (meters / 1000.0) / (kph / 3600.0)
    elif meters == 0:
        # Calculate distance in meters
        meters = (kph * 1000.0) / (3600.0 / seconds)

    # Round the results to 3 decimal places
    kph = kph
    seconds = seconds
    meters = meters

    return kph, seconds, meters

def estimate_drag_ratio_in_paceline(position: int) -> float:
    """
    Calculate the power factor based on the rider's position in the peloton.
    The leader's factor is 1.0. Follower's in the paceline are based on ZwiftInsider's
    power matrix. Their factors are less than 1.0, diminishing as they are further back.
    This function guards against index out of range errors if POWER_CURVE_IN_PACELINE is shorter than 8.
    """
    denominator = POWER_CURVE_IN_PACELINE[0]
    max_index = len(POWER_CURVE_IN_PACELINE) - 1
    # Clamp position to valid range (1 to len(POWER_CURVE_IN_PACELINE)), else use last_name available value
    if 1 <= position <= len(POWER_CURVE_IN_PACELINE):
        numerator = POWER_CURVE_IN_PACELINE[position - 1]
    else:
        numerator = POWER_CURVE_IN_PACELINE[max_index]  # Use last_name available value
    return numerator / denominator

def estimate_kilojoules_from_wattage_and_time(wattage: float, duration: float) -> float:
    """
    Calculate the energy consumption given power and duration.
    
    Args:
    power (float): The power in watts.
    duration (float): The duration in seconds.
    
    Returns:
    float: The energy consumption in joules.
    """
    return wattage * duration/1_000

def estimate_watts_from_speed(kph: float, weight: float, height: float) -> float:
    """
    Calculate the power (watts) as a function of speed (km/h), weight (kg), and height (cm).
    """

    rider_frontal_area: float = frontal_area(height, weight)
    rider_plus_bike_mass: float = weight + COEFFICIENT_bike_weight_kg
    watts = solve_power_from_speed(kph, COEFFICIENT_Cd, rider_frontal_area, COEFFICIENT_Crr, rider_plus_bike_mass, COEFFICIENT_gradient)

    return watts

def estimate_speed_from_wattage(wattage: float, weight: float, height: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm)
    """

    rider_frontal_area: float = frontal_area(height, weight)
    rider_plus_bike_mass: float = weight + COEFFICIENT_bike_weight_kg
    speed_kmh: float = solve_speed_from_power(wattage, COEFFICIENT_Cd, rider_frontal_area, COEFFICIENT_Crr, rider_plus_bike_mass, COEFFICIENT_gradient)

    return speed_kmh


