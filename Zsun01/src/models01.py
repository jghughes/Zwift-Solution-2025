import uuid
from typing import List, Union
from tabulate import tabulate

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
        rank               : int    The rank of the rider in a group of riders.
        zwiftid            : int    The Zwift ID of the rider.
        name               : str    The name of the rider.
        weight             : float  The weight of the rider in kilograms.
        height             : float  The height of the rider in centimeters.
        gender             : Gender The gender of the rider.
        ftp                : float  Functional Threshold Power in watts.
        zwift_racing_score : int    Zwift racing score.
        velo_rating        : int    Velo rating.
        guid               : str    Unique identifier for the rider.

    Methods:
        calculate_kph_riding_alone(power: float) -> float:
            Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.

        calculate_wattage_riding_alone(speed: float) -> float:
            Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

        calculate_wattage_riding_in_the_peloton(speed: float, position: int) -> float:
            Calculate the wattage required for a rider given their speed and position in the peloton.
    """
    rank               : int    = 0               # Rank of the rider in a group of riders
    zwiftid            : int    = 0               # Zwift ID of the rider
    name               : str    = "Eric Schlange" # Name of the rider
    weight             : float  = 84.3            # Weight of the rider in kilograms
    height             : float  = 180             # Height of the rider in centimeters
    gender             : Gender = Gender.MALE     # Gender of the rider
    ftp                : float  = 272             # Functional Threshold Power in watts
    zwift_racing_score : int    = 549             # Zwift racing score
    velo_rating        : int    = 1513            # Velo rating
    guid               : str    = str(uuid.uuid4()) # Unique identifier for the rider

    class Config:
        json_schema_extra = {
            "example": {
                "zwiftid": 58160,
                "name": "Eric Schlange",
                "weight": 84.3,
                "height": 180,
                "gender": "m",
                "ftp": 272,
                "zwift_racing_score": 549,
                "velo_rating": 1513,
                "guid": "generated-uuid-placeholder"
            }
        }

    def calculate_strength(self) -> float:
        return self.ftp / self.weight

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

    #add a def named get_key to return a concatentaion of all the attributes except rank and guid
    def get_key(self) -> str:
        return f"{self.zwiftid}{self.name}{self.weight}{self.height}{self.gender}{self.ftp}{self.zwift_racing_score}{self.velo_rating}"  

# Example usage
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # example: Instantiate ZwiftRider using the example from Config 
    # i.e.how we could do it from a JSON file
    example_data = ZwiftRider.Config.json_schema_extra["example"]
    rider = ZwiftRider.model_validate(example_data)
    # Log the instantiated object
    logger.info(f"ZwiftRider instantiated from JSON config is:-\r\n{rider}")

    # instantiate examples of two riders of differing ability. for each of them calculate 
    # strength, kph, and wattage and in two positions in the peloton - position 1 and position 5.
    # tabulate the results in a table and log it.
    rider1 = ZwiftRider(name="Rider 1", weight=90.0, height=183, ftp=300, gender=Gender.MALE)
    rider2 = ZwiftRider(name="Rider 2", weight=75.4, height=174, ftp=200, gender=Gender.MALE)
    riders = [rider1, rider2]
    table: List[List[Union[str, float]]] = []
    headers = ["Rider", "Wattage (Position 1, Speed 40 km/h)", "Wattage (Position 5, Speed 40 km/h)"]
    for rider in riders:
        row = [rider.name]
        for position in [1, 5]:
            wattage = rider.calculate_wattage_riding_in_the_peloton(40, position)
            row.append(str(wattage))  # Convert wattage to string
        table.append(row)
    
    # Log the table
    logger.info("Rider wattage in positions 1 and 5 for speeds 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()