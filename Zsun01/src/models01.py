from pydantic import BaseModel
from enum import Enum
from typing import List, Tuple

from formulae import *

class Gender(Enum):
    MALE = 'm'
    FEMALE = 'f'

class ZwiftRider(BaseModel):
    """
    A class representing a Zwift rider.

    Attributes:
        rank               : int    The rank of the rider in a group of riders.
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
    rank               : int    = 0               # Rank of the rider in agroup of riders
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

    def calculate_strength(self)-> float:
        return self.ftp/self.weight

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

class Team(BaseModel):
    riders_working : list[ZwiftRider] = []
    riders_sleeping : list[ZwiftRider] = []
    
    @staticmethod
    def create(riders: list[ZwiftRider]) -> 'Team':
        riders.sort(key=lambda x: x.calculate_strength(), reverse=True)
        #assign rank to rank attr sarting with 1
        for i, rider in enumerate(riders):
            rider.rank = i+1
        team = Team(riders_working = riders, riders_sleeping=[])
        return team

    def sort_riders(self) -> None:
        self.riders_working.sort(key=lambda x: x.calculate_strength(), reverse=True)
        self.riders_sleeping.sort(key=lambda x: x.calculate_strength(), reverse=True)

    def demote_rider_from_working_to_sleeping(self, rider: ZwiftRider) -> None:
        self.riders_sleeping.append(rider)
        self.riders_working.remove(rider)
        self.sort_riders()

    def promote_rider_from_sleeping_to_working(self, rider: ZwiftRider) -> None:
        self.riders_working.append(rider)
        self.riders_sleeping.remove(rider)
        self.sort_riders()













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