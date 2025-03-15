import logging
from jgh_logging import jgh_configure_logging
import numpy as np
from pydantic import BaseModel
from typing import List, Tuple, Dict, Set
from models import ZwiftRider, Interval, Gender, estimate_joules_from_wattage_and_time
from math import comb

# Configure logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

# Define the constants
MAX_POWER_INTENSITY: float = 1.3
energy_intensity: float = 1.0  # Global variable with default value 1.0

# Define valid durations
VALID_DURATIONS: List[int] = [15, 30, 60, 90, 120, 180]

# Sets to store invalid and valid rotations
invalid_rotations: Set[Tuple] = set()
valid_rotations: Set[Tuple] = set()

# Dictionary to store the optimal rotation for each team size
optimal_rotations: Dict[int, 'Rotation'] = {}

# Counters for inspected, valid, and invalid alternatives
inspected_count: int = 0
valid_count: int = 0
invalid_count: int = 0

class Period(BaseModel):
    duration: int
    speed: float
    riders: List[ZwiftRider]
    intervals: List[Interval] = []

    def __init__(self, **data):
        super().__init__(**data)
        if self.duration not in VALID_DURATIONS:
            raise ValueError(f"Invalid duration: {self.duration}. Must be one of {VALID_DURATIONS}.")
        self.intervals = [Interval.create(rider, self.duration, self.speed, 0, 1) for rider in self.riders]

    def total_energy_burned(self) -> float:
        return sum(interval.energy_burned * energy_intensity for interval in self.intervals)

class Rotation(BaseModel):
    periods: List[Period]

    def total_time(self) -> int:
        return sum(period.duration for period in self.periods)

    def average_speed(self) -> float:
        total_distance = sum(period.speed * (period.duration / 3600) for period in self.periods)
        return total_distance / (self.total_time() / 3600)

    def to_tuple(self) -> Tuple:
        return tuple((period.duration, period.speed, tuple(rider.name for rider in period.riders)) for period in self.periods)

    def validate_energy_constraint(self) -> None:
        total_time = self.total_time()
        for rider in self.periods[0].riders:
            total_energy_burned = sum(period.total_energy_burned() for period in self.periods if rider in period.riders)
            max_allowable_energy = estimate_joules_from_wattage_and_time(rider.ftp * energy_intensity, total_time) / 1000
            if total_energy_burned > max_allowable_energy:
                raise ValueError(f"Rider {rider.name} exceeds max allowable energy: {total_energy_burned} kJ > {max_allowable_energy} kJ")

def validate_wattage(duration: int, speed: float, riders: List[ZwiftRider]) -> bool:
    for rider in riders:
        interval = Interval.create(rider, duration, speed, 0, 1)
        max_allowed_wattage = MAX_POWER_INTENSITY * rider.ftp
        if interval.power_output > max_allowed_wattage:
            return False
    return True

def calculate_total_combinations(riders: List[ZwiftRider], num_periods: int) -> int:
    total_combinations: int = 0
    for team_size in range(1, len(riders) + 1):
        combinations: int = comb(len(riders), team_size) * (len(VALID_DURATIONS) ** num_periods)
        total_combinations += combinations
    return total_combinations

def explore_rotations(riders: List[ZwiftRider], speeds: List[float], current_periods: List[Period] = [], depth: int = 0) -> None:
    global inspected_count, valid_count, invalid_count
    # indent: str = "  " * depth
    if len(current_periods) == len(speeds):
        rotation_tuple: Tuple = tuple((period.duration, period.speed, tuple(rider.name for rider in period.riders)) for period in current_periods)

        if rotation_tuple in invalid_rotations:
            # logger.info(f"{indent}Rotation is already known to be invalid.")
            return
        if rotation_tuple in valid_rotations:
            # logger.info(f"{indent}Rotation is already known to be valid.")
            return

        try:
            rotation = Rotation(periods=current_periods)
            rotation.validate_energy_constraint()

            # logger.info(f"{indent}Total Time of Rotation: {rotation.total_time()} seconds")
            # logger.info(f"{indent}Average Speed of Rotation: {rotation.average_speed()} km/h")

            # for i, period in enumerate(rotation.periods, start=1):
            #     logger.info(f"{indent}Period {i}: Duration = {period.duration} sec, Speed = {period.speed} km/h, Total Energy Burned = {period.total_energy_burned()} kJ")

            valid_rotations.add(rotation.to_tuple())
            # logger.info(f"{indent}Rotation is valid and archived.")

            # Archive the optimal rotation for the current team size
            team_size: int = len(current_periods[0].riders)
            if team_size not in optimal_rotations or rotation.average_speed() > optimal_rotations[team_size].average_speed():
                optimal_rotations[team_size] = rotation
                # logger.info(f"{indent}New optimal rotation for team size {team_size} archived.")
            valid_count += 1
        except ValueError as e:
            # logger.error(f"{indent}Invalid rotation: {e}")
            invalid_rotations.add(rotation_tuple)
            # logger.info(f"{indent}Rotation is invalid and archived.")
            invalid_count += 1
        inspected_count += 1
        return

    for duration in VALID_DURATIONS:
        if validate_wattage(duration, speeds[len(current_periods)], riders):
            # logger.info(f"{indent}Exploring branch with duration {duration} for period {len(current_periods) + 1}")
            new_periods: List[Period] = current_periods + [Period(duration=duration, speed=speeds[len(current_periods)], riders=riders)]
            explore_rotations(riders, speeds, new_periods, depth + 1)
        else:
            # logger.info(f"{indent}Skipping invalid period with duration {duration} for period {len(current_periods) + 1}")
            pass

    # Recursive reduction: explore rotations with one less rider
    if len(riders) > 1:
        for i in range(len(riders)):
            new_riders: List[ZwiftRider] = riders[:i] + riders[i+1:]
            # logger.info(f"{indent}Exploring rotation with one less rider: {riders[i].name}")
            explore_rotations(new_riders, speeds, current_periods, depth + 1)

def main() -> None:
    # Example riders
    riders: List[ZwiftRider] = [
        # ZwiftRider(name="Rider_01", weight=70, height=175, gender=Gender.MALE, ftp=300, zwift_racing_score=600, velo_rating=1500),
        # ZwiftRider(name="Rider_02", weight=68, height=178, gender=Gender.MALE, ftp=290, zwift_racing_score=610, velo_rating=1520),
        # ZwiftRider(name="Rider_03", weight=72, height=180, gender=Gender.MALE, ftp=310, zwift_racing_score=620, velo_rating=1540),
        ZwiftRider(name="Rider_04", weight=75, height=174, gender=Gender.MALE, ftp=230, zwift_racing_score=590, velo_rating=1180),
    ]

    # Define speeds for each period
    # speeds: List[float] = [40, 42, 44, 41]
    speeds: List[float] = [50]

    # Calculate total combinations
    total_combinations: int = calculate_total_combinations(riders, len(speeds))
    logger.info(f"Total combinations to explore: {total_combinations}")

    # Explore all rotations sequentially
    explore_rotations(riders, speeds)

    # Log the optimal rotations for each team size
    for team_size, rotation in optimal_rotations.items():
        logger.info(f"Optimal rotation for team size {team_size}:")
        logger.info(f"Total Time: {rotation.total_time()} seconds")
        logger.info(f"Average Speed: {rotation.average_speed()} km/h")
        for i, period in enumerate(rotation.periods, start=1):
            logger.info(f"Period {i}: Leader = {period.riders[0].name} Duration = {period.duration} sec, Speed = {period.speed} km/h, Total Energy Burned = {period.total_energy_burned()} kJ")

    # Log the summary of inspected alternatives
    logger.info(f"Total inspected alternatives: {inspected_count}")
    logger.info(f"Valid rotations: {valid_count}")
    logger.info(f"Invalid rotations: {invalid_count}")
    logger.info(f"Percentage of solution space inspected: {inspected_count / total_combinations * 100:.2f}%")

if __name__ == "__main__":
    main()
