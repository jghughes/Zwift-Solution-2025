from typing import List, Tuple, Dict
import numpy as np
from numpy import ndarray
import logging

def distill_cp_metrics_from_wattages_per_second(datapoints: List[Tuple[int, float]], cp_test_duration_specs: List[int]) -> Dict[int, float]:
    """
    Segment the data into specified durations and calculate the maximum average power for each segment.

    Args:
        datapoints (List[Tuple[int, float]]): List of power wattages recorded per second for a period of one hour.
        cp_test_duration_specs (List[int]): List of required critical power timespan in seconds.

    Returns:
        Dict[int, float]: Dictionary where key is the cp timespan (sec) and value is power (W) for the timespan.
    """
    dict_of_riders_and_their_criticalpower_curve: Dict[int, float] = {}

    for duration in cp_test_duration_specs:
        max_avg_power: float = 0.0
        num_intervals: int = 3600 - duration + 1

        # Calculate the sum of the first interval
        interval_sum: float = sum(datapoints[j][1] for j in range(duration))
        max_avg_power = interval_sum / duration

        # Use sliding window technique to calculate the sum of subsequent intervals
        for i in range(1, num_intervals):
            interval_sum = interval_sum - datapoints[i - 1][1] + datapoints[i + duration - 1][1]
            avg_power: float = interval_sum / duration
            if avg_power > max_avg_power:
                max_avg_power = avg_power

        dict_of_riders_and_their_criticalpower_curve[duration] = max_avg_power

    return dict_of_riders_and_their_criticalpower_curve

def linearize_cp_metrics(cp_interval_data: Dict[int, float]) -> Tuple[ndarray, ndarray]:
    """
    Linearize the data by plotting the average power output against the inverse of the duration.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary where keys are segment durations and values are average power outputs.

    Returns:
        Tuple[ndarray, ndarray]: Arrays of inverse durations and average power outputs.
    """
    durations: ndarray = np.array(list(cp_interval_data.keys()))
    avg_powers: ndarray = np.array(list(cp_interval_data.values()))
    inverse_durations: ndarray = 1 / durations
    return inverse_durations, avg_powers

def make_bestfit_cp_model(inverse_durations: ndarray, avg_powers: ndarray) -> Tuple[float, float]:
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
    return float(slope), float(intercept)


def deduce_cp_and_w_prime_from_bestfit_model(slope: float, intercept: float) -> Tuple[float, float]:
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

def estimate_cp_and_w_prime(cp_interval_data: Dict[int, float]) -> Tuple[float, float]:
    """
    Calculate Critical Power (CP) and Work Capacity Above CP (W') for a rider.

    Args:
        cp_interval_data (List[Tuple[int, float]]): List of power cp_interval_data for one hour.
        criticalpower_timespans (List[int]): List of segment durations in seconds.
        high_intensity_threshold (float): Power output threshold for high-intensity efforts.
        moderate_intensity_threshold (float): Power output threshold for moderate efforts.
        recovery_rate (float): Rate at which fatigue is recovered during low-intensity efforts.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
   
    inverse_durations, avg_powers = linearize_cp_metrics(cp_interval_data)
    slope, intercept = make_bestfit_cp_model(inverse_durations, avg_powers)
    cp, w_prime = deduce_cp_and_w_prime_from_bestfit_model(slope, intercept)
    return cp, w_prime

# Example usage
def main() -> None:
    # Configure logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from zwiftrider_related_items import RiderExertionItem

    # Sample data for testing
    efforts1: List[RiderExertionItem] = [
        RiderExertionItem(duration=10, wattage=300),
        RiderExertionItem(duration=5, wattage=150),
        RiderExertionItem(duration=5, wattage=250),
    ]

    output: List[Tuple[int, float]] = generate_rider_power_datapoints_for_one_hour(efforts1)

    # Segment durations
    criticalpower_timespans: List[int] = [5, 15, 30, 60, 120, 180, 300, 600, 720, 900, 1200, 1800, 2400, 3600]

    # Calculate Critical Power and W' with complex fatigue model
    cp, w_prime = calculate_cp_and_w_prime(output, criticalpower_timespans, high_intensity_threshold=250, moderate_intensity_threshold=200, recovery_rate=0.05)
    logger.info(f"Estimated CP: {cp:.2f} watts")
    logger.info(f"Estimated W': {w_prime:.2f} joules")

if __name__ == "__main__":
    main()
