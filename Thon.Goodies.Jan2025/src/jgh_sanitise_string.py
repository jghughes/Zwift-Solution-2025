import re
import unicodedata

def sanitise_string(input: str | None) -> str:
    """
    Sanitizes a string by removing invalid Unicode characters, unwanted symbols (e.g., emoji),
    reducing multiple spaces to a single space, and stripping leading and trailing whitespace.

    Args:
        input (str): The string to sanitize.

    Returns:
        str: The sanitized string.
    """
    if input is None:
        return ""
    if not isinstance(input, str):
        raise ValueError(f"Expected a string, but got {type(input).__name__}")
    try:
        # Remove invalid Unicode characters (e.g., �)
        sanitized_value = input.replace("\uFFFD", "")
        # Remove invalid surrogate pairs or other invalid characters
        sanitized_value = sanitized_value.encode("utf-8", errors="ignore").decode("utf-8")
        # Remove unwanted Unicode characters (e.g., emoji, symbols)
        sanitized_value = ''.join(
            char for char in sanitized_value
            if unicodedata.category(char)[0] not in {'C', 'S', 'P', 'M'}  # Remove control, symbol, punctuation, and mark characters
        )
        # Reduce multiple spaces (including tabs and newlines) to a single space
        sanitized_value = re.sub(r'\s+', ' ', sanitized_value)
        # Strip leading and trailing spaces
        return sanitized_value.strip()
    except Exception as e:
        raise ValueError(f"Error sanitizing string '{input}'. Details: {e}")
