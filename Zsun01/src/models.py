from pydantic import BaseModel
from enum import Enum

from formulae import *

class Gender(Enum):
    MALE = 'm'
    FEMALE = 'f'

class ZwiftRider(BaseModel):
    """
    A class representing a Zwift rider.

    Attributes:
        zwiftid            : int    The Zwift ID of the rider.
        name               : str    The name of the rider.
        weight             : float  The weight of the rider in kilograms.
        height             : float  The height of the rider in centimeters.
        gender             : Gender The gender of the rider.
        ftp                : float  Functional Threshold Power in watts.
        zwift_racing_score : int    Zwift racing score.
        velo_rating        : int    Velo rating.

    Methods:
        calculate_kph_riding_alone(power: float) -> float:
            Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.

        calculate_wattage_riding_alone(speed: float) -> float:
            Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

        calculate_wattage_riding_in_the_peloton(speed: float, position: int) -> float:
            Calculate the wattage required for a rider given their speed and position in the peloton.
    """
    zwiftid            : int    = 0               # Zwift ID of the rider
    name               : str    = "Eric Schlange" # Name of the rider
    weight             : float  = 84.3            # Weight of the rider in kilograms
    height             : float  = 180             # Height of the rider in centimeters
    gender             : Gender = Gender.MALE     # Gender of the rider
    ftp                : float  = 272             # Functional Threshold Power in watts
    zwift_racing_score : int    = 549             # Zwift racing score
    velo_rating        : int    = 1513            # Velo rating

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

    def calculate_kph_riding_alone(self, power: float) -> float:
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

    def calculate_wattage_riding_alone(self, speed: float) -> float:
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

    def calculate_wattage_riding_in_the_peloton(self, speed: float, position: int) -> float:
        """
        Calculate the wattage required for a rider given their speed and position in the peloton.

        Args:
        rider (ZwiftRider): The rider object.
        speed (float): The speed in km/h.
        position (int): The position in the peloton.

        Returns:
        float: The required wattage in watts.
        """
        # Calculate the base power required for the given speed
        base_power = self.calculate_wattage_riding_alone(speed)

        # Get the power factor based on the rider's position in the peloton
        power_factor = estimate_power_factor_in_peloton(position)

        # Adjust the power based on the power factor
        adjusted_power = base_power * power_factor

        return round(adjusted_power, 3)

class Interval(BaseModel):
    """
    A class representing an interval for a Zwift rider.

    Attributes:
        rider                : ZwiftRider The Zwift rider participating in the interval.
        duration             : float      The duration of the interval in seconds.
        speed                : float      The speed during the interval in kilometers per hour.
        distance             : float      The distance covered during the interval in meters.
        position_in_peloton  : int        The position of the rider in the peloton.
        power_output         : float      The average wattage in the rider's position.
        energy_burned        : float      The energy burned in the rider's position in kiloJoules.

    Methods:
        create(rider: ZwiftRider, duration: float, speed: float, distance: float, position: int) -> 'Interval':
            Create an Interval instance with the given parameters, calculating the wattage and energy burned.
    """

    rider               : ZwiftRider = ZwiftRider()  # The Zwift rider participating in the interval
    duration            : float      = 0             # The duration of the interval in seconds
    speed               : float      = 0             # The speed during the interval in kilometers per hour
    distance            : float      = 0             # The distance covered during the interval in meters
    position_in_peloton : int        = 1             # The position of the rider in the peloton
    power_output        : float      = 0             # The average wattage in the rider's position
    energy_burned       : float      = 0             # The energy burned in the rider's position in kiloJoules

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
                "power_output": 270,
                "energy_burned": 972
            },
            "description": {
                "rider": "The rider participating in the interval",
                "duration": "The duration of the interval in seconds",
                "speed": "The speed during the interval in kilometers per hour",
                "distance": "The distance covered during the interval in meters",
                "position_in_peloton": "The position of the rider in the peloton",
                "power_output": "The average wattage in the rider's position",
                "energy_burned": "The energy burned in the rider's position in kiloJoules"
            },
            "validation": {
                "duration": "Must be a positive number",
                "speed": "Must be a positive number",
                "distance": "Must be a positive number",
                "position_in_peloton": "Must be a non-negative integer",
                "power_output": "Must be a positive number",
                "energy_burned": "Must be a positive number"
            }
        }

    @staticmethod
    def create(rider: ZwiftRider, duration: float, speed: float, distance: float, position: int) -> 'Interval':

        speed, duration, distance = triangulate_speed_time_and_distance(speed, duration, distance)
        wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position)
        energy = estimate_joules_from_wattage_and_time(wattage, duration)/1000

        return Interval(
            rider=rider,
            duration=duration,
            speed=speed,
            distance=distance,
            position_in_peloton=position,
            power_output=wattage,
            energy_burned=energy
        )

# Example usage
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Instantiate ZwiftRider using the example from Config
    example_data = ZwiftRider.Config.json_schema_extra["example"]
    rider = ZwiftRider.model_validate(example_data)
    # Log the instantiated object
    logger.info(f"ZwiftRider instantiated from JSON config is:-\r\n{rider}")


if __name__ == "__main__":
    main()