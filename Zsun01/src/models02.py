from pydantic import BaseModel
from models01 import *
from typing import Dict

class RiderPeriodOfEffort(BaseModel):
    """
    A class representing the effort of a Zwift rider in a specified period 
    of a multi-period rotation, based on his position in the peloton at the time
    of the effort.

    Attributes:
        rider (ZwiftRider): The Zwift rider participating in the period.
        duration (float): The duration of the period in seconds.
        speed (float): The speed during the period in kilometers per hour.
        position_in_peloton (int): The position of the rider in the peloton.
        power_output (float): The average wattage in the rider's position.
        energy_burned (float): The energy burned in the rider's position in kiloJoules.

    Methods:
        generate_key(rider: ZwiftRider, duration: float, speed: float, position_in_peloton: int) -> str:
            Generate a unique key for caching based on rider, duration, speed, and position.
        get_from_cache(cls, key: str) -> 'RiderPeriodOfEffort':
            Retrieve an instance from the cache using the provided key.
        add_to_cache(cls, key: str, instance: 'RiderPeriodOfEffort'):
            Add an instance to the cache with the provided key.
        clear_cache() -> None:
            Clear the cache of all stored instances.
        get_cache_contents() -> Dict[str, 'RiderPeriodOfEffort']:
            Get the contents of the cache.
        display_cache_contents() -> str:
            Display the contents of the cache in a readable format.
        get_or_create(rider: ZwiftRider, duration: float, speed: float, position_in_peloton: int) -> 'RiderPeriodOfEffort':
            Create a RiderPeriodOfEffort instance with the given parameters, calculating the wattage and energy burned.
    """

    _cache: Dict[str, 'RiderPeriodOfEffort'] = {}

    rider               : ZwiftRider = ZwiftRider()  # The Zwift rider participating in the period
    duration            : float      = 0             # The duration of the period in seconds
    speed               : float      = 0             # The speed during the period in kilometers per hour
    position_in_peloton : int        = 1             # The position of the rider in the peloton
    power_output        : float      = 0             # The average wattage in the rider's position
    energy_burned       : float      = 0             # The energy burned in the rider's position in kiloJoules

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "rider": {
                    "zwiftid": 58160,
                    "name": "John Hughes",
                    "weight": 75.4,
                    "height": 174,
                    "gender": "m",
                    "ftp": 233,
                    "zwift_racing_score": 351,
                    "velo_rating": 1067,
                },
                "duration": 30,
                "speed": 40,
                "position_in_peloton": 1,
                "power_output": 277,
                "energy_burned": 3
            }
        }

    @staticmethod
    def generate_key(rider: ZwiftRider, duration: float, speed: float, position_in_peloton: int) -> str:
        return ";".join([rider.get_key(), str(duration), str(speed), str(position_in_peloton)])

    @classmethod
    def get_from_cache(cls, key: Union[str, None]) -> Union['RiderPeriodOfEffort', None]:
        if key is None:
            return None
        return cls._cache.get(key)

    @classmethod
    def add_to_cache(cls, key: Union[str, None], instance: 'RiderPeriodOfEffort'):
        if key is None:
            return
        cls._cache[key] = instance

    @staticmethod
    def clear_cache() -> None:
        RiderPeriodOfEffort._cache.clear()

    @staticmethod
    def get_cache_contents() -> Dict[str, 'RiderPeriodOfEffort']:
        return RiderPeriodOfEffort._cache

    @staticmethod
    def display_cache_contents() -> str:
        if not RiderPeriodOfEffort._cache:
            return "Cache is empty."
        
        cache_contents = ["Cache contents:"]
        for key, effort in RiderPeriodOfEffort._cache.items():
            cache_contents.append(f"Key: {key}")
            cache_contents.append(f"  Rider: {effort.rider.name}")
            cache_contents.append(f"  Duration: {effort.duration}")
            cache_contents.append(f"  Speed: {effort.speed}")
            cache_contents.append(f"  Position in Peloton: {effort.position_in_peloton}")
            cache_contents.append(f"  Power Output: {effort.power_output}")
            cache_contents.append(f"  Energy Burned: {effort.energy_burned}")
            cache_contents.append("")  # Add a blank line for readability
        
        return "\n".join(cache_contents)

    @staticmethod
    def get_or_create(rider: ZwiftRider, duration: float, speed: float, position_in_peloton: int) -> 'RiderPeriodOfEffort':
        """
        Create a RiderPeriodOfEffort instance with the given parameters, calculating 
        the wattage and energy burned and using the cache if available.

        Args:
            rider (ZwiftRider): The Zwift rider participating in the period.
            duration (float): The duration of the period in seconds.
            speed (float): The speed during the period in kilometers per hour.
            position_in_peloton (int): The position of the rider in the peloton.

        Returns:
            RiderPeriodOfEffort: An instance of RiderPeriodOfEffort with the calculated 
            power output and energy burned.
        """

        key = RiderPeriodOfEffort.generate_key(rider, duration, speed, position_in_peloton)
        cached_instance = RiderPeriodOfEffort.get_from_cache(key)
        if cached_instance:
            return cached_instance

        wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position_in_peloton)
        energy = estimate_joules_from_wattage_and_time(wattage, duration)/1000

        instance = RiderPeriodOfEffort(
            rider=rider,
            duration=duration,
            speed=speed,
            position_in_peloton=position_in_peloton,
            power_output=wattage,
            energy_burned=energy
        )

        RiderPeriodOfEffort.add_to_cache(key, instance)
        return instance

def main():
    import logging
    from jgh_logging import jgh_configure_logging
    from tabulate import tabulate

    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Create ZwiftRider instances
    rider1 = ZwiftRider(
        name="John H",
        weight=75.4,
        height=174,
        gender=Gender.MALE,
        ftp=230,
        zwift_racing_score=500,
        velo_rating=1200,
    )

    rider2 = ZwiftRider(
        name="Mark B",
        weight=90.0,
        height=183,
        gender=Gender.MALE,
        ftp=255,
        zwift_racing_score=450,
        velo_rating=1100,
    )

    # Create RiderPeriodOfEffort instances for position 1 in the peloton
    rider1_effort_pos1 = RiderPeriodOfEffort.get_or_create(
        rider=rider1,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=1
    )

    rider2_effort_pos1 = RiderPeriodOfEffort.get_or_create(
        rider=rider2,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=1
    )

    # Create RiderPeriodOfEffort instances for position 2 in the peloton
    rider1_effort_pos2 = RiderPeriodOfEffort.get_or_create(
        rider=rider1,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=2
    )

    rider2_effort_pos2 = RiderPeriodOfEffort.get_or_create(
        rider=rider2,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=2
    )

    # Prepare data for tabulation
    data_pos1 = [
        ["Rider", "Power Output (W)", "Energy Burned (kJ)"],
        [rider1_effort_pos1.rider.name, rider1_effort_pos1.power_output, rider1_effort_pos1.energy_burned],
        [rider2_effort_pos1.rider.name, rider2_effort_pos1.power_output, rider2_effort_pos1.energy_burned]
    ]

    data_pos2 = [
        ["Rider", "Power Output (W)", "Energy Burned (kJ)"],
        [rider1_effort_pos2.rider.name, rider1_effort_pos2.power_output, rider1_effort_pos2.energy_burned],
        [rider2_effort_pos2.rider.name, rider2_effort_pos2.power_output, rider2_effort_pos2.energy_burned]
    ]

    # Log the attributes of the instances in position 1
    logger.info("Position 1 in the peloton:")
    logger.info("\n" + tabulate(data_pos1, headers="firstrow", tablefmt="grid"))

    # Log the attributes of the instances in position 2
    logger.info("Position 2 in the peloton:")
    logger.info("\n" + tabulate(data_pos2, headers="firstrow", tablefmt="grid"))




if __name__ == "__main__":
    main()
