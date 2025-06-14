from typing import Union
import math

def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> float:
    """
    Safely divides numerator by denominator. Returns 0.0 if denominator is zero,
    NaN, infinite, or not a valid number.

    Args:
        numerator (int or float): The value to be divided.
        denominator (int or float): The value to divide by.

    Returns:
        float: The result of the division, or 0.0 if denominator is zero, NaN, or infinite.
    """
    try:
        denom = float(denominator)
        if denom == 0.0 or denom == -0.0 or not math.isfinite(denom) or math.isnan(denom):
            return 0.0
        return float(numerator) / denom
    except Exception:
        return 0.0