import time
import numpy as np
import numba
from constants import POWER_CURVE_IN_PACELINE

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
    power (float): The power in watts.
    duration (float): The duration in seconds.
    
    Returns:
    float: The energy consumption in joules.
    """
    return wattage * duration/1_000


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
    return watts


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
            return new_speed
        v = new_speed

    raise ValueError("Newton-Raphson method did not converge")


def main01():
    kph = 40.0
    weight = 75.0
    height = 175.0
    iterations = 300000

    funcs = [
        ("estimate_watts_from_speed", estimate_watts_from_speed),
        # ("estimate_watts_from_speedV2", estimate_watts_from_speedV2),
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
    main01()