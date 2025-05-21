from typing import Union

def round_to_nearest_10(x: float) -> int:
    """
    Round an int or float to the nearest multiple of 10.

    Args:
        x (int or float): The number to round.

    Returns:
        int: The rounded value, e.g., 23 -> 20, 25 -> 30, 30 -> 30.
    """
    return int(round(x / 10.0) * 10)

def format_number_1_decimal(x: float) -> str:
    """
    Format a float to one decimal place, always showing the decimal digit (including trailing zero).
    
    Args:
        x (float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '12.0', '3.5', '0.0'.
    """
    return f"{x:.1f}"

def format_number_sig2(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 2 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.2e+03' or '12'.
    """
    return f"{x:.2g}"

def format_number_sig4(x : Union[int, float]):
    """
    Format a number in compact scientific or fixed-point notation with 4 significant digits.
    
    Args:
        x (int or float): The number to format.
    
    Returns:
        str: The formatted string, e.g., '1.234e+03' or '1234'.
    """
    return f"{x:.4g}"

def format_number_with_commas(x: Union[int, float]) -> str:
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

def format_hms(seconds: float) -> str:
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

def truncate(f : float, n : int):
    factor = 10 ** n
    return int(f * factor) / factor



