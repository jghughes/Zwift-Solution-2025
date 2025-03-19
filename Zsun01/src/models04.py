from pydantic import BaseModel
from typing import List, Tuple
from zwiftrider_item import ZwiftRiderItem
from models02 import *
from models03 import *

class TttTeamOfRiders(BaseModel):
    riders_working : list[ZwiftRiderItem] = []
    riders_resting : list[ZwiftRiderItem] = []
    
    @staticmethod
    def create(riders: list[ZwiftRiderItem]) -> 'TttTeamOfRiders':
        riders.sort(key=lambda x: x.calculate_strength(), reverse=True)
        #assign rank to rank attr sarting with 1
        for i, rider in enumerate(riders):
            rider.rank = i+1
        team = TttTeamOfRiders(riders_working = riders, riders_resting=[])
        return team

    def sort_riders(self) -> None:
        self.riders_working.sort(key=lambda x: x.calculate_strength(), reverse=True)
        self.riders_resting.sort(key=lambda x: x.calculate_strength(), reverse=True)

    def demote_rider_from_working_to_resting(self, rider: ZwiftRiderItem) -> None:
        self.riders_resting.append(rider)
        self.riders_working.remove(rider)
        self.sort_riders()

    def promote_rider_from_resting_to_working(self, rider: ZwiftRiderItem) -> None:
        self.riders_working.append(rider)
        self.riders_resting.remove(rider)
        self.sort_riders()

class Rotation(BaseModel):
    speed : float = 0.0
    periods: List[TttWorkPeriod]

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
