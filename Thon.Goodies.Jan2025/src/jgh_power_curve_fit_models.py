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
    A decay function that computes a * (1 / (xdata ** b)) for NumPy arrays.
    Handles zero values in the array by replacing them with a small epsilon value.

    Args:
        xdata (NDArray[np.float64]): The input array.
        a (float): Coefficient.
        b (float): Exponent.

    Returns:
        NDArray[np.float64]: The computed values of the decay function.

    Raises:
        ValueError: If xdata contains zero values to avoid division by zero.
    """

    if np.any(xdata < 1):
        raise ValueError("Jgh error message: input xdata must not contain values less than 1.")

    result = a * (1 / (xdata ** b))

    return result

def solve_decay_model_for_x_numpy(a : float, b : float, ydata: NDArray[np.float64]) -> NDArray[np.float64]:
    return (a / ydata) ** (1 / b)

