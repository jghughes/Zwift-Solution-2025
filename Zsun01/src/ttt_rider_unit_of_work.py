from pydantic import BaseModel
from jgh_formulae import *
from zwiftrider_item import ZwiftRiderItem


class RiderUnitOfWork(BaseModel):
    """
    A class representing the effort of a Zwift rider in a specified period 
    of a multi-period rotation, based on his position in the peloton at the time
    of the effort.

    Attributes:
        rider               (ZwiftRiderItem): The Zwift rider participating in the period.
        duration            (float)         : The duration of the period in seconds.
        speed               (float)         : The speed during the period in kilometers per hour.
        position_in_peloton (int)           : The position of the rider in the peloton.
        power_output        (float)         : The average wattage in the rider's position.
        energy_burned       (float)         : The energy burned in the rider's position in kiloJoules.
    """

    rider               : ZwiftRiderItem = ZwiftRiderItem()  # The Zwift rider participating in the period
    duration            : float      = 0             # The duration of the period in seconds
    speed               : float      = 0             # The speed during the period in kilometers per hour
    position_in_peloton : int        = 1             # The position of the rider in the peloton
    power_output        : float      = 0             # The average wattage in the rider's position
    energy_burned       : float      = 0             # The energy burned in the rider's position in kiloJoules

    class Config:
        frozen = True
        json_schema_extra = {
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
                "duration": 30,
                "speed": 40,
                "position_in_peloton": 1,
        }

       
    @staticmethod
    def create(rider: ZwiftRiderItem, duration: float, speed: float, position_in_peloton: int) -> 'RiderUnitOfWork':
        """
        Create a RiderUnitOfWork instance with the given parameters, calculating 
        the wattage and energy burned and using the cache if available.

        Args:
            rider               (ZwiftRiderItem): The Zwift rider participating in the period.
            duration            (float)         : The duration of the period in seconds.
            speed               (float)         : The speed during the period in kilometers per hour.
            position_in_peloton (int)           : The position of the rider in the peloton.
            power_output        (float)         : The average wattage in the rider's position.
            energy_burned       (float)         : The energy burned in the rider's position in kiloJoules.

        Returns:
            RiderUnitOfWork: An instance of RiderUnitOfWork with the calculated 
            power output and energy burned.
        """


        wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position_in_peloton)
        energy = estimate_joules_from_wattage_and_time(wattage, duration)/1000

        instance = RiderUnitOfWork(
            rider=rider,
            duration=duration,
            speed=speed,
            position_in_peloton=position_in_peloton,
            power_output=wattage,
            energy_burned=energy
        )

        return instance


    @staticmethod
    def make_identifier(rider: ZwiftRiderItem, duration: float, speed: float, position_in_peloton: int) -> str:
        """
        Generate a unique identifier based on the rider, duration, speed, and position in the peloton.

        Args:
            rider               (ZwiftRiderItem): The Zwift rider participating in the period.
            duration            (float)         : The duration of the period in seconds.
            speed               (float)         : The speed during the period in kilometers per hour.
            position_in_peloton (int)           : The position of the rider in the peloton.
            power_output        (float)         : The average wattage in the rider's position.
            energy_burned       (float)         : The energy burned in the rider's position in kiloJoules.

        Returns:
            str: A unique key representing the RiderUnitOfWork instance.
        """
        return ";".join([
            rider.get_key(), str(duration), str(speed), str(position_in_peloton)
        ])

    def get_identifier(self) -> str:
        """
        Generate an identifier for the current RiderUnitOfWork instance.

        Returns:
            str: A unique key representing the RiderUnitOfWork instance.
        """
        return self.make_identifier(self.rider, self.duration, self.speed, self.position_in_peloton)


def main():

    from tabulate import tabulate

    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Create ZwiftRiderItem instances
    example_data = ZwiftRiderItem.Config.json_schema_extra["johnh"]
    rider_john = ZwiftRiderItem.model_validate(example_data)

    example_data = ZwiftRiderItem.Config.json_schema_extra["markb"]
    rider_mark = ZwiftRiderItem.model_validate(example_data)

    # Create RiderUnitOfWork instances for position 1 in the peloton
    rider_john_effort_pos1 = RiderUnitOfWork.create(
        rider=rider_john,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=1
    )

    rider_mark_effort_pos1 = RiderUnitOfWork.create(
        rider=rider_mark,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=1
    )

    # Create RiderUnitOfWork instances for position 2 in the peloton
    rider_john_effort_pos2 = RiderUnitOfWork.create(
        rider=rider_john,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=2
    )

    rider_mark_effort_pos2 = RiderUnitOfWork.create(
        rider=rider_mark,
        duration=30.0,  # duration in seconds
        speed=40.0,     # speed in km/h
        position_in_peloton=2
    )

    # Prepare data for tabulation
    data_pos1 = [
        ["Rider", "Power Output (W)", "Energy Burned (kJ)"],
        [rider_john_effort_pos1.rider.name, rider_john_effort_pos1.power_output, rider_john_effort_pos1.energy_burned],
        [rider_mark_effort_pos1.rider.name, rider_mark_effort_pos1.power_output, rider_mark_effort_pos1.energy_burned]
    ]

    data_pos2 = [
        ["Rider", "Power Output (W)", "Energy Burned (kJ)"],
        [rider_john_effort_pos2.rider.name, rider_john_effort_pos2.power_output, rider_john_effort_pos2.energy_burned],
        [rider_mark_effort_pos2.rider.name, rider_mark_effort_pos2.power_output, rider_mark_effort_pos2.energy_burned]
    ]

    # Log the attributes of the instances in position 1
    logger.info("Position 1 in the peloton:")
    logger.info("\n" + tabulate(data_pos1, headers="firstrow", tablefmt="grid"))

    # Log the attributes of the instances in position 2
    logger.info("Position 2 in the peloton:")
    logger.info("\n" + tabulate(data_pos2, headers="firstrow", tablefmt="grid"))

if __name__ == "__main__":
    main()
