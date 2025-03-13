def estimate__power_ratio_in_peloton(position: int) -> float:
    """
    Calculate the power ratio based on the rider's
    position in the peloton.
    """
    # ZwiftInsiderWattageMatrix = np.array([
    #     [300, 350, 400],
    #     [212, 252, 290],
    #     [196, 236, 261],
    #     [191, 217, 255]
    # ])

    # Define the ZwiftInsider power ratios for each position in the peloton
    denominator = 350
    power_ratios = {
        1: denominator/denominator,
        2: 252/denominator,
        3: 236/denominator,
        4: 217/denominator,
    }
    # Return the power ratio for the given position
    if position in power_ratios:
        return power_ratios.get(position, 1)
    else:
        return power_ratios.get(4,1)

def estimate_joules_from_wattage_and_time(wattage: float, duration: float) -> float:
    """
    Calculate the energy consumption given power and duration.
    
    Args:
    power (float): The power in watts.
    duration (float): The duration in seconds.
    
    Returns:
    float: The energy consumption in joules.
    """
    return wattage * duration

def estimate_wattage_from_speed(speed: float, weight: float, height: float) -> float:
    """
    Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

    https://julesandjames.blogspot.com/2021/04/speed-vs-power-in-zwift.html

    Args:
    weight (float): The rider's weight in kg.
    speed (float): The velocity in km/h.
    height (float): The rider's height in cm.
    
    Returns:
    float: The calculated power in watts.
    """
    P = 1.86e-02 * weight * speed - 5.37e-04 * speed**3 + 2.23e-05 * weight * speed**3 + 1.33e-05 * height * speed**3

    return round(P, 3)

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
    speed = 30.0

    # Tolerance and maximum iterations for the Newton-Raphson method
    tolerance = 1e-6
    max_iterations = 100

    for _ in range(max_iterations):
        # Calculate the function value at the current speed
        f = 1.86e-02 * weight * speed - 5.37e-04 * speed**3 + 2.23e-05 * weight * speed**3 + 1.33e-05 * height * speed**3 - wattage

        # Calculate the function derivative at the current speed
        f_prime = 1.86e-02 * weight - 3 * 5.37e-04 * speed**2 + 3 * 2.23e-05 * weight * speed**2 + 3 * 1.33e-05 * height * speed**2

        # Update the speed using the Newton-Raphson formula
        new_speed = speed - f / f_prime

        # Check for convergence and return the speed if the tolerance is met
        if abs(new_speed - speed) < tolerance:
            return round(new_speed,2)

        # Update the speed for the next iteration
        speed = new_speed

    # If the method did not converge, raise an error
    raise ValueError("Newton-Raphson method did not converge")

def estimate_kilojoules_from_speed_and_time(speed: float, duration: float, weight: float, height: float) -> float:
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
    power = estimate_wattage_from_speed(speed, weight, height)

    # Calculate the energy consumed in joules
    energy_joules = estimate_joules_from_wattage_and_time(power, duration)

    # Convert joules to kilojoules
    energy_kilojoules = energy_joules / 1000

    return round(energy_kilojoules, 3)


# Example usage
def main():
    # units of power (w) = watts
    # units of speed (kph) = kilometers per hour
    # units of velocity (v) = m/s
    # units of energy (kJ) = kilojoules
    # units of height (cm) = centimeters
    # units of weight (kg) = kilograms 

    # parameters for the power calculation
    #     name: Eric Schlange
    #     speed: float = 40 kph
    #     weight: float = 84.3
    #     height: float = 180
    #     ftp: float = 272  # Functional Threshold Power in watts

    import numpy as np

    import logging
    from jgh_logging import jgh_configure_logging

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Define the rider's name, speed, weight, and height
    name = "Eric Schlange"
    speed = 40.0
    weight = 84.3
    height = 180.0

    # Calculate the power based on the rider's weight, speed, and height
    power = estimate_wattage_from_speed(speed, weight, height)
    logger.info(f"Estimated power for {name} @ {speed} km/h   {weight} kg   {height} cm  := {power} watts")

    # Estimate the speed based on the rider's weight, power, and height
    estimated_speed = estimate_speed_from_wattage(power, weight, height)
    logger.info(f"Estimated speed for {name} @ {power} watts   {weight} kg   {height} cm  := {estimated_speed} km/h")

    # Define the speed matrix in km/h
    ZwiftInsiderSpeedMatrix_kph = np.array([39.9, 42.2, 44.4])

    # Calculate the power matrix based on the rider's weight, speed, and height
    power_matrix = np.array([estimate_wattage_from_speed(speed, weight, height) for speed in ZwiftInsiderSpeedMatrix_kph])

    # Log the results
    for speed, power in zip(ZwiftInsiderSpeedMatrix_kph, power_matrix):
        logger.info(f"Estimated power for {name} @ {speed} km/h   {weight} kg   {height} cm  := {power} watts")


if __name__ == "__main__":
    main()