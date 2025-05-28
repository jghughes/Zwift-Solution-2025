import numpy as np
import numba
from constants import POWER_CURVE_IN_PACELINE

@numba.njit
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
        kph = (meters / 1000) / (seconds / 3600)
    elif seconds == 0:
        # Calculate time in seconds
        seconds = (meters / 1000) / (kph / 3600)
    elif meters == 0:
        # Calculate distance in meters
        meters = (kph * 1000) / (3600 / seconds)

    # Round the results to 3 decimal places
    kph = round(kph, 3)
    seconds = round(seconds, 3)
    meters = round(meters, 3)

    return kph, seconds, meters


@numba.njit
def estimate_drag_ratio_in_paceline(position: int) -> float:
    """
    Calculate the power factor based on the rider's position in the peloton.
    The leader's factor is 1.0. Follower's in the paceline are based on ZwiftInsider's
    power matrix. Their factors are less than 1.0, diminishing as they are further back.
    """
    denominator = POWER_CURVE_IN_PACELINE[0]  # 350.0
    # Clamp position to valid range (1-4), else use position 4 as fallback
    if 1 <= position <= 4:
        numerator = POWER_CURVE_IN_PACELINE[position - 1]
    else:
        numerator = POWER_CURVE_IN_PACELINE[3]  # Use position 4's value
    return numerator / denominator


@numba.njit
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


@numba.njit
def estimate_watts_from_speed(kph: float, weight: float, height: float) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

    https://julesandjames.blogspot.com/2021/04/speed-vs-power-in-zwift.html

    Args:
    weight (float): The rider's weight in kg.
    kph (float): The velocity in km/h.
    height (float): The rider's height in cm.
    
    Returns:
    float: The calculated power in watts.
    """
    kph3 = kph * kph * kph
    watts = 0.0186 * weight * kph + ( -0.000537 + 0.0000223 * weight + 0.0000133 * height ) * kph3 
    return round(watts, 3)


@numba.njit
def estimate_speed_from_wattage(wattage: float, weight: float, height: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.
    Optimized for speed by precomputing constants and reducing repeated calculations.
    """
    v = 30.0
    m = weight

    c1 = 1.86e-02 * m
    c2 = -5.37e-04
    c3 = 2.23e-05 * m
    c4 = 1.33e-05 * height

    tolerance = 1e-6
    max_iterations = 100

    for _ in range(max_iterations):
        v2 = v * v
        v3 = v2 * v

        f = c1 * v + c2 * v3 + c3 * v3 + c4 * v3 - wattage
        f_prime = c1 + 3 * (c2 + c3 + c4) * v2

        new_speed = v - f / f_prime

        if abs(new_speed - v) < tolerance:
            return round(new_speed, 2)
        v = new_speed

    raise ValueError("Newton-Raphson method did not converge")


# @numba.njit
# def estimate_kilojoules_from_speed_and_time(kph: float, duration: float, weight: float, height: float) -> float:
#     """
#     Calculate the energy consumed in kilojoules given speed, duration, weight, and height.

#     Args:
#     speed (float): The speed in km/h.
#     duration (float): The duration in seconds.
#     weight (float): The weight in kg.
#     height (float): The height in cm.

#     Returns:
#     float: The energy consumed in kilojoules.
#     """
#     # Estimate the power in watts
#     power = estimate_watts_from_speed(kph, weight, height)

#     # Calculate the energy consumed in kJ
#     energy_kilojoules = estimate_kilojoules_from_wattage_and_time(power, duration)

#     return round(energy_kilojoules, 3)

# Example usage
# def main():
#     # units of power (w) = watts
#     # units of speed (kph) = kilometers per hour
#     # units of velocity (v) = m/s
#     # units of energy (kJ) = kilojoules
#     # units of height (cm) = centimeters
#     # units of weight (kg) = kilograms 

#     # parameters for the power calculation
#     #     name: Eric Schlange
#     #     speed: float = 40 kph
#     #     weight: float = 84.3
#     #     height: float = 180
#     #     ftp: float = 272  # Functional Threshold Power in watts

#     # Configure logging
#     import logging
#     from jgh_logging import jgh_configure_logging
#     jgh_configure_logging("appsettings.json")
#     logger = logging.getLogger(__name__)

#     import numpy as np

#     # Define the input parameters
#     kph = 40.0
#     seconds = 0
#     meters = 4000.0

#     logger.info(f"Input parameters  = speed: {kph} km/h, time: {seconds} seconds, distance: {meters} meters")
#     kph, seconds, meters = triangulate_speed_time_and_distance(kph, seconds, meters)
#     logger.info(f"Output parameters = speed: {kph} km/h, time: {seconds} seconds, distance: {meters} meters")

#     # Define the rider's name, speed, weight, and height
#     name = "Eric Schlange"
#     speed = 40.0
#     weight = 84.3
#     height = 180.0

#     # Calculate the power based on the rider's weight, speed, and height
#     power = estimate_watts_from_speed(speed, weight, height)
#     logger.info(f"Estimated power for {name} @ {speed} km/h   {weight} kg   {height} cm  := {power} watts")

#     # Estimate the speed based on the rider's weight, power, and height
#     estimated_speed = estimate_speed_from_wattage(power, weight, height)
#     logger.info(f"Estimated speed for {name} @ {power} watts   {weight} kg   {height} cm  := {estimated_speed} km/h")

#     # Define the speed matrix in km/h
#     ZwiftInsiderSpeedMatrix_kph = np.array([39.9, 42.2, 44.4])

#     # Calculate the power matrix based on the rider's weight, speed, and height
#     power_matrix = np.array([estimate_watts_from_speed(speed, weight, height) for speed in ZwiftInsiderSpeedMatrix_kph])

#     # Log the results
#     for speed, power in zip(ZwiftInsiderSpeedMatrix_kph, power_matrix):
#         logger.info(f"Estimated power for {name} @ {speed} km/h   {weight} kg   {height} cm  := {power} watts")

#     # Log cache performance
#     logger.info(f"estimate_drag_ratio_in_paceline cache info: {estimate_drag_ratio_in_paceline.cache_info()}")
#     logger.info(f"estimate_watts_from_speed cache info: {estimate_watts_from_speed.cache_info()}")
#     logger.info(f"estimate_speed_from_wattage cache info: {estimate_speed_from_wattage.cache_info()}")
#     logger.info(f"estimate_kilojoules_from_speed_and_time cache info: {estimate_kilojoules_from_speed_and_time.cache_info()}")


import time


def test_speed_of_estimate_watts_from_speed_functions():
    kph = 40.0
    weight = 75.0
    height = 175.0
    iterations = 300000

    funcs = [
        ("estimate_watts_from_speed", estimate_watts_from_speed),
        ("estimate_watts_from_speedV2", estimate_watts_from_speedV2),
    ]

    for name, func in funcs:
        # Warm up JIT for numba functions
        func(kph, weight, height)
        start = time.perf_counter()
        for _ in range(iterations):
            func(kph, weight, height)
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.6f} seconds for {iterations} iterations")

if __name__ == "__main__":
    test_speed_of_estimate_watts_from_speed_functions()