import logging
from jgh_logging import jgh_configure_logging
import numpy as np

# Configure logging
jgh_configure_logging("appsettings.json")
logger= logging.getLogger(__name__)

# units of power (w) = watts
# units of velocity (v) = m/s
# coefficient of drag of cyclist (c) = 0.5
# frontal area of cyclist (a) = 0.5 m^2

# w = c * a * (v^3)


def estimate_coefficient_of_drag(mass: float, height: float) -> float:
    """
    Estimate the coefficient of drag (Cd) for a cyclist based on body mass and height.
    
    Args:
    mass (float): The body mass in kg.
    height (float): The height in cm.
    
    Returns:
    float: The estimated coefficient of drag (Cd).
    """
    # Convert height from cm to m
    height_m = height / 100
    
    # Estimate the coefficient of drag area (CdA) using the formula from Martin et al. (1998)
    cda = 0.2025 * (mass / height_m) ** 0.425
    
    # Estimate the frontal area (A) using the formula from Olds et al. (1993)
    a = 0.266 * (mass / height_m) ** 0.5
    
    # Calculate the coefficient of drag (Cd) as CdA / A
    cd = cda / a
    
    return cd

def estimate_frontal_area(mass: float, height: float) -> float:
    """
    Estimate the frontal area (A) for a cyclist based on body mass and height.
    
    Args:
    mass (float): The body mass in kg.
    height (float): The height in cm.
    
    Returns:
    float: The estimated frontal area (A) in m^2.
    """
    # Convert height from cm to m
    height_m = height / 100
    
    # Estimate the frontal area (A) using the formula from Olds et al. (1993)
    a = 0.266 * (mass / height_m) ** 0.5
    
    return a

def calculate_power(velocity: float, coefficient_of_drag: float, frontal_area: float) -> float:
    """
    Calculate the power given a velocity, coefficient of drag, and frontal area.
    
    Args:
    velocity (float): The velocity in m/s.
    coefficient_of_drag (float): The coefficient of drag.
    frontal_area (float): The frontal area in m^2.
    
    Returns:
    float: The calculated power in watts.
    """
    return coefficient_of_drag * frontal_area * (velocity ** 3)

def calculate_velocity(power: float, coefficient_of_drag: float, frontal_area: float) -> float:
    """
    Calculate the velocity given the power, coefficient of drag, and frontal area.
    
    Args:
    power (float): The power in watts.
    coefficient_of_drag (float): The coefficient of drag.
    frontal_area (float): The frontal area in m^2.
    
    Returns:
    float: The calculated velocity in m/s.
    """
    return (power / (coefficient_of_drag * frontal_area)) ** (1 / 3)

def calculate_energy_from_power(power: float, duration: float) -> float:
    """
    Calculate the energy consumption given power and duration.
    
    Args:
    power (float): The power in watts.
    duration (float): The duration in seconds.
    
    Returns:
    float: The energy consumption in joules.
    """
    return power * duration

def calculate_energy_from_velocity(velocity: float, duration: float, coefficient_of_drag: float, frontal_area: float) -> float:
    """
    Calculate the energy consumption given velocity, duration, coefficient of drag, and frontal area.
    
    Args:
    velocity (float): The velocity in m/s.
    duration (float): The duration in seconds.
    coefficient_of_drag (float): The coefficient of drag.
    frontal_area (float): The frontal area in m^2.
    
    Returns:
    float: The energy consumption in joules.
    """
    power = calculate_power(velocity, coefficient_of_drag, frontal_area)
    return calculate_energy_from_power(power, duration)

# Define the ZwiftInsiderWattageMatrix
ZwiftInsiderWattageMatrix = np.array([
    [300, 350, 400],
    [212, 252, 290],
    [196, 236, 261],
    [191, 217, 255]
])

# Define the ZwiftInsiderVelocityMatrix_kph (km/h)
ZwiftInsiderVelocityMatrix_kph = np.array([39.9, 42.2, 44.4])

# Convert the velocity matrix to m/s
ZwiftInsiderVelocityMatrix_ms = ZwiftInsiderVelocityMatrix_kph * 1000 / 3600


# Example usage

def main():
    logger.info("ZwiftInsiderWattageMatrix:")
    logger.info(ZwiftInsiderWattageMatrix)
    logger.info("ZwiftInsiderVelocityMatrix_kph:")
    logger.info(ZwiftInsiderVelocityMatrix_kph)
    logger.info("ZwiftInsiderVelocityMatrix_ms:")
    logger.info(ZwiftInsiderVelocityMatrix_ms)

    # # Create the velocity matrix with the same shape as ZwiftInsiderWattageMatrix
    velocity_matrix = np.tile(ZwiftInsiderVelocityMatrix_ms, (ZwiftInsiderWattageMatrix.shape[0], 1))
    logger.info("Velocity Matrix (m/s):")
    logger.info(velocity_matrix)


if __name__ == "__main__":
    main()

