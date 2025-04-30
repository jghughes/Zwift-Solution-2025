from functools import lru_cache

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

@lru_cache(maxsize=128)
def estimate_power_factor_in_peloton(position: int) -> float:
    """
    Calculate the power factor based on the rider's
    position in the peloton. The leader's factor is 1.0.
    Follower's in the peloton are based on ZwiftInsider's
    power matrix.Their factors are less than 1.0, diminishing
    as they are further back in the peloton.

        ZwiftInsiderWattageMatrix = np.array([
            [300, 350, 400],
            [212, 252, 290],
            [196, 236, 261],
            [191, 217, 255]
        ])

    """
    default = 200 # Default power for unknown positions
    # Define the ZwiftInsider powers for each position in the 
    # peloton, choosing the 350W leader as the baseline.
    power_ratios: dict[int, int] = {
        1: 350,
        2: 252,
        3: 236,
        4: 217,
    }
    denominator = power_ratios.get(1, default)
    # Return the power ratio for the given position
    if position in power_ratios:
        return power_ratios.get(position, default) / denominator
    else:
        return power_ratios.get(4, default) / denominator

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

@lru_cache(maxsize=256)
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
    watts = 1.86e-02 * weight * kph - 5.37e-04 * kph**3 + 2.23e-05 * weight * kph**3 + 1.33e-05 * height * kph**3
    return round(watts, 3)

@lru_cache(maxsize=256)
def estimate_speed_from_wattage(wattage: float, weight: float, height: float) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.

    Args:
    wattage (float): The power in watts.
    weight (float): The weight in kg.
    height (float): The height in cm.

    Returns:
    float: The estimated speed in km/h.
    """
    # Initial guess for speed (km/h)
    v = 30.0
    m = weight

    # Tolerance and maximum iterations for the Newton-Raphson method
    tolerance = 1e-6
    max_iterations = 100

    for _ in range(max_iterations):
        # Calculate the function value at the current v
        f = 1.86e-02 * m * v - 5.37e-04 * v**3 + 2.23e-05 * m * v**3 + 1.33e-05 * height * v**3 - wattage

        # Calculate the function derivative at the current speed
        f_prime = 1.86e-02 * m - 3 * 5.37e-04 * v**2 + 3 * 2.23e-05 * m * v**2 + 3 * 1.33e-05 * height * v**2

        # Update the speed using the Newton-Raphson formula
        new_speed = v - f / f_prime

        # Check for convergence and return the speed if the tolerance is met
        if abs(new_speed - v) < tolerance:
            return round(new_speed, 2)

        # Update the speed for the next iteration
        v = new_speed

    # If the method did not converge, raise an error
    raise ValueError("Newton-Raphson method did not converge")

@lru_cache(maxsize=256)
def estimate_kilojoules_from_speed_and_time(kph: float, duration: float, weight: float, height: float) -> float:
    """
    Calculate the energy consumed in kilojoules given speed, duration, weight, and height.

    Args:
    speed (float): The speed in km/h.
    duration (float): The duration in seconds.
    weight (float): The weight in kg.
    height (float): The height in cm.

    Returns:
    float: The energy consumed in kilojoules.
    """
    # Estimate the power in watts
    power = estimate_watts_from_speed(kph, weight, height)

    # Calculate the energy consumed in kJ
    energy_kilojoules = estimate_kilojoules_from_wattage_and_time(power, duration)

    return round(energy_kilojoules, 3)

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
#     logger.info(f"estimate_power_factor_in_peloton cache info: {estimate_power_factor_in_peloton.cache_info()}")
#     logger.info(f"estimate_watts_from_speed cache info: {estimate_watts_from_speed.cache_info()}")
#     logger.info(f"estimate_speed_from_wattage cache info: {estimate_speed_from_wattage.cache_info()}")
#     logger.info(f"estimate_kilojoules_from_speed_and_time cache info: {estimate_kilojoules_from_speed_and_time.cache_info()}")

# if __name__ == "__main__":
#     main()
