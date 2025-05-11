import numpy as np
from numpy.typing import NDArray


def cp_w_prime_model_numpy(xdata: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    Compute power as a function of CP and W' using the formula (a * xdata + b) / xdata.

    Args:
        xdata (NDArray[np.float64]): Duration (seconds). Must be non-zero.
        a (float): Coefficient for the linear term, cp_watts.
        b (float): Constant term, W'

    Returns:
        NDArray[np.float64]: Computed power values.

    Raises:
        ValueError: If xdata contains zero values to avoid division by zero.
    """

    if np.any(xdata < 1):
        raise ValueError("Jgh error message: input xdata must not contain values less than 1.")

    result = (a * xdata + b) / xdata

    return result


def decay_model_numpy(xdata: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    Computes a decay function using the formula: a * (1 / (xdata ** b)).

    This function models an inverse exponential decay relationship between duration 
    and power outut, where `a` is the scaling coefficient and `b` is the exponent 
    controlling the rate of decay. The input array `xdata` must not contain values
    less than 1 to avoid invalid computations.xdata are measured in seconds. 
    ydata are measured in watts.

    Args:
        xdata (NDArray[np.float64]): Input array representing the independent variable (e.g., time or duration).
                                     All values must be >= 1.
        a (float): Scaling coefficient that determines the amplitude of the decay.
        b (float): Exponent that controls the rate of decay.

    Returns:
        NDArray[np.float64]: Computed values of the decay function for each element in `xdata`.

    Raises:
        ValueError: If any value in `xdata` is less than 1, as this would lead to invalid computations.
          """

    if np.any(xdata < 1):
        raise ValueError("Jgh error message: input xdata must not contain values less than 1.")

    result = a * (1 / (xdata ** b))

    return result

def solve_decay_model_for_x_numpy(a : float, b : float, ydata: NDArray[np.float64]) -> NDArray[np.float64]:
    return (a / ydata) ** (1 / b)

