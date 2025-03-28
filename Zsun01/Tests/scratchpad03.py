from typing import List, Tuple, Dict
import numpy as np
from numpy import ndarray
import logging
from jgh_formulae05 import RiderEffortItem

def generate_rider_power_datapoints_for_one_hour(efforts: List[RiderEffortItem]) -> List[Tuple[int, float]]:
    """
    Generate rider power datapoints for one hour.

    Args:
        efforts (List[RiderEffortItem]): List of rider efforts.

    Returns:
        List[Tuple[int, float]]: List of power datapoints for one hour.
    """
    # Step 1: Generate a succession of repetitions of the input list of RiderEffortItem
    total_duration = sum(effort.duration for effort in efforts)
    repetitions = int((3600 // total_duration) + 1)
    extended_efforts: List[RiderEffortItem] = [effort for _ in range(repetitions) for effort in efforts]
    
    # Step 2: Generate a datapoint of (t, wattage) for every second up until t=3600
    datapoints: List[Tuple[int, float]] = [(0, 0.0)] * 3601  # Preallocate list with 3601 elements
    current_time: int = 0
    effort_index: int = 0
    current_effort: RiderEffortItem = extended_efforts[effort_index]
    effort_time: int = 0
    
    while current_time <= 3600:
        if effort_time >= current_effort.duration:
            effort_index += 1
            current_effort = extended_efforts[effort_index]
            effort_time = 0
        
        datapoints[current_time] = (current_time, current_effort.wattage)
        current_time += 1
        effort_time += 1
    
    return datapoints[:3600]  # Ensure the list is exactly 3600 elements long

def segment_data(datapoints: List[Tuple[int, float]], segment_durations: List[int]) -> Dict[int, float]:
    """
    Segment the data into specified durations and calculate the average power for each segment.

    Args:
        datapoints (List[Tuple[int, float]]): List of power datapoints for one hour.
        segment_durations (List[int]): List of segment durations in seconds.

    Returns:
        Dict[int, float]: Dictionary where keys are segment durations and values are average power outputs.
    """
    segmented_data: Dict[int, float] = {}
    for duration in segment_durations:
        num_segments: int = len(datapoints) // duration
        avg_power: float = np.mean([np.mean([wattage for _, wattage in datapoints[i*duration:(i+1)*duration]]) for i in range(num_segments)])
        segmented_data[duration] = avg_power
    return segmented_data

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

def calculate_critical_power(datapoints: List[Tuple[int, float]]) -> Tuple[float, float]:
    """
    Calculate Critical Power (CP) and Work Capacity Above CP (W') for a rider.

    Args:
        datapoints (List[Tuple[int, float]]): List of power datapoints for one hour.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
    segment_durations: List[int] = [5, 15, 30, 60, 180, 300, 600, 720, 900, 1200, 1800, 2400, 3600]
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

    # Calculate Critical Power and W'
    cp, w_prime = calculate_critical_power(output)
    logger.info(f"Estimated CP: {cp:.2f} watts")
    logger.info(f"Estimated W': {w_prime:.2f} joules")

if __name__ == "__main__":
    main()
