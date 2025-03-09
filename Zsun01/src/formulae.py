import logging
from jgh_logging import jgh_configure_logging
import numpy as np
from pydantic import BaseModel, Field
from enum import Enum

# Configure logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

# units of power (w) = watts
# units of velocity (v) = m/s
# height of cyclist (cm) = 183
# weight of cyclist (kg) = 75
# gender of cyclist (enum) m

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

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

class ZwiftInsiderRider(BaseModel):
    mass: float = 75
    height: float = 183
    gender: Gender = Gender.MALE
    ftp: float = 3.5  # Functional Threshold Power in watts per kilogram
    coefficient_of_drag: float = Field(init=False)
    frontal_area: float = Field(init=False)

    def __init__(self, **data):
        super().__init__(**data)
        self.coefficient_of_drag = estimate_coefficient_of_drag(self.mass, self.height)
        self.frontal_area = estimate_frontal_area(self.mass, self.height)

    def calculate_power(self, velocity: float) -> float:
        return calculate_power(velocity, self.coefficient_of_drag, self.frontal_area)

    def calculate_velocity(self, power: float) -> float:
        return calculate_velocity(power, self.coefficient_of_drag, self.frontal_area)

    def calculate_energy_from_power(self, power: float, duration: float) -> float:
        return calculate_energy_from_power(power, duration)

    def calculate_energy_from_velocity(self, velocity: float, duration: float) -> float:
        return calculate_energy_from_velocity(velocity, duration, self.coefficient_of_drag, self.frontal_area)

    def calculate_average_speed(self, total_distance: float, total_time: float) -> float:
        """
        Calculate the average speed given total distance and total time.
        
        Args:
        total_distance (float): The total distance in meters.
        total_time (float): The total time in seconds.
        
        Returns:
        float: The average speed in m/s.
        """
        return total_distance / total_time

    def calculate_total_distance(self, velocity: float, duration: float) -> float:
        """
        Calculate the total distance covered given velocity and duration.
        
        Args:
        velocity (float): The velocity in m/s.
        duration (float): The duration in seconds.
        
        Returns:
        float: The total distance in meters.
        """
        return velocity * duration

    def calculate_efficiency(self, power: float, energy: float) -> float:
        """
        Calculate the efficiency as the ratio of power output to energy consumption.
        
        Args:
        power (float): The power in watts.
        energy (float): The energy consumption in joules.
        
        Returns:
        float: The efficiency as a ratio.
        """
        return power / energy

    def calculate_power_to_weight_ratio(self, power: float) -> float:
        """
        Calculate the power-to-weight ratio.
        
        Args:
        power (float): The power in watts.
        
        Returns:
        float: The power-to-weight ratio in watts per kilogram.
        """
        return power / self.mass

class Ride(BaseModel):
    rider: ZwiftInsiderRider = ZwiftInsiderRider()
    distance: float = 40000  # Distance in meters

    def calculate_finishing_time(self, ftp_percentage: float) -> float:
        """
        Calculate the finishing time of the ride given the rider's FTP percentage.
        
        Args:
        ftp_percentage (float): The percentage of the rider's FTP to ride at.
        
        Returns:
        float: The finishing time in seconds.
        """
        # Calculate the power based on the FTP percentage
        power = self.rider.ftp * ftp_percentage * self.rider.mass

        # Calculate the velocity based on the power and drag
        velocity = self.rider.calculate_velocity(power)

        # Calculate the finishing time
        finishing_time = self.distance / velocity

        return finishing_time

    def calculate_average_speed(self, ftp_percentage: float) -> float:
        """
        Calculate the average speed for the ride as a whole.
        
        Args:
        ftp_percentage (float): The percentage of the rider's FTP to ride at.
        
        Returns:
        float: The average speed in meters per second.
        """
        # Calculate the finishing time
        finishing_time = self.calculate_finishing_time(ftp_percentage)

        # Calculate the average speed
        average_speed = self.distance / finishing_time

        return average_speed

    def calculate_total_energy_consumption(self, ftp_percentage: float) -> float:
        """
        Calculate the total energy consumption of the ride given the rider's FTP percentage.
        
        Args:
        ftp_percentage (float): The percentage of the rider's FTP to ride at.
        
        Returns:
        float: The total energy consumption in joules.
        """
        # Calculate the power based on the FTP percentage
        power = self.rider.ftp * ftp_percentage * self.rider.mass

        # Calculate the velocity based on the power and drag
        velocity = self.rider.calculate_velocity(power)

        # Calculate the finishing time
        finishing_time = self.distance / velocity

        # Calculate the total energy consumption
        total_energy_consumption = calculate_energy_from_power(power, finishing_time)

        return total_energy_consumption

    def calculate_energy_consumption_intensity(self, ftp_percentage: float) -> float:
        """
        Calculate the energy total energy consumption intensity as the ratio of the total energy consumption
        to the energy that would have been consumed at a constant average power of 100% of FTP.
        
        Args:
        ftp_percentage (float): The percentage of the rider's FTP to ride at.
        
        Returns:
        float: The energy total energy consumption intensity (dimensionless).
        """
        # Calculate the total energy consumption at the given FTP percentage
        total_energy_consumption = self.calculate_total_energy_consumption(ftp_percentage)

        # Calculate the power at 100% FTP
        power_at_100_ftp = self.rider.ftp * self.rider.mass

        # Calculate the velocity at 100% FTP
        velocity_at_100_ftp = self.rider.calculate_velocity(power_at_100_ftp)

        # Calculate the finishing time at 100% FTP
        finishing_time_at_100_ftp = self.distance / velocity_at_100_ftp

        # Calculate the energy consumption at 100% FTP
        energy_consumption_at_100_ftp = calculate_energy_from_power(power_at_100_ftp, finishing_time_at_100_ftp)

        # Calculate the energy total energy consumption intensity
        energy_total_energy_consumption_intensity = total_energy_consumption / energy_consumption_at_100_ftp

        return energy_total_energy_consumption_intensity


# Example usage
def main():
    # Create an instance of ZwiftInsiderRider with height=183, mass=75, gender=MALE, and ftp=3.5
    rider = ZwiftInsiderRider(mass=75, height=183, gender=Gender.MALE, ftp=3.5)
    ride = Ride(rider=rider, distance=40000)
    velocity = 10.0  # m/s
    power = rider.calculate_power(velocity)
    logger.info(f"Power for velocity {velocity} m/s: {power:.2f} W")

    power = 300  # W
    velocity = rider.calculate_velocity(power)
    logger.info(f"Velocity for power {power} W: {velocity:.2f} m/s")

    duration = 3600  # seconds (1 hour)
    energy = rider.calculate_energy_from_power(power, duration)
    logger.info(f"Energy for power {power} W over {duration} seconds: {energy:.2f} J")

    energy = rider.calculate_energy_from_velocity(velocity, duration)
    logger.info(f"Energy for velocity {velocity} m/s over {duration} seconds: {energy:.2f} J")

    power_to_weight_ratio = rider.calculate_power_to_weight_ratio(power)
    logger.info(f"Power-to-weight ratio for power {power} W: {power_to_weight_ratio:.2f} W/kg")

    logger.info(f"Ride distance: {ride.distance} meters")

    # Calculate the finishing time for the ride at 75% of the rider's FTP
    ftp_percentage = 0.75
    finishing_time = ride.calculate_finishing_time(ftp_percentage)
    logger.info(f"Finishing time for the ride at {ftp_percentage * 100}% of FTP: {finishing_time:.2f} seconds")

    # Calculate the total energy consumption for the ride at 75% of the rider's FTP
    total_energy_consumption = ride.calculate_total_energy_consumption(ftp_percentage)
    logger.info(f"Total energy consumption for the ride at {ftp_percentage * 100}% of FTP: {total_energy_consumption:.2f} joules")

    # Calculate the energy total energy consumption intensity for the ride at 75% of the rider's FTP
    energy_total_energy_consumption_intensity = ride.calculate_energy_total_energy_consumption_intensity(ftp_percentage)
    logger.info(f"Energy total energy consumption intensity for the ride at {ftp_percentage * 100}% of FTP: {energy_total_energy_consumption_intensity:.2f}")

    # Calculate the average speed for the ride at 75% of the rider's FTP
    average_speed = ride.calculate_average_speed(ftp_percentage)
    logger.info(f"Average speed for the ride at {ftp_percentage * 100}% of FTP: {average_speed:.2f} m/s")

if __name__ == "__main__":
    main()
