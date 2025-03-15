
from pydantic import BaseModel
from models01 import *

class RiderQuantumOfEffort(BaseModel):
    """
    A class representing the effort of a Zwift rider in a specified period 
    of a multi-period rotation, based on his position in the peloton at the time
    of the effort.

    Attributes:
        rider                : ZwiftRider The Zwift rider participating in the period.
        duration             : float      The duration of the period in seconds.
        speed                : float      The speed during the period in kilometers per hour.
        distance             : float      The distance covered during the period in meters.
        position_in_peloton  : int        The position of the rider in the peloton.
        power_output         : float      The average wattage in the rider's position.
        energy_burned        : float      The energy burned in the rider's position in kiloJoules.

    Methods:
        create(rider: ZwiftRider, duration: float, speed: float, distance: float, position: int) -> 'RiderQuantumOfEffort':
            Create an RiderQuantumOfEffort instance with the given parameters, calculating the wattage and energy burned.
    """

    rider               : ZwiftRider = ZwiftRider()  # The Zwift rider participating in the period
    duration            : float      = 0             # The duration of the period in seconds
    speed               : float      = 0             # The speed during the period in kilometers per hour
    distance            : float      = 0             # The distance covered during the period in meters
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
            }
        }

    @staticmethod
    def create(rider: ZwiftRider, duration: float, speed: float, distance: float, position_in_peloton: int) -> 'RiderQuantumOfEffort':

        speed, duration, distance = triangulate_speed_time_and_distance(speed, duration, distance)
        wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position_in_peloton)
        energy = estimate_joules_from_wattage_and_time(wattage, duration)/1000

        instance = RiderQuantumOfEffort(
            rider=rider,
            duration=duration,
            speed=speed,
            distance=distance,
            position_in_peloton=position_in_peloton,
            power_output=wattage,
            energy_burned=energy
        )

        return instance

def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Create a ZwiftRider instance
    rider = ZwiftRider(
        name="John H",
        weight=75.4,
        height=174,
        gender=Gender.MALE,
        ftp=230,
        zwift_racing_score=500,
        velo_rating=1200,
    )

    # Create the first RiderQuantumOfEffort instance
    rider_action1 = RiderQuantumOfEffort.create(
        rider=rider,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        distance=0.0, # distance in meters
        position_in_peloton=1      # position in peloton
    )

    # Create the second RiderQuantumOfEffort instance
    rider_action2 = RiderQuantumOfEffort.create(
        rider=rider,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        distance=0.0, # distance in meters
        position_in_peloton=5      # position in peloton
    )


    # Log the attributes of the first instance
    logger.info("Pulling position:")
    logger.info(f"{'Rider:':<20} {rider_action1.rider.name}")
    logger.info(f"{'Duration:':<20} {rider_action1.duration} seconds")
    logger.info(f"{'Speed:':<20} {rider_action1.speed} km/h")
    logger.info(f"{'Distance:':<20} {rider_action1.distance} meters")
    logger.info(f"{'Position in Peloton:':<20} {rider_action1.position_in_peloton}")
    logger.info(f"{'Power Output:':<20} {rider_action1.power_output} watts")
    logger.info(f"{'Energy Burned:':<20} {rider_action1.energy_burned} kJ")

    # Log the attributes of the second instance
    logger.info("Resting position:")
    logger.info(f"{'Rider:':<20} {rider_action2.rider.name}")
    logger.info(f"{'Duration:':<20} {rider_action2.duration} seconds")
    logger.info(f"{'Speed:':<20} {rider_action2.speed} km/h")
    logger.info(f"{'Distance:':<20} {rider_action2.distance} meters")
    logger.info(f"{'Position in Peloton:':<20} {rider_action2.position_in_peloton}")
    logger.info(f"{'Power Output:':<20} {rider_action2.power_output} watts")
    logger.info(f"{'Energy Burned:':<20} {rider_action2.energy_burned} kJ")

if __name__ == "__main__":
    main()