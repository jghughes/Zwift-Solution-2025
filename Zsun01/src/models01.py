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
            Generate a unique key based on all the parameters that define
            an instance of the class as used in the ctor for the frozen class.

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

    class Config:
        frozen = True
        json_schema_extra = {
            "davek": {
                "zwiftid": 3147366,
                "name": "Dave K",
                "weight": 73.4,
                "height": 182,
                "gender": "m",
                "ftp": 276,
                "zwift_racing_score": 744,
                "velo_rating": 1897,
            },
            "huskyc": {
                "zwiftid": 5134,
                "name": "Husky C",
                "weight": 75.5,
                "height": 178,
                "gender": "m",
                "ftp": 268,
                "zwift_racing_score": 552,
                "velo_rating": 1519,
            },
            "scottm": {
                "zwiftid": 11526,
                "name": "Scott M",
                "weight": 78,
                "height": 165,
                "gender": "m",
                "ftp": 247,
                "zwift_racing_score": 509,
                "velo_rating": 1537,
            },
            "markb": {
                "zwiftid": 5530045,
                "name": "Mark B",
                "weight": 91.6,
                "height": 185,
                "gender": "m",
                "ftp": 229,
                "zwift_racing_score": 493,
                "velo_rating": 1309,
            },
            "barryb": {
                "zwiftid": 5490373,
                "name": "Barry B",
                "weight": 77,
                "height": 176,
                "gender": "m",
                "ftp": 273,
                "zwift_racing_score": 444,
                "velo_rating": 1294,
            },
            "johnh": {
                "zwiftid": 58160,
                "name": "John H",
                "weight": 75.4,
                "height": 174,
                "gender": "m",
                "ftp": 233,
                "zwift_racing_score": 351,
                "velo_rating": 1067,
            },
            "brenth": {
                "zwiftid": 480698,
                "name": "Brent H",
                "weight": 75.6,
                "height": 180,
                "gender": "m",
                "ftp": 243,
                "zwift_racing_score": 335,
                "velo_rating": 1078,
            },
            "joshn": {
                "zwiftid": 2508033,
                "name": "Josh N",
                "weight": 101,
                "height": 178,
                "gender": "m",
                "ftp": 260,
                "zwift_racing_score": 285,
                "velo_rating": 942,
            },
            "edh": {
                "zwiftid": 1713736,
                "name": "Ed H",
                "weight": 107.5,
                "height": 188,
                "gender": "m",
                "ftp": 274,
                "zwift_racing_score": 206,
                "velo_rating": 748,
            },
            "richardm": {
                "zwiftid": 1193,
                "name": "Richard M",
                "weight": 93,
                "height": 178,
                "gender": "m",
                "ftp": 200,
                "zwift_racing_score": 189,
                "velo_rating": 628,
            },
            "selenas": {
                "zwiftid": 2682791,
                "name": "Selena S",
                "weight": 63,
                "height": 171,
                "gender": "f",
                "ftp": 214,
                "zwift_racing_score": 345,
                "velo_rating": 1129,
            },
            "kristend": {
                "zwiftid": 2398312,
                "name": "Kristen D",
                "weight": 71.2,
                "height": 178,
                "gender": "f",
                "ftp": 236,
                "zwift_racing_score": 338,
                "velo_rating": 1035,
            },
            "lynseys": {
                "zwiftid": 383480,
                "name": "Lynsey S",
                "weight": 63.5,
                "height": 165,
                "gender": "f",
                "ftp": 201,
                "zwift_racing_score": 327,
                "velo_rating": 915,
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

class ZwiftRiderCache:
    _cache: Dict[str, ZwiftRider] = {}

    @classmethod
    def get_from_cache(cls, key: Union[str, None]) -> Union[ZwiftRider, None]:
        if key is None:
            return None
        return cls._cache.get(key)

    @classmethod
    def add_to_cache(cls, key: Union[str, None], instance: ZwiftRider):
        if key is None:
            return
        cls._cache[key] = instance

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()

    @classmethod
    def get_cache_contents(cls) -> Dict[str, ZwiftRider]:
        return cls._cache

    @classmethod
    def display_cache_contents(cls) -> str:
        if not cls._cache:
            return "Cache is empty."
        
        cache_contents = ["Cache contents:"]
        for key, rider in cls._cache.items():
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

    @classmethod
    def get_cache_count(cls) -> int:
        """
        Get the count of items in the cache.

        Returns:
        int: The number of items in the cache.
        """
        return len(cls._cache)

    @staticmethod
    def get_or_create(
        zwiftid: int, name: str, weight: float, height: float, gender: Gender, 
        ftp: float, zwift_racing_score: int, velo_rating: int
    ) -> ZwiftRider:
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
        cached_instance = ZwiftRiderCache.get_from_cache(key)
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

        ZwiftRiderCache.add_to_cache(key, instance)
        return instance

# Example usage
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # # example: Instantiate ZwiftRider using the example from Config 
    # # i.e.how we could do it from a JSON file
    example_data = ZwiftRider.Config.json_schema_extra["johnh"]
    rider1 = ZwiftRider.model_validate(example_data)

    # Log the instantiated object using a table
    rider_attrs = [[attr, getattr(rider1, attr)] for attr in rider1.model_fields.keys()]
    logger.info("\nZwiftRider instantiated (ctor) from JSON config is:")
    logger.info("\n" + tabulate(rider_attrs, tablefmt="plain"))

    # example : instantiate examples of two riders of differing ability. for each of them 
    # calculate wattage at a given speed (40kph)and in two positions in the peloton - 
    # position 1 and position 5. tabulate the results in a table and log it.
    example_data = ZwiftRider.Config.json_schema_extra["markb"]
    rider2 = ZwiftRider.model_validate(example_data)

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
    logger.info("\nRider wattage in positions 1 and 5 for speeds 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))

    # example : using rider "John H" instantiated using ctor
    # calculate wattage for each position in the peloton from 1 to 5
    # at a given speed (40kph) and tabulate neatly and log it.
    rider_john = rider1

    positions = range(1, 6)
    table: List[List[Union[str, float]]] = []
    headers = ["Position", "Wattage (Speed 40 km/h)"]

    for position in positions:
        wattage = rider_john.calculate_wattage_riding_in_the_peloton(40, position)
        table.append([position, wattage])

    # Log the table
    logger.info("\nWattage for John H in positions 1 to 5 at speed 40 km/h")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))

    # example : using rider "John H" instantiated using ctor
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
    logger.info("\nSpeed for John H in positions 1 to 5 at FTP 233")
    logger.info("\n" + tabulate(table, headers=headers, tablefmt="simple"))


    # Test cache functionality
    logger.info("\nTesting cache functionality with rider_john")
    rider_john_key = rider_john.get_key()
    ZwiftRiderCache.add_to_cache(rider_john_key, rider_john)

    # Attempt to get_or_create rider_john again instantiated using get_or_create()
    # This should return the cached instance
    cached_rider_john = ZwiftRiderCache.get_or_create(
        zwiftid=rider_john.zwiftid,
        name=rider_john.name,
        weight=rider_john.weight,
        height=rider_john.height,
        gender=rider_john.gender,
        ftp=rider_john.ftp,
        zwift_racing_score=rider_john.zwift_racing_score,
        velo_rating=rider_john.velo_rating
    )

    # Check if the cached instance is the same as the original instance
    if cached_rider_john is rider_john:
        logger.info("Cache is working: The second attempt to get_or_create rider_john returned the cached instance.")
    else:
        logger.error("Cache is not working: The second attempt to get_or_create rider_john did not return the cached instance.")

    # Log the count of items in the cache
    cache_count = ZwiftRiderCache.get_cache_count()
    logger.info(f"Number of items in the cache: {cache_count}")

if __name__ == "__main__":
    main()
