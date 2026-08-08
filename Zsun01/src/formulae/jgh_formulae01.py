from constants import (
    COEFFICIENT_bike_weight_kg,
    AERO_POSITION_FACTOR_DEFAULT,
    DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC,
)
from jgh_formulae00 import calculate_velocity_from_power, calculate_power_from_velocity


def calculate_rider_watts_from_kph(speed_kph: float, rider_weight: float, rider_height: float, slope_pc: float = DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """ 
    Estimate the power (wattage) given the speed (km/h), weight (kg), height (cm), and slope (%)
    """
    rider_plus_bike_mass: float = rider_weight + COEFFICIENT_bike_weight_kg
    wattage: float = calculate_power_from_velocity(speed_kph, rider_height, rider_plus_bike_mass, slope_pc, aero_factor)
    return wattage

def calculate_rider_kph_from_watts(wattage: float, rider_weight: float, rider_height: float, slope_pc: float = DEFAULT_SLOPE_FOR_ALL_PACELINE_CALCULATIONS_PC, aero_factor: float = AERO_POSITION_FACTOR_DEFAULT) -> float:
    """
    Estimate the speed (km/h) given the power (wattage), weight (kg), height (cm), and slope (%)
    """
    rider_plus_bike_mass: float = rider_weight + COEFFICIENT_bike_weight_kg
    speed_kmh: float = calculate_velocity_from_power(wattage, rider_height, rider_plus_bike_mass, slope_pc, aero_factor)
    return speed_kmh

