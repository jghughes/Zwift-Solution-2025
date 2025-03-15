
from pydantic import BaseModel
from typing import List, Tuple
from models01 import *

class RiderQuantumOfAction(BaseModel):
    """
    A class representing an period of action for a Zwift rider.

    Attributes:
        rider                : ZwiftRider The Zwift rider participating in the period.
        duration             : float      The duration of the period in seconds.
        speed                : float      The speed during the period in kilometers per hour.
        distance             : float      The distance covered during the period in meters.
        position_in_peloton  : int        The position of the rider in the peloton.
        power_output         : float      The average wattage in the rider's position.
        energy_burned        : float      The energy burned in the rider's position in kiloJoules.

    Methods:
        create(rider: ZwiftRider, duration: float, speed: float, distance: float, position: int) -> 'RiderQuantumOfAction':
            Create an RiderQuantumOfAction instance with the given parameters, calculating the wattage and energy burned.
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
            },
            "description": {
                "rider": "The rider participating in the period",
                "duration": "The duration of the period in seconds",
                "speed": "The speed during the period in kilometers per hour",
                "distance": "The distance covered during the period in meters",
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
    def create(rider: ZwiftRider, duration: float, speed: float, distance: float, position: int) -> 'RiderQuantumOfAction':

        speed, duration, distance = triangulate_speed_time_and_distance(speed, duration, distance)
        wattage = rider.calculate_wattage_riding_in_the_peloton(speed, position)
        energy = estimate_joules_from_wattage_and_time(wattage, duration)/1000

        return RiderQuantumOfAction(
            rider=rider,
            duration=duration,
            speed=speed,
            distance=distance,
            position_in_peloton=position,
            power_output=wattage,
            energy_burned=energy
        )

    # Define the constants

class ActionPeriodWithinRotation(BaseModel):
    index : int = 1
    duration: float = 0.0
    speed: float = 0.0
    power_limit_factor : float = 1.0
    rider_actions: List[RiderQuantumOfAction] = []

    @staticmethod
    def create(index : int, riders: List[ZwiftRider], duration: int, speed: float, power_ceiling_factor : float, positions: List[int]) -> 'ActionPeriodWithinRotation':
        rider_actions = [RiderQuantumOfAction.create(rider, duration, speed, 0, position) for rider, position in zip(riders, positions)]
        return ActionPeriodWithinRotation(index = index, duration=duration, speed=speed, power_limit_factor=power_ceiling_factor, rider_actions=rider_actions)

    def find_overworked_riders(self) -> List[RiderQuantumOfAction]:
        return [rider_action for rider_action in self.rider_actions if rider_action.power_output > rider_action.rider.ftp * self.power_limit_factor]

    def actionperiod_is_too_hard(self) -> bool:
        # return false if find_riders_with_excessive_power any
        if self.find_overworked_riders():
            return False

        return True

class Rotation(BaseModel):
    speed : float = 0.0
    periods: List[ActionPeriodWithinRotation]

    def total_time(self) -> float:
        return sum(period.duration for period in self.periods)

    def total_distance(self) -> float:
        return sum(period.speed * (period.duration / 3600) for period in self.periods)

    def average_speed(self) -> float:
        return self.total_distance() / (self.total_time() / 3600)

    def to_tuple(self) -> Tuple[Tuple[float, float, str], ...]:
        """
        Convert the rotation instance to a tuple representation.

        Returns:
        Tuple[Tuple[float, float, str], ...]: A tuple containing the duration, speed, and concatenated rider names for this instance.
        """
        result: List[Tuple[float, float, str]] = []
        for period in self.periods:
            # Extract the duration and speed for the period
            duration: float = period.duration
            speed: float = period.speed
            # Concatenate the names of the riders in the period
            rider_names: str = ", ".join(rider_action.rider.name for rider_action in period.rider_actions)
            # Append the tuple (duration, speed, rider_names) to the result list
            result.append((duration, speed, rider_names))
        # Convert the result list to a tuple and return it
        return tuple(result)

    def validate_energy_constraint(self) -> None:
        total_time = self.total_time()
        for rider in self.periods[0].riders:
            total_energy_burned = sum(period.total_energy_burned() for period in self.periods if rider in period.riders)
            max_allowable_energy = estimate_joules_from_wattage_and_time(rider.ftp * energy_intensity, total_time) / 1000
            if total_energy_burned > max_allowable_energy:
                raise ValueError(f"Rider {rider.name} exceeds max allowable energy: {total_energy_burned} kJ > {max_allowable_energy} kJ")
