from typing import List, Tuple, Dict
import numpy as np
from numpy import ndarray
import logging
from jgh_formulae05 import RiderEffortItem
from jgh_formulae08 import generate_rider_power_datapoints_for_one_hour, apply_complex_fatigue_model, segment_data

def apply_complex_fatigue_model(datapoints: List[Tuple[int, float]], high_intensity_threshold: float, moderate_intensity_threshold: float, recovery_rate: float) -> List[Tuple[int, float]]:
    """
    Apply a complex fatigue model to the power data.

    Args:
        datapoints (List[Tuple[int, float]]): List of power datapoints for one hour.
        high_intensity_threshold (float): Power output threshold for high-intensity efforts.
        moderate_intensity_threshold (float): Power output threshold for moderate efforts.
        recovery_rate (float): Rate at which fatigue is recovered during low-intensity efforts.

    Returns:
        List[Tuple[int, float]]: Adjusted power datapoints accounting for fatigue.
    """
    adjusted_datapoints: List[Tuple[int, float]] = []
    fatigue: float = 0.0

    for t, wattage in datapoints:
        if wattage > high_intensity_threshold:
            fatigue += 0.02 * wattage  # High-intensity effort increases fatigue quickly
        elif wattage > moderate_intensity_threshold:
            fatigue += 0.01 * wattage  # Moderate effort increases fatigue moderately
        else:
            fatigue -= recovery_rate * fatigue  # Recovery effort decreases fatigue

        fatigue = max(fatigue, 0)  # Ensure fatigue does not go below zero
        adjusted_wattage = wattage * (1 - fatigue / 1000)  # Adjust power output based on fatigue
        adjusted_datapoints.append((t, adjusted_wattage))

    return adjusted_datapoints


def linearize_data(segmented_data: Dict[int, float]) -> Tuple[ndarray, ndarray]:
    """
    Linearize the data by plotting the average power output against the inverse of the duration.

    Args:
        segmented_data (Dict[int, float]): Dictionary where keys are segment durations and values are average power outputs.

    Returns:
        Tuple[ndarray, ndarray]: Arrays of inverse durations and average power outputs.
    """
    durations: ndarray = np.array(list(segmented_data.keys()))
    avg_powers: ndarray = np.array(list(segmented_data.values()))
    inverse_durations: ndarray = 1 / durations
    return inverse_durations, avg_powers

def fit_model(inverse_durations: ndarray, avg_powers: ndarray) -> Tuple[float, float]:
    """
    Fit a linear model to the linearized data.

    Args:
        inverse_durations (ndarray): Array of inverse durations.
        avg_powers (ndarray): Array of average power outputs.

    Returns:
        Tuple[float, float]: Slope and intercept of the fitted line.
    """
    A: ndarray = np.vstack([inverse_durations, np.ones(len(inverse_durations))]).T
    slope: float
    intercept: float
    slope, intercept = np.linalg.lstsq(A, avg_powers, rcond=None)[0]
    return slope, intercept

def extract_cp_and_w_prime(slope: float, intercept: float) -> Tuple[float, float]:
    """
    Extract CP and W' from the fitted model.

    Args:
        slope (float): Slope of the fitted line.
        intercept (float): Intercept of the fitted line.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
    cp: float = intercept
    w_prime: float = slope * cp
    return cp, w_prime

def calculate_critical_power(datapoints: List[Tuple[int, float]], segment_durations: List[int], high_intensity_threshold: float, moderate_intensity_threshold: float, recovery_rate: float) -> Tuple[float, float]:
    """
    Calculate Critical Power (CP) and Work Capacity Above CP (W') for a rider.

    Args:
        datapoints (List[Tuple[int, float]]): List of power datapoints for one hour.
        segment_durations (List[int]): List of segment durations in seconds.
        high_intensity_threshold (float): Power output threshold for high-intensity efforts.
        moderate_intensity_threshold (float): Power output threshold for moderate efforts.
        recovery_rate (float): Rate at which fatigue is recovered during low-intensity efforts.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
    datapoints = apply_complex_fatigue_model(datapoints, high_intensity_threshold, moderate_intensity_threshold, recovery_rate)
    
    segmented_data: Dict[int, float] = segment_data(datapoints, segment_durations)
    inverse_durations, avg_powers = linearize_data(segmented_data)
    slope, intercept = fit_model(inverse_durations, avg_powers)
    cp, w_prime = extract_cp_and_w_prime(slope, intercept)
    return cp, w_prime

# Example usage
def main() -> None:
    # Configure logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Sample data for testing
    efforts1: List[RiderEffortItem] = [
        RiderEffortItem(duration=10, wattage=300),
        RiderEffortItem(duration=5, wattage=150),
        RiderEffortItem(duration=5, wattage=250),
    ]

    output: List[Tuple[int, float]] = generate_rider_power_datapoints_for_one_hour(efforts1)

    # Segment durations
    segment_durations: List[int] = [5, 15, 30, 60, 120, 180, 300, 600, 720, 900, 1200, 1800, 2400, 3600]

    # Calculate Critical Power and W' with complex fatigue model
    cp, w_prime = calculate_critical_power(output, segment_durations, high_intensity_threshold=250, moderate_intensity_threshold=200, recovery_rate=0.05)
    logger.info(f"Estimated CP: {cp:.2f} watts")
    logger.info(f"Estimated W': {w_prime:.2f} joules")

if __name__ == "__main__":
    main()
