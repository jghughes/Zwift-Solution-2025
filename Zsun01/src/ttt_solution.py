import logging

from jgh_logging import jgh_configure_logging
from zwiftrider_related_items import RiderRotationItem
from pydantic import BaseModel
from typing import List, Tuple, Dict, Set
from zwiftrider_item import *
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
optimal_rotations: Dict[int, RiderRotationItem] = {}

# Counters for inspected, valid, and invalid alternatives
inspected_count: int = 0
valid_count: int = 0
invalid_count: int = 0


class SolutionLineItem(BaseModel):

    rank : int = 1
    rider : ZwiftRiderItem
    pull_duration : float = 0.0
    pull_speed : float = 0.0
    pull_watts: float = 0.0
    pull_wkg : float = 0.0

    wattage_position_3 : float = 0.0
    wattage_position_4 : float = 0.0
    wattage_position_5 : float = 0.0
    energy_intensity_factor : float = 1.0

class Solution(BaseModel):
    speed : float = 0
    distance_of_rotation : float = 0
    total_time : float = 0
    lineitems : list[SolutionLineItem] = []
    
def validate_wattage(duration: int, speed: float, riders: List[ZwiftRiderItem]) -> bool:
    for rider in riders:
        interval = RiderPeriodOfEffort.get_or_create(rider, duration, speed, 0, 1)
        max_allowed_wattage = MAX_POWER_INTENSITY * rider.ftp
        if interval.power_output > max_allowed_wattage:
            return False
    return True

def calculate_total_combinations(riders: List[ZwiftRiderItem], num_periods: int) -> int:
    total_combinations: int = 0
    for team_size in range(1, len(riders) + 1):
        combinations: int = comb(len(riders), team_size) * (len(VALID_DURATIONS) ** num_periods)
        total_combinations += combinations
    return total_combinations

def explore_rotations(riders: List[ZwiftRiderItem], speeds: List[float], current_periods: List[TttWorkPeriod] = [], depth: int = 0) -> None:
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
            #     logger.info(f"{indent}TttWorkPeriod {i}: Duration = {period.duration} sec, Speed = {period.speed} km/h, Total Energy Burned = {period.total_energy_burned()} kJ")

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
            new_periods: List[TttWorkPeriod] = current_periods + [TttWorkPeriod(duration=duration, speed=speeds[len(current_periods)], riders=riders)]
            explore_rotations(riders, speeds, new_periods, depth + 1)
        else:
            # logger.info(f"{indent}Skipping invalid period with duration {duration} for period {len(current_periods) + 1}")
            pass

    # Recursive reduction: explore rotations with one less rider
    if len(riders) > 1:
        for i in range(len(riders)):
            new_riders: List[ZwiftRiderItem] = riders[:i] + riders[i+1:]
            # logger.info(f"{indent}Exploring rotation with one less rider: {riders[i].name}")
            explore_rotations(new_riders, speeds, current_periods, depth + 1)

def main() -> None:
    # Example riders
    riders: List[ZwiftRiderItem] = [
        # ZwiftRiderItem(name="Rider_01", weight=70, height=175, gender=Gender.MALE, ftp=300, zwift_racing_score=600, velo_rating=1500),
        # ZwiftRiderItem(name="Rider_02", weight=68, height=178, gender=Gender.MALE, ftp=290, zwift_racing_score=610, velo_rating=1520),
        # ZwiftRiderItem(name="Rider_03", weight=72, height=180, gender=Gender.MALE, ftp=310, zwift_racing_score=620, velo_rating=1540),
        ZwiftRiderItem(name="Rider_04", weight=75, height=174, gender=Gender.MALE, ftp=230, zwift_racing_score=590, velo_rating=1180),
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
            logger.info(f"TttWorkPeriod {i}: Leader = {period.riders[0].name} Duration = {period.duration} sec, Speed = {period.speed} km/h, Total Energy Burned = {period.total_energy_burned()} kJ")

    # Log the summary of inspected alternatives
    logger.info(f"Total inspected alternatives: {inspected_count}")
    logger.info(f"Valid rotations: {valid_count}")
    logger.info(f"Invalid rotations: {invalid_count}")
    logger.info(f"Percentage of solution space inspected: {inspected_count / total_combinations * 100:.2f}%")

if __name__ == "__main__":
    main()
