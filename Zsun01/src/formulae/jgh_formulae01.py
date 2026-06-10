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
- calculate_drag_ratio_in_paceline(position):
  Estimate the drag reduction factor for a rider's position.
  Compute energy expenditure in kilojoules.
- calculate_watts_from_speed(speed, weight, height, slope):
  Calculate required power for a given speed.
- solve_for_speed_from_wattage_using_binary_search(wattage, weight, height, slope):
  Estimate speed from rider wattage.

Notes:
------
- All calculations use SI units unless otherwise specified.
- Logging is disabled in functions called during parallel processing.

Example Usage:
--------------
    speed = solve_for_speed_from_wattage_using_binary_search(wattage=300, weight_kg=75, height_cm=183, slope_pc=0.0)
    watts = calculate_watts_from_speed(speed=40, weight_kg=75, height_cm=183, slope_pc=0.0)
    drag_factor = calculate_drag_ratio_in_paceline(3)
"""

import numpy as np
import warnings


from jgh_number import safe_divide
from jgh_power_curve_fit_models import decay_model_numpy

from constants import (
    COEFFICIENT_bike_weight_kg,
    AERO_POSITION_FACTOR_DEFAULT,
    DEFAULT_PACELINE_SLOPE_PC,
)
# from jgh_number import safe_divide

from jgh_formulae00 import calculate_power_from_velocity


def solve_for_velocity_from_power_using_binary_search(power_watts: float, height_cm: float, total_mass_kg: float, slope_pc: float, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Solve for the steady-state cycling velocity (km/h) at which a rider
    producing a specified constant power output (W) will travel, given
    the physical and environmental parameters of the rider and road.
    Defaults to a typical time-trial position for the 
    aero factor, which is not the same as the hoods position 
    or the supertuck position.


    Algorithm
    ---------
    Phase 1 – Upper bound scan:
        Start at 0 kph and step upward in fixed increments until
        calculate_power_from_velocity() first exceeds power_watts.
        That step becomes the upper bound for the binary search.

    Phase 2 – Binary search:
        Bisect [lower_bound_kph, upper_bound_kph] until the interval
        width is within REQUIRED_PRECISION_OF_SPEED_KPH.

    Args:
        power_watts (float):
            Target mechanical power output in watts (W).
        aero_factor (float):
            Dimensionless aerodynamic factor. 
            Defaults to a typical time-trial position.
        height_cm (float):
            Rider height in centimetres (cm).
        Crr (float):
            Dimensionless rolling resistance coefficient.
        total_mass_kg (float):
            Combined mass of rider and bicycle in kilograms (kg)..
        slope_pc (float):
            Road gradient as a % (rise / run).
            For example, 5 for a 5% climb, -5 for a 5% descent,
            0 for flat terrain.

    Returns:
        float: Steady-state velocity in kilometres per hour (km/h).

    Raises:
        ValueError: If Phase 1 fails to find an upper bound within
            SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND steps.
    """

    if (power_watts <= 0.0):
        return 0.0

    # 1. Find safe upper bound for binary search

    CHUNK_OF_KPH_PER_ITERATION = 20.0
    SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND = 30 

    lower_bound_kph: float = 0.0
    upper_bound_kph: float = 0.0

    for _ in range(SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND):
        upper_bound_kph += CHUNK_OF_KPH_PER_ITERATION
        if calculate_power_from_velocity(upper_bound_kph, height_cm=height_cm, total_mass_kg=total_mass_kg, slope_pc=slope_pc, aero_factor=aero_factor) > power_watts:
            break
        lower_bound_kph = upper_bound_kph 
    else:
        raise ValueError(
            f"solve_for_velocity_from_power_using_binary_search failed to find an upper bound "
            f"after {SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND} iterations "
            f"at {power_watts:.1f} W. Maximum speed scanned: {upper_bound_kph:.1f} kph."
        )

    # 2. Binary search

    REQUIRED_PRECISION_OF_SPEED_KPH = 0.05
    MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30

    binary_search_iterations: int = 0

    while (upper_bound_kph - lower_bound_kph) > REQUIRED_PRECISION_OF_SPEED_KPH and binary_search_iterations < MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION:
        mid_point_kph: float = (lower_bound_kph + upper_bound_kph) / 2.0
        binary_search_iterations += 1
        if calculate_power_from_velocity(mid_point_kph, height_cm=height_cm, total_mass_kg=total_mass_kg, slope_pc=slope_pc, aero_factor=aero_factor) > power_watts:
            upper_bound_kph = mid_point_kph
        else:
            lower_bound_kph = mid_point_kph

    if (upper_bound_kph - lower_bound_kph) > REQUIRED_PRECISION_OF_SPEED_KPH:
        warnings.warn(
            f"solve_for_velocity_from_power_using_binary_search hit the iteration cap "
            f"({MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION} iterations) without "
            f"achieving the required precision of {REQUIRED_PRECISION_OF_SPEED_KPH} kph. "
            f"Residual interval: {upper_bound_kph - lower_bound_kph:.5f} kph "
            f"at {power_watts:.1f} W, slope {slope_pc:.1f}%.",
            UserWarning,
            stacklevel=2,
        )

    # Return lower_bound: the highest speed provably achievable at power_watts.
    return lower_bound_kph


def solve_for_speed_from_wattage_using_binary_search(wattage: float, rider_weight: float, rider_height: float, slope_pc: float = DEFAULT_PACELINE_SLOPE_PC) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight (kg), height (cm), and slope (%)
    """

    rider_plus_bike_mass: float = rider_weight + COEFFICIENT_bike_weight_kg
    speed_kmh: float = solve_for_velocity_from_power_using_binary_search(wattage, rider_height, rider_plus_bike_mass, slope_pc)

    return speed_kmh


