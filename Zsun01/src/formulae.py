import logging
from jgh_logging import jgh_configure_logging
from pydantic import BaseModel
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

def estimate_coefficient_of_drag(mass: float, height: float, gender: Gender) -> float:
    """
    Estimate the coefficient of drag (Cd) for a cyclist based on body mass and height.
    
    Args:
    mass (float): The body mass in kg.
    height (float): The height in cm.
    gender (enum) : male or female
    
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

def estimate_frontal_area(mass: float, height: float, gender : Gender) -> float:
    """
    Estimate the frontal area (A) for a cyclist based on body mass and height.
    
    Args:
    mass (float): The body mass in kg.
    height (float): The height in cm.
    gender (enum) : male or female

    Returns:
    float: The estimated frontal area (A) in m^2.
    """
    # Convert height from cm to m
    height_m = height / 100
    
    # Estimate the frontal area (A) using the formula from Olds et al. (1993)
    a = 0.266 * (mass / height_m) ** 0.5
    
    return a

def estimate_wattage_from_speed(speed: float, coefficient_of_drag: float, frontal_area: float) -> float:
    """
    Estimate the power given a velocity, coefficient of drag, and frontal area.
    
    Args:
    velocity (float): The velocity in m/s.
    coefficient_of_drag (float): The coefficient of drag.
    frontal_area (float): The frontal area in m^2.
   
    Returns:
    float: The estimated power in watts.
    """
    return coefficient_of_drag * frontal_area * (speed ** 3)

def estimate_speed_from_wattage(wattage: float, coefficient_of_drag: float, frontal_area: float) -> float:
    """
    Calculate the velocity given the power, coefficient of drag, and frontal area.
    
    Args:
    power (float): The power in watts.
    coefficient_of_drag (float): The coefficient of drag.
    frontal_area (float): The frontal area in m^2.
    
    Returns:
    float: The calculated velocity in m/s.
    """
    return (wattage / (coefficient_of_drag * frontal_area)) ** (1 / 3)

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

def estimate_joules_from_speed_and_time(speed: float, duration: float, coefficient_of_drag: float, frontal_area: float) -> float:
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
    power = estimate_wattage_from_speed(speed, coefficient_of_drag, frontal_area)
    return estimate_joules_from_wattage_and_time(power, duration)

class Rider(BaseModel):
    zwiftid: int = 0  # Zwift ID of the rider
    name: str = ""  # Name of the rider
    mass: float = 75
    height: float = 183
    gender: Gender = Gender.MALE
    ftp: float = 3.5  # Functional Threshold Power in watts per kilogram
    zwift_racing_score: int = 500  # Zwift racing score
    velo_rating: int = 1200  # Velo rating

    class Config:
        json_schema_extra = {
            "example": {
                "zwiftid": 0,
                "name": "John Doe",
                "mass": 75,
                "height": 183,
                "gender": "male",
                "ftp": 3.5,
                "zwift_racing_score": 500,
                "velo_rating": 1200
            },
            "description": {
                "zwiftid": "The Zwift ID of the rider",
                "name": "The name of the rider",
                "mass": "The mass of the rider in kilograms",
                "height": "The height of the rider in centimeters",
                "gender": "The gender of the rider",
                "ftp": "Functional Threshold Power in watts per kilogram",
                "zwift_racing_score": "Zwift racing score",
                "velo_rating": "Velo rating"
            },
            "validation": {
                "zwiftid": "Must be a non-negative integer",
                "mass": "Must be a positive number",
                "height": "Must be a positive number",
                "ftp": "Must be a positive number",
                "zwift_racing_score": "Must be a non-negative integer",
                "velo_rating": "Must be a non-negative integer"
            }
        }

    def calculate_coefficient_of_drag(self) -> float:
        return estimate_coefficient_of_drag(self.mass, self.height, self.gender)

    def calculate_frontal_area(self) -> float:
        return estimate_frontal_area(self.mass, self.height, self.gender)

    def calculate_power_from_velocity(self, velocity: float) -> float:
        coefficient_of_drag = self.calculate_coefficient_of_drag()
        frontal_area = self.calculate_frontal_area()
        return estimate_wattage_from_speed(velocity, coefficient_of_drag, frontal_area)

    def calculate_velocity_from_power(self, power: float) -> float:
        coefficient_of_drag = self.calculate_coefficient_of_drag()
        frontal_area = self.calculate_frontal_area()
        return estimate_speed_from_wattage(power, coefficient_of_drag, frontal_area)

    def calculate_energy_consumed_from_power_and_duration(self, power: float, duration: float) -> float:
        return estimate_joules_from_wattage_and_time(power, duration)

class Ride(BaseModel):
    rider: Rider = Rider()
    distance: float = 40000  # Distance in meters

    class Config:
        json_schema_extra = {
            "example": {
                "rider": {
                    "name": "John Doe",
                    "mass": 75,
                    "height": 183,
                    "gender": "male",
                    "ftp": 3.5,
                    "zwift_racing_score": 500,
                    "velo_rating": 1200
                },
                "distance": 40000
            },
            "description": {
                "rider": "The rider participating in the ride",
                "distance": "The distance of the ride in meters"
            },
            "validation": {
                "distance": "Must be a positive number"
            }
        }

    def compute_finishing_time(self, ftp_percentage: float) -> float:
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
        velocity = self.rider.calculate_velocity_from_power(power)

        # Calculate the finishing time
        finishing_time = self.distance / velocity

        return finishing_time

    def compute_average_speed(self, ftp_percentage: float) -> float:
        """
        Calculate the average speed for the ride as a whole.
        
        Args:
        ftp_percentage (float): The percentage of the rider's FTP to ride at.
        
        Returns:
        float: The average speed in meters per second.
        """
        # Calculate the finishing time
        finishing_time = self.compute_finishing_time(ftp_percentage)

        # Calculate the average speed
        average_speed = self.distance / finishing_time

        return average_speed

    def compute_total_energy_consumed(self, ftp_percentage: float) -> float:
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
        velocity = self.rider.calculate_velocity_from_power(power)

        # Calculate the finishing time
        finishing_time = self.distance / velocity

        # Calculate the total energy consumption
        total_energy_consumption = estimate_joules_from_wattage_and_time(power, finishing_time)

        return total_energy_consumption

    def compute_overall_energy_intensity(self, ftp_percentage: float) -> float:
        """
        Calculate the energy total energy consumption intensity as the ratio of the total energy consumption
        to the energy that would have been consumed at a constant average power of 100% of FTP.
        
        Args:
        ftp_percentage (float): The percentage of the rider's FTP to ride at.
        
        Returns:
        float: The energy total energy consumption intensity (dimensionless).
        """
        # Calculate the total energy consumption at the given FTP percentage
        total_energy_consumption = self.compute_total_energy_consumed(ftp_percentage)

        # Calculate the power at 100% FTP
        power_at_100_ftp = self.rider.ftp * self.rider.mass

        # Calculate the velocity at 100% FTP
        velocity_at_100_ftp = self.rider.calculate_velocity_from_power(power_at_100_ftp)

        # Calculate the finishing time at 100% FTP
        finishing_time_at_100_ftp = self.distance / velocity_at_100_ftp

        # Calculate the energy consumption at 100% FTP
        energy_consumption_at_100_ftp = estimate_joules_from_wattage_and_time(power_at_100_ftp, finishing_time_at_100_ftp)

        # Calculate the energy total energy consumption intensity
        energy_total_energy_consumption_intensity = total_energy_consumption / energy_consumption_at_100_ftp

        return energy_total_energy_consumption_intensity

class Interval(BaseModel):
    rider: Rider = Rider()
    duration: float = 30  # seconds
    velocity: float = 10  # meters/second
    drafting_power_saving_percentage: float = 0  # percentage, dimensionless ratio

    class Config:
        json_schema_extra = {
            "example": {
                "rider": {
                    "name": "John Doe",
                    "mass": 75,
                    "height": 183,
                    "gender": "male",
                    "ftp": 3.5,
                    "zwift_racing_score": 500,
                    "velo_rating": 1200
                },
                "duration": 30,
                "velocity": 10,
                "drafting_power_saving_percentage": 0
            },
            "description": {
                "rider": "The rider participating in the interval",
                "duration": "The duration of the interval in seconds",
                "velocity": "The velocity during the interval in meters per second",
                "drafting_power_saving_percentage": "The percentage of power saved due to drafting"
            },
            "validation": {
                "duration": "Must be a positive number",
                "velocity": "Must be a positive number",
                "drafting_power_saving_percentage": "Must be a non-negative number"
            }
        }

    def determine_distance(self) -> float:
        """
        Calculate the distance covered during the interval.
        
        Returns:
        float: The distance in meters.
        """
        return self.velocity * self.duration

    def determine_average_power(self) -> float:
        """
        Calculate the power after adjusting for the power saving percentage.
        
        Returns:
        float: The adjusted power in watts.
        """
        base_power = self.rider.calculate_power_from_velocity(self.velocity)
        adjusted_power = base_power * (1 - self.drafting_power_saving_percentage / 100)
        return adjusted_power

    def determine_average_power_to_ftp_ratio(self) -> float:
        """
        Calculate the ratio of the adjusted power to the rider's FTP.
        
        Returns:
        float: The power to FTP ratio.
        """
        adjusted_power = self.determine_average_power()
        ftp_power = self.rider.ftp * self.rider.mass
        return adjusted_power / ftp_power

    def determine_energy_consumed(self) -> float:
        """
        Calculate the energy consumption from the adjusted power and duration.
        
        Returns:
        float: The energy consumption in joules.
        """
        adjusted_power = self.determine_average_power()
        return estimate_joules_from_wattage_and_time(adjusted_power, self.duration)

# Example usage
def main():

    # Instantiate Rider using the example from Config
    example_data = Rider.Config.json_schema_extra["example"]
    rider = Rider.model_validate(example_data)

    # Log the instantiated object
    logger.info(f"Rider instantiated from JSON config is:-\r\n{rider}")

    # Create an instance of Rider with height=183, mass=75, gender=MALE, and ftp=3.5
    rider = Rider(name="John Doe", mass=75, height=183, gender=Gender.MALE, ftp=3.5, zwift_racing_score=500, velo_rating=1200)
    ride = Ride(rider=rider, distance=40000)
    velocity = 10.0  # m/s
    power = rider.calculate_power_from_velocity(velocity)
    logger.info(f"Power for velocity {velocity} m/s: {power:.2f} W")

    power = 300  # W
    velocity = rider.calculate_velocity_from_power(power)
    logger.info(f"Velocity for power {power} W: {velocity:.2f} m/s")

    duration = 3600  # seconds (1 hour)
    energy = rider.calculate_energy_consumed_from_power_and_duration(power, duration)
    logger.info(f"Energy for power {power} W over {duration} seconds: {energy:.2f} J")

    # Calculate the finishing time for the ride at 75% of the rider's FTP
    ftp_percentage = 0.75
    finishing_time = ride.compute_finishing_time(ftp_percentage)
    logger.info(f"Finishing time for the ride at {ftp_percentage * 100}% of FTP: {finishing_time:.2f} seconds")

    # Calculate the total energy consumption for the ride at 75% of the rider's FTP
    total_energy_consumption = ride.compute_total_energy_consumed(ftp_percentage)
    logger.info(f"Total energy consumption for the ride at {ftp_percentage * 100}% of FTP: {total_energy_consumption:.2f} joules")

    # Calculate the energy total energy consumption intensity for the ride at 75% of the rider's FTP
    energy_total_energy_consumption_intensity = ride.compute_overall_energy_intensity(ftp_percentage)
    logger.info(f"Energy total energy consumption intensity for the ride at {ftp_percentage * 100}% of FTP: {energy_total_energy_consumption_intensity:.2f}")

    # Calculate the average speed for the ride at 75% of the rider's FTP
    average_speed = ride.compute_average_speed(ftp_percentage)
    logger.info(f"Average speed for the ride at {ftp_percentage * 100}% of FTP: {average_speed:.2f} m/s")

    # Calculate the finishing time for the ride at 100% of the rider's FTP
    ftp_percentage = 1.0
    finishing_time = ride.compute_finishing_time(ftp_percentage)
    logger.info(f"Finishing time for the ride at {ftp_percentage * 100}% of FTP: {finishing_time:.2f} seconds")

    # Calculate the total energy consumption for the ride at 100% of the rider's FTP
    total_energy_consumption = ride.compute_total_energy_consumed(ftp_percentage)
    logger.info(f"Total energy consumption for the ride at {ftp_percentage * 100}% of FTP: {total_energy_consumption:.2f} joules")

    # Calculate the energy total energy consumption intensity for the ride at 100% of the rider's FTP
    energy_total_energy_consumption_intensity = ride.compute_overall_energy_intensity(ftp_percentage)
    logger.info(f"Energy total energy consumption intensity for the ride at {ftp_percentage * 100}% of FTP: {energy_total_energy_consumption_intensity:.2f}")

    # Calculate the average speed for the ride at 100% of the rider's FTP
    average_speed = ride.compute_average_speed(ftp_percentage)
    logger.info(f"Average speed for the ride at {ftp_percentage * 100}% of FTP: {average_speed:.2f} m/s")

    # Calculate the finishing time for the ride at 130% of the rider's FTP
    ftp_percentage = 1.3
    finishing_time = ride.compute_finishing_time(ftp_percentage)
    logger.info(f"Finishing time for the ride at {ftp_percentage * 100}% of FTP: {finishing_time:.2f} seconds")

    # Calculate the total energy consumption for the ride at 130% of the rider's FTP
    total_energy_consumption = ride.compute_total_energy_consumed(ftp_percentage)
    logger.info(f"Total energy consumption for the ride at {ftp_percentage * 100}% of FTP: {total_energy_consumption:.2f} joules")

    # Create an instance of Rider with height=183, mass=75, gender=MALE, and ftp=3.5
    rider = Rider(name="John Doe", mass=75, height=183, gender=Gender.MALE, ftp=3.5, zwift_racing_score=500, velo_rating=1200)
    ride = Ride(rider=rider, distance=40000)
    
    # Calculate the finishing time for the ride at 100% of the rider's FTP
    ftp_percentage = 1.0
    finishing_time = ride.compute_finishing_time(ftp_percentage)
    logger.info(f"Finishing time for the ride at {ftp_percentage * 100}% of FTP: {finishing_time:.2f} seconds")

    # Calculate the average speed for the ride at 100% of the rider's FTP
    average_speed = ride.compute_average_speed(ftp_percentage)
    logger.info(f"Average speed for the ride at {ftp_percentage * 100}% of FTP: {average_speed:.2f} m/s")

    # Calculate the total energy consumption for the ride at 100% of the rider's FTP
    total_energy_consumption = ride.compute_total_energy_consumed(ftp_percentage)
    logger.info(f"Total energy consumption for the ride at {ftp_percentage * 100}% of FTP: {total_energy_consumption:.2f} joules")

    # Create an Interval instance with the calculated duration and velocity
    interval = Interval(rider=rider, duration=finishing_time, velocity=average_speed)
    interval_energy_consumed = interval.determine_energy_consumed()
    logger.info(f"Energy consumption for the interval: {interval_energy_consumed:.2f} joules")

    # Check if the energy consumed in the ride and interval are equivalent
    if abs(total_energy_consumption - interval_energy_consumed) < 1e-6:
        logger.info("The energy consumption for the ride and interval are equivalent.")
    else:
        logger.error("The energy consumption for the ride and interval are not equivalent.")

if __name__ == "__main__":
    main()