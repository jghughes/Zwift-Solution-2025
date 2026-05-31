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
- estimate_drag_ratio_in_paceline(position):
  Estimate the drag reduction factor for a rider's position.
- estimate_kilojoules_from_wattage_and_time(wattage, duration):
  Compute energy expenditure in kilojoules.
- estimate_watts_from_speed(kph, weight, height, slope):
  Calculate required power for a given speed.
- solve_for_speed_from_wattage(wattage, weight, height, slope):
  Estimate speed from rider wattage.

Notes:
------
- All calculations use SI units unless otherwise specified.
- Logging is disabled in functions called during parallel processing.

Example Usage:
--------------
    speed = solve_for_speed_from_wattage(300, 75, 183, 0.0)
    watts = estimate_watts_from_speed(40, 75, 183, 0.0)
    drag_factor = estimate_drag_ratio_in_paceline(3)
"""


from constants import (
    COEFFICIENT_Cd,
    COEFFICIENT_Crr,
    POWER_CURVE_IN_PACELINE,
    COEFFICIENT_bike_weight_kg,
)
from jgh_formulae00 import calculate_frontal_area, solve_for_velocity_from_power, calculate_power_from_velocity

# All of these functions are called during parallel processing. Logging forbidden

def estimate_drag_ratio_in_paceline(position: int) -> float:
    """
    Calculate the power factor based on the rider's position in the peloton.
    The leader's factor is 1.0. Follower's in the paceline are based on ZwiftInsider's
    power matrix. Their factors are less than 1.0, diminishing as they are further back.
    This function guards against index out of range errors if POWER_CURVE_IN_PACELINE is shorter than 8.
    """
    denominator = POWER_CURVE_IN_PACELINE[0]
    max_index = len(POWER_CURVE_IN_PACELINE) - 1
    # Clamp position to valid range (1 to len(POWER_CURVE_IN_PACELINE)), else use last available value
    if 1 <= position <= len(POWER_CURVE_IN_PACELINE):
        numerator = POWER_CURVE_IN_PACELINE[position - 1]
    else:
        numerator = POWER_CURVE_IN_PACELINE[max_index]  # Use last available value
    return numerator / denominator

def estimate_kilojoules_from_wattage_and_time(wattage: float, duration: float) -> float:
    """
    Calculate the energy consumption given power and duration.
    
    Args:
    wattage (float): The power in watts.
    duration (float): The duration in seconds.
    
    Returns:
    float: The energy consumption in kilojoules.
    """
    return wattage * duration/1_000

def estimate_watts_from_speed(kph: float, weight: float, height: float, slope: float) -> float:
    """
    Calculate the power (watts) as a function of speed (km/h), weight (kg), height (cm), slope (fraction).
    """

    rider_frontal_area: float = calculate_frontal_area(height, weight)
    rider_plus_bike_mass: float = weight + COEFFICIENT_bike_weight_kg
    watts = calculate_power_from_velocity(kph, COEFFICIENT_Cd, rider_frontal_area, COEFFICIENT_Crr, rider_plus_bike_mass, slope)

    return watts

def solve_for_speed_from_wattage(wattage: float, weight: float, height: float, slope: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight (kg), height (cm), and slope (fraction)
    """

    rider_frontal_area: float = calculate_frontal_area(height, weight)
    rider_plus_bike_mass: float = weight + COEFFICIENT_bike_weight_kg
    speed_kmh: float = solve_for_velocity_from_power(wattage, COEFFICIENT_Cd, rider_frontal_area, COEFFICIENT_Crr, rider_plus_bike_mass, slope)

    return speed_kmh


