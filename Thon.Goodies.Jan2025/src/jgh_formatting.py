from typing import Union, Optional
from datetime import datetime, timezone

def truncate(f : float, n : int):
    factor = 10 ** n
    return int(f * factor) / factor

def round_to_nearest_10(x: float) -> int:
    """
    Round an int or float to the nearest multiple of 10.

    Args:
        x (int or float): The number to round.

    Returns:
        int: The rounded value, e.g., 23 -> 20, 25 -> 30, 30 -> 30.
    """
    return int(round(x / 10.0) * 10)

def format_number_1dp(x: float) -> str:
    """
    Format a float to one decimal place, always showing the decimal digit (including trailing zero).
    
    Args:
        x (float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '12.0', '3.5', '0.0'.
    """
    return f"{x:.1f}"

def format_number_2dp(x: float) -> str:
    """
    Format a float to two decimal places, always showing the decimal digit (including trailing zero).
    
    Args:
        x (float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '12.00', '3.56', '0.01'.
    """
    return f"{x:.2f}"

def format_number_3dp(x: float) -> str:
    """
    Format a float to two decimal places, always showing the decimal digit (including trailing zero).
    
    Args:
        x (float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '12.00', '3.56', '0.01'.
    """
    return f"{x:.3f}"

def format_number_4dp(x: float) -> str:
    """
    Format a float to two decimal places, always showing the decimal digit (including trailing zero).
    
    Args:
        x (float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '12.0000', '3.5600', '0.0100'.
    """
    return f"{x:.4f}"

def format_number_2sig(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 2 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.2e+03' or '12'.
    """
    return f"{x:.2g}"

def format_number_4sig(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 4 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.234e+03' or '1234'.
    """
    return f"{x:.4g}"

def format_number_with_comma_separators(x: Union[int, float]) -> str:
    """
    Format a number with thousands separators and up to 2 decimal places.
    For floats, trailing zeros and decimal points are removed if unnecessary.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1,234' or '1,234.56'.
    """
    if isinstance(x, int):
        return f"{x:,}"
    elif isinstance(x, float):
        return f"{x:,.2f}".rstrip('0').rstrip('.') if '.' in f"{x:,.2f}" else f"{x:,.2f}"
    else:
        return str(x)

def format_number_0dp_padded2(x: Union[int, float]) -> str:
    """
    Round a float to zero decimal places (nearest integer) and return a string
    padded with leading zeros so the result is at least 2 characters long.

    Examples:
        5.3   -> "05"
        1234.7-> "1235"
        -5.2  -> "-05"

    Note: If the rounded integer requires more than 2 characters (e.g. 123),
    the full number will be returned (no truncation).
    """
    rounded = int(round(x))
    return f"{rounded:02d}"

def format_number_0dp_padded4(x: Union[int, float]) -> str:
    """
    Round a float to zero decimal places (nearest integer) and return a string
    padded with leading zeros so the result is at least 4 characters long.

    Examples:
        5.3   -> "0005"
        1234.7-> "1235"
        -5.2  -> "-005"

    Note: If the rounded integer requires more than 4 characters (e.g. 12345),
    the full number will be returned (no truncation).
    """
    rounded = int(round(x))
    return f"{rounded:04d}"



def format_pretty_duration_hms(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    # Format seconds with one leading zero if < 10, else no leading zero
    sec_str = f"{secs:03.1f}" if secs < 10 else f"{secs:0.1f}"
    if hours >= 1:
        return f"{int(hours)} hours {int(minutes):02} minutes {sec_str} seconds"
    elif minutes >= 1:
        return f"{int(minutes):02} minutes {sec_str} seconds"
    else:
        return f"{sec_str} seconds"


def format_timestamp_as_yyyy_mm_dd(ts: Optional[float] = None) -> str:
    """
    Format a timestamp (seconds since epoch) as 'YYYY-MM-DD'.
    If no timestamp is provided, use the current time.

    Args:
        ts (float, optional): Unix timestamp. Defaults to None (current time).

    Returns:
        str: The formatted date string, e.g., '2025-08-15'.
    """
    dt = datetime.fromtimestamp(ts) if ts is not None else datetime.now()
    return dt.strftime("%Y-%m-%d")

def get_current_utc_iso8601_timestamp() -> str:
    """
    Format the current UTC time as ISO 8601 string with 'Z' suffix.
    Returns:
        str: The formatted ISO 8601 string, e.g., '2025-08-15T12:34:56.789Z'.
    """
    dt = datetime.now(timezone.utc)
    ms = int(dt.microsecond / 1000)
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{ms:03d}Z")
