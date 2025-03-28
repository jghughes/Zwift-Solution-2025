import numpy as np
from typing import List, Tuple
from jgh_formulae05 import RiderEffortItem
import logging

def estimate_cp_and_w_prime(efforts: List[RiderEffortItem]) -> Tuple[float, float]:
    """
    Estimate Critical Power (CP) and Work Capacity Above CP (W') using linear regression.

    Args:
        efforts (List[RiderEffortItem]): List of rider efforts.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
    # Prepare the data for linear regression
    durations = np.array([effort.duration for effort in efforts])
    powers = np.array([effort.wattage for effort in efforts])

    # Transform the data
    inverse_durations = 1 / durations
    power_minus_cp = powers

    # Perform linear regression
    A = np.vstack([inverse_durations, np.ones(len(inverse_durations))]).T
    cp, w_prime = np.linalg.lstsq(A, power_minus_cp, rcond=None)[0]

    # Convert w_prime to joules (since it is in watts * seconds)
    w_prime = w_prime * cp

    return cp, w_prime

# Example usage
def main() -> None:
    # Configure logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Example efforts (you would replace this with actual data)
    efforts = [
        RiderEffortItem(duration=60, wattage=400, speed=40, kilojoules=24),
        RiderEffortItem(duration=300, wattage=350, speed=35, kilojoules=105),
        RiderEffortItem(duration=600, wattage=300, speed=30, kilojoules=180),
    ]

    cp, w_prime = estimate_cp_and_w_prime(efforts)

    logger.info(f"Estimated CP: {cp:.2f} watts")
    logger.info(f"Estimated W': {w_prime:.2f} joules")

if __name__ == "__main__":
    main()
