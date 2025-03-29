from typing import List, Tuple, Dict
import numpy as np
from numpy import ndarray
import logging
from jgh_formulae05 import RiderEffortItem


def linearize_cp_data(cp_datapoints: Dict[int, float]) -> Tuple[ndarray, ndarray]:
    """
    Linearize the data by plotting the average power output against the inverse of the duration.

    Args:
        cp_datapoints (Dict[int, float]): Dictionary where keys are segment durations and values are average power outputs.

    Returns:
        Tuple[ndarray, ndarray]: Arrays of inverse durations and average power outputs.
    """
    durations: ndarray = np.array(list(cp_datapoints.keys()))
    avg_powers: ndarray = np.array(list(cp_datapoints.values()))
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
    criticalpower_timespans: List[int] = [5, 15, 30, 60, 120, 180, 300, 600, 720, 900, 1200, 1800, 2400, 3600]

    # Calculate Critical Power and W' with complex fatigue model
    cp, w_prime = calculate_cp_and_w_prime(output, criticalpower_timespans, high_intensity_threshold=250, moderate_intensity_threshold=200, recovery_rate=0.05)
    logger.info(f"Estimated CP: {cp:.2f} watts")
    logger.info(f"Estimated W': {w_prime:.2f} joules")

if __name__ == "__main__":
    main()
