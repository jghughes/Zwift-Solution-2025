from typing import List, Union, Dict
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
        zwiftid            : int    The Zwift ID of the rider.
        name               : str    The name of the rider.
        weight             : float  The weight of the rider in kilograms.
        height             : float  The height of the rider in centimeters.
        gender             : Gender The gender of the rider.
        ftp                : float  Functional Threshold Power in watts.
        zwift_racing_score : int    Zwift racing score.
        velo_rating        : int    Velo rating.

    Methods:
        generate_key(
            zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
            ftp: float, zwift_racing_score: int, velo_rating: int
        ) -> str:
            Generate a unique key for the ZwiftRider instance.

        get_from_cache(key: str) -> 'ZwiftRider':
            Retrieve a ZwiftRider instance from the cache using the given key.

        add_to_cache(key: str, instance: 'ZwiftRider'):
            Add a ZwiftRider instance to the cache with the given key.

        clear_cache() -> None:
            Clear the cache of all ZwiftRider instances.

        get_cache_contents() -> Dict[str, 'ZwiftRider']:
            Get the contents of the cache.

        display_cache_contents() -> str:
            Display the contents of the cache in a readable format.

        create(
            zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
            ftp: float, zwift_racing_score: int, velo_rating: int
        ) -> 'ZwiftRider':
            Create a ZwiftRider instance with the given parameters, using the cache if available.

        get_key() -> str:
            Generate a unique key for the current ZwiftRider instance.

        calculate_strength() -> float:
            Calculate the strength of the rider based on FTP and weight.

        calculate_kph_riding_alone(power: float) -> float:
            Estimate the speed (km/h) given the power (wattage), weight (kg), and height (cm) using the Newton-Raphson method.

        calculate_wattage_riding_alone(speed: float) -> float:
            Calculate the power (P) as a function of speed (km/h), weight (kg), and height (cm).

        calculate_wattage_riding_in_the_peloton(speed: float, position: int) -> float:
            Calculate the wattage required for a rider given their speed and position in the peloton.

        calculate_speed_riding_in_the_peloton(power: float, position: int) -> float:
            Calculate the speed (km/h) for a rider given their power output (watts) and position in the peloton.
    """    
    
    zwiftid            : int    = 0             # Zwift ID of the rider
    name               : str    = ""            # Name of the rider
    weight             : float  = 0             # Weight of the rider in kilograms
    height             : float  = 0             # Height of the rider in centimeters
    gender             : Gender = Gender.MALE   # Gender of the rider
    ftp                : float  = 0             # Functional Threshold Power in watts
    zwift_racing_score : int    = 0             # Zwift racing score
    velo_rating        : int    = 0             # Velo rating

    _cache: Dict[str, 'ZwiftRider'] = {}

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "zwiftid": 58160,
                "name": "John Hughes",
                "weight": 75.4,
                "height": 174,
                "gender": "m",
                "ftp": 233,
                "zwift_racing_score": 351,
                "velo_rating": 1067,
            }
        }

    @staticmethod
    def generate_key(
        zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
        ftp: float, zwift_racing_score: int, velo_rating: int
    ) -> str:
        return ";".join([
            str(zwiftid), name, str(weight), str(height), gender.value, 
            str(ftp), str(zwift_racing_score), str(velo_rating)
        ])

    @classmethod
    def get_from_cache(cls, key: str) -> Union['ZwiftRider', None]:
        if key is None:
            return None
        return cls._cache.get(key)

    @classmethod
    def add_to_cache(cls, key: str, instance: 'ZwiftRider'):
        if key is None:
            return
        cls._cache[key] = instance

    @staticmethod
    def clear_cache() -> None:
        ZwiftRider._cache.clear()

    @staticmethod
    def get_cache_contents() -> Dict[str, 'ZwiftRider']:
        return ZwiftRider._cache

    @staticmethod
    def display_cache_contents() -> str:
        if not ZwiftRider._cache:
            return "Cache is empty."
        
        cache_contents = ["Cache contents:"]
        for key, rider in ZwiftRider._cache.items():
            cache_contents.append(f"Key: {key}")
            cache_contents.append(f"  ZwiftID: {rider.zwiftid}")
            cache_contents.append(f"  Name: {rider.name}")
            cache_contents.append(f"  Weight: {rider.weight}")
            cache_contents.append(f"  Height: {rider.height}")
            cache_contents.append(f"  Gender: {rider.gender.value}")
            cache_contents.append(f"  FTP: {rider.ftp}")
            cache_contents.append(f"  Zwift Racing Score: {rider.zwift_racing_score}")
            cache_contents.append(f"  Velo Rating: {rider.velo_rating}")
            cache_contents.append("")  # Add a blank line for readability
        
        return "\n".join(cache_contents)

    @staticmethod
    def create(
        zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
        ftp: float, zwift_racing_score: int, velo_rating: int
    ) -> 'ZwiftRider':
        """
        Create a ZwiftRider instance with the given parameters, using the cache if available.

        Args:
            zwiftid (int): The Zwift ID of the rider.
            name (str): The name of the rider.
            weight (float): The weight of the rider in kilograms.
            height (float): The height of the rider in centimeters.
            gender (Gender): The gender of the rider.
            ftp (float): Functional Threshold Power in watts.
            zwift_racing_score (int): Zwift racing score.
            velo_rating (int): Velo rating.

        Returns:
            ZwiftRider: A ZwiftRider instance with the given parameters.
        """

        key = ZwiftRider.generate_key(
            zwiftid, name, weight, height, gender, ftp, zwift_racing_score, velo_rating
        )
        cached_instance = ZwiftRider.get_from_cache(key)
        if cached_instance:
            return cached_instance

        instance = ZwiftRider(
            zwiftid=zwiftid,
            name=name,
            weight=weight,
            height=height,
            gender=gender,
            ftp=ftp,
            zwift_racing_score=zwift_racing_score,
            velo_rating=velo_rating
        )

        ZwiftRider.add_to_cache(key, instance)
        return instance

    def get_key(self) -> str:
        return self.generate_key(
            self.zwiftid, self.name, self.weight, self.height, self.gender, 
            self.ftp, self.zwift_racing_score, self.velo_rating
        )

    def calculate_strength(self) -> float:
        return self.ftp / self.weight

    def calculate_kph_riding_alone(self, power: float) -> float:
        """
        Estimate the speed (km/h) given the power (wattage), weight (kg), and 
        height (cm) using the Newton-Raphson method.

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
        Calculate the power (P) as a function of speed (km/h), weight (kg), and 
        height (cm).

        Args:
        speed (float): The speed in km/h.

        Returns:
        float: The calculated power in watts.
        """
        # Calculate the power using the estimate_wattage_from_speed function
        power = estimate_wattage_from_speed(speed, self.weight, self.height)
        return power

    def calculate_wattage_riding_in_the_peloton(
        self, speed: float, position: int
    ) -> float:
        """
        Calculate the wattage required for a rider given their speed and position 
        in the peloton.

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

    def calculate_speed_riding_in_the_peloton(
        self, power: float, position: int
    ) -> float:
        """
        Calculate the speed (km/h) for a rider given their power output (watts) 
        and position in the peloton.

        Args:
        power (float): The power output in watts.
        position (int): The position in the peloton.

        Returns:
        float: The estimated speed in km/h.
        """
        # Get the power factor based on the rider's position in the peloton
        power_factor = estimate_power_factor_in_peloton(position)

        # Adjust the power based on the power factor
        adjusted_watts = power / power_factor

        # Estimate the speed in km/h using the estimate_speed_from_wattage function
        speed_kph = estimate_speed_from_wattage(adjusted_watts, self.weight, self.height)
        
        return round(speed_kph, 3)

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
    # Log the instantiated object with neat columns
    logger.info("ZwiftRider instantiated from JSON config is:")
    logger.info(f"  ZwiftID            : {rider.zwiftid}")
    logger.info(f"  Name               : {rider.name}")
    logger.info(f"  Weight             : {rider.weight}")
    logger.info(f"  Height             : {rider.height}")
    logger.info(f"  Gender             : {rider.gender.value}")
    logger.info(f"  FTP                : {rider.ftp}")
    logger.info(f"  Zwift Racing Score : {rider.zwift_racing_score}")
    logger.info(f"  Velo Rating        : {rider.velo_rating}")

    # example : instantiate examples of two riders of differing ability. for each of them 
    # calculate wattage at a given speed (40kph)and in two positions in the peloton - 
    # position 1 and position 5. tabulate the results in a table and log it.
    rider1 = ZwiftRider(
        name="Mark B", weight=90.0, height=183, ftp=255, gender=Gender.MALE
    )
    rider2 = ZwiftRider(
        name="John H", weight=75.4, height=174, ftp=233, gender=Gender.MALE
    )
    riders = [rider1, rider2]
    table: List[List[Union[str, float]]] = []
    headers = [
        "Rider", "Wattage (Position 1, Speed 40 km/h)", 
        "Wattage (Position 5, Speed 40 km/h)"
    ]
    for rider in riders:
        row = [rider.name]
        for position in [1, 5]:
            wattage = rider.calculate_wattage_riding_in_the_peloton(40, position)
            row.append(str(wattage))  # Convert wattage to string
        table.append(row)
    
    # Log the table
    logger.info("Rider wattage in positions 1 and 5 for speeds 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

    # example : using rider "John H"  
    # calculate wattage for each position in the peloton from 1 to 5
    # at a given speed (40kph) and tabulate neatly and log it.
    rider_john = ZwiftRider(
        name="John H", weight=75.4, height=174, ftp=233, gender=Gender.MALE
    )
    positions = range(1, 6)
    table: List[List[Union[str, float]]] = []
    headers = ["Position", "Wattage (Speed 40 km/h)"]

    for position in positions:
        wattage = rider_john.calculate_wattage_riding_in_the_peloton(40, position)
        table.append([position, wattage])

    # Log the table
    logger.info("Wattage for John H in positions 1 to 5 at speed 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

    # example : using rider "John H"  
    # calculate speed for each position in the peloton from 1 to 5
    # at a given wattage (ftp=233) and tabulate neatly and log it.
    rider_john = ZwiftRider(
        name="John H", weight=75.4, height=174, ftp=233, gender=Gender.MALE
    )
    positions = range(1, 6)
    table: List[List[Union[str, float]]] = []
    headers = ["Position", "Speed (km/h) at FTP 233"]

    for position in positions:
        # Calculate the speed for the given position and FTP
        speed = rider_john.calculate_speed_riding_in_the_peloton(rider_john.ftp, position)
        table.append([position, speed])

    # Log the table
    logger.info("Speed for John H in positions 1 to 5 at FTP 233")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
