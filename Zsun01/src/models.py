from pydantic import BaseModel
from enum import Enum

from formulae import *

class Gender(Enum):
    MALE = 'm'
    FEMALE = 'f'


class Rider(BaseModel):
    zwiftid: int = 0  # Zwift ID of the rider
    name: str = "Eric Schlange"  # Name of the rider
    weight: float = 84.3
    height: float = 180
    gender: Gender = Gender.MALE
    ftp: float = 272  # Functional Threshold Power in watts
    zwift_racing_score: int = 549  # Zwift racing score
    velo_rating: int = 1513  # Velo rating

    class Config:
        json_schema_extra = {
            "example": {
                "zwiftid": 58160,
                "name": "Eric Schlange",
                "weight": 84.3,
                "height": 180,
                "gender": "male",
                "ftp": 272,
                "zwift_racing_score": 549,
                "velo_rating": 1513
            },
            "description": {
                "zwiftid": "The Zwift ID of the rider",
                "name": "The name of the rider",
                "weight": "The weight of the rider in kilograms",
                "height": "The height of the rider in centimeters",
                "gender": "The gender of the rider",
                "ftp": "Functional Threshold Power in watts",
                "zwift_racing_score": "Zwift racing score",
                "velo_rating": "Velo rating"
            },
            "validation": {
                "zwiftid": "Must be a non-negative integer",
                "weight": "Must be a positive number",
                "height": "Must be a positive number",
                "ftp": "Must be a positive number",
                "zwift_racing_score": "Must be a non-negative integer",
                "velo_rating": "Must be a non-negative integer"
            }
        }

    def calculate_wattage_from_kph(self, speed: float) -> float:
        """
        Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

        Args:
        speed (float): The speed in km/h.

        Returns:
        float: The calculated power in watts.
        """
        # Calculate the power using the estimate_wattage_from_speed function
        power = estimate_wattage_from_speed(speed, self.weight, self.height)
        return power

    def calculate_kph_from_wattage(self, power: float) -> float:
        """
        Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.

        Args:
        power (float): The power in watts.

        Returns:
        float: The estimated speed in km/h.
        """
        # Estimate the speed in km/h using the estimate_speed_from_wattage function
        speed_kph = estimate_speed_from_wattage(power, self.weight, self.height)
        return speed_kph

    def calculate_kilojoules_from_wattage_and_seconds(self, power: float, duration: float) -> float:
        """
        Calculate the energy consumption in kilojoules given power and duration.

        Args:
        power (float): The power in watts.
        duration (float): The duration in seconds.

        Returns:
        float: The energy consumption in kilojoules.
        """
        # Calculate the energy consumption in joules
        energy_joules = estimate_joules_from_wattage_and_time(power, duration)
        # Convert joules to kilojoules
        energy_kilojoules = energy_joules / 1000
        return round(energy_kilojoules, 3)

    def calculate_wattage_from_kph_and_position(self, speed: float, position_in_peloton: int) -> float:
        """
        Determine the wattage required for a rider given their speed and position in the peloton.

        Args:
        rider (Rider): The rider object.
        speed (float): The speed in km/h.
        position (int): The position in the peloton.

        Returns:
        float: The required wattage in watts.
        """
        # Calculate the base power required for the given speed
        base_power = self.calculate_wattage_from_kph(speed)

        # Adjust the power based on the rider's position in the peloton
        if position_in_peloton == 1:
            # No drafting benefit for the lead rider
            adjusted_power = base_power
        else:
            # Apply a drafting benefit for riders behind the lead
            drafting_benefit = 0.1 * (position_in_peloton - 1)  # Example: 10% benefit per position behind the lead
            adjusted_power = base_power * (1 - drafting_benefit)

        return round(adjusted_power, 3)


class Interval(BaseModel):
    rider: Rider = Rider()
    duration: float = 0  # seconds
    speed: float = 0  # km/h
    distance: float = 0  # meters
    position_in_peloton: int = 1
    average_wattage_if_leader: float = 0  # watts
    average_wattage_if_follower: float = 0  # watts
    energy_burned_if_leader : float = 0 # kiloJoules
    energy_burned_if_follower: float = 0 # kiloJoules

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "rider": {
                    "name": "John Doe",
                    "weight": 75,
                    "height": 183,
                    "gender": "male",
                    "ftp": 3.5,
                    "zwift_racing_score": 500,
                    "velo_rating": 1200
                },
                "duration": 30,
                "speed": 10,
                "distance": 300,
                "position_in_peloton": 2,
                "average_wattage_if_leader": 300,
                "average_wattage_if_follower": 270,
                "energy_burned_if_leader": 1080,
                "energy_burned_if_follower": 972
            },
            "description": {
                "rider": "The rider participating in the interval",
                "duration": "The duration of the interval in seconds",
                "speed": "The speed during the interval in kilometers per hour",
                "distance": "The distance covered during the interval in meters",
                "position_in_peloton": "The position of the rider in the peloton",
                "average_wattage_if_leader": "The average wattage if the rider is the leader",
                "average_wattage_if_follower": "The average wattage if the rider is a follower",
                "energy_burned_if_leader": "The energy burned if the rider is the leader in kiloJoules",
                "energy_burned_if_follower": "The energy burned if the rider is a follower in kiloJoules"
            },
            "validation": {
                "duration": "Must be a positive number",
                "speed": "Must be a positive number",
                "distance": "Must be a positive number",
                "position_in_peloton": "Must be a non-negative integer",
                "average_wattage_if_leader": "Must be a positive number",
                "average_wattage_if_follower": "Must be a positive number",
                "energy_burned_if_leader": "Must be a positive number",
                "energy_burned_if_follower": "Must be a positive number"
            }
        }

    @staticmethod
    def create(rider: Rider, duration: float, speed: float, distance: float, position: int) -> 'Interval':
        speed, duration, distance = triangulate_speed_time_and_distance(speed, duration, distance)
        average_wattage_if_leader = rider.calculate_wattage_from_kph_and_position(speed, 1)
        average_wattage_as_follower = rider.calculate_wattage_from_kph_and_position(speed, position)

        energy_burned_by_leader = rider.calculate_kilojoules_from_wattage_and_seconds(average_wattage_if_leader, duration)
        energy_burned_by_follower = rider.calculate_kilojoules_from_wattage_and_seconds(average_wattage_as_follower, duration)

        return Interval(rider=rider, duration=duration, speed=speed, distance=distance, position_in_peloton=position, average_wattage_if_leader = average_wattage_if_leader, average_wattage_if_follower = average_wattage_as_follower energy_burned_if_leader=energy_burned_by_leader, energy_burned_if_follower=energy_burned_by_follower)


# Example usage
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)


    # Instantiate Rider using the example from Config
    example_data = Rider.Config.json_schema_extra["example"]
    rider = Rider.model_validate(example_data)

    # Log the instantiated object
    logger.info(f"Rider instantiated from JSON config is:-\r\n{rider}")

    # Create an instance of Rider with height=183, weight=75, gender=MALE, and ftp=3.5
    rider = Rider(name="John Doe", weight=75, height=183, gender=Gender.MALE, ftp=3.5, zwift_racing_score=500, velo_rating=1200)
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

    # Create an instance of Rider with height=183, weight=75, gender=MALE, and ftp=3.5
    rider = Rider(name="John Doe", weight=75, height=183, gender=Gender.MALE, ftp=3.5, zwift_racing_score=500, velo_rating=1200)
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