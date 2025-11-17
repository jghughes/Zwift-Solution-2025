from typing import Optional
from datetime import datetime
import re

CallTimedOut = "Call timed out. Please try again later."
MethodFailed = "Method failed to complete."


# ============================================================
# Basic String Utilities
# ============================================================

def capitalize_first_letter(text: Optional[str]) -> str:
    """
    Returns the input string with the first_name letter capitalized.
    Handles None or empty string gracefully.
    """
    if not text:
        return ""
    return text[0].upper() + text[1:]

def first_n_chars(text: Optional[str], n: int) -> str:
    """
    Returns the first_name n characters of the input string.
    Handles cases where text is None or shorter than n characters.
    """
    if text is None:
        return ""
    return text[:n]


# ============================================================
# String Concatenation Helpers
# ============================================================

def concat(*array_of_texts: str) -> str:
    """
    Concatenates a variable length array of texts.
    Skips texts that are null or whitespace.
    """
    return concat_with_separator("", *array_of_texts)

def concat_with_separator(separator: str, *array_of_texts: str) -> str:
    """
    Concatenates a variable length array of texts with a separator.
    Skips texts that are null or whitespace.
    """
    list_of_texts = [text for text in array_of_texts if text]
    if not list_of_texts:
        return ""
    return separator.join(list_of_texts)

def concat_as_sentences(*array_of_texts: str) -> str:
    """
    Concatenates texts with a space between each.
    Skips texts that are null or whitespace.
    """
    return concat_with_separator(" ", *array_of_texts)

def concat_as_lines(*array_of_texts: str) -> str:
    """
    Concatenates texts with each on a new line.
    Skips texts that are null or whitespace.
    """
    return concat_with_separator("\n", *array_of_texts)

def concat_as_paragraphs(*array_of_texts: str) -> str:
    """
    Concatenates texts with a linespace between each.
    Skips texts that are null or whitespace.
    """
    return concat_with_separator("\n\n", *array_of_texts)


# ============================================================
# Formatting and Messaging Helpers
# ============================================================

def make_pretty_time_from_seconds(elapsed_time: float) -> str:
    """
    Returns a human-readable string representing the elapsed time.
    Formats as seconds, minutes, or hours as appropriate.
    Assumes elapsed_time is in seconds.
    """
    if elapsed_time < 60:
        return f"{elapsed_time:.2f} seconds"
    elif elapsed_time < 3600:
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        return f"{minutes} min {seconds:.1f} sec"
    else:
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = elapsed_time % 60
        return f"{hours} hr {minutes} min {seconds:.0f} sec"

def make_pretty_count_of_bytes(numberOfBytes: int) -> str:
    """
    Returns a human-readable string representing the size in bytes, KB, or MB.
    """
    if numberOfBytes < 1024:
        return f"{numberOfBytes} bytes"
    elif numberOfBytes < 1024 * 1024:
        kb = numberOfBytes / 1024
        return f"{kb:.1f} KB"
    else:
        mb = numberOfBytes / (1024 * 1024)
        return f"{mb:.2f} MB"

def make_wait_time_msg(start_timestamp: datetime) -> str:
    """
    Returns a pretty message describing the wait time since start_timestamp.
    """
    elapsed_seconds = (datetime.now() - start_timestamp).total_seconds()
    return f"Wait time was {elapsed_seconds:.1f} seconds."

import unicodedata

# ============================================================
# Custom for Brute
# ============================================================

def make_short_displayname(old_name: str) -> str:
    """
    Cleans up a given name according to the following rules:
    1. Trim spaces from the old name and replace any contained commas or dots with spaces.
    2. If the old name has only one word, capitalize the first_name letter of the word.
    3. If the old name has more than one word, concatenate the first_name word (with the first_name letter capitalized)
        with the capitalized first_name letter of the second word.

    Args:
        old_name (str): The original name to be cleaned.

    Returns:
        str: The cleaned-up new name.
    """
    old_name = cleanup_name_string(old_name)

    # Step 1: Trim spaces and replace commas or dots with spaces
    old_name = old_name.strip().replace(",", " ").replace(".", " ")

    # Step 2: Split the name into words
    name_parts = old_name.split()

    # Step 3: Determine the new name
    if len(name_parts) == 1:
        # If the old name has only one word, capitalize the first_name letter
        new_name = name_parts[0][0].upper() + name_parts[0][1:]
    elif len(name_parts) > 1:
        # If the old name has more than one word, concatenate the first_name word
        # (with only the first_name letter capitalized) with the capitalized first_name letter of the second word
        new_name = name_parts[0][0].upper() + name_parts[0][1:] + " " + name_parts[1][0].upper()
    else:
        # Handle edge cases where the name might be empty
        new_name = "Unknown"

    return new_name

def cleanup_name_string(name_to_clean: str | None) -> str:

    sanitized_value = sanitise_string(name_to_clean)

    try:
        # Remove specific unwanted characters - this is a kludge - who knows what others out there lurk
        unwanted_characters = sorted(
            ['ZSUN', 'ZSUNR', 'ZSUNstruck', 'JOINcc', 'WCCZSUNR', 'ZSunR', 'ZSUNr', 'ZSUNShine', 'HERD LITTLE PENGUINS', 'ZSUNRAtomic', 'ZSUNR Betelgeuse', 'ZSuNR', '(NCC)', 'CC Solaris Racing pb Suncoast Vet', 'Evo Renegades', 'Red Dwarfs', 'Harlow Tri Club', 'ZSUNR Neptune', 'ZNeptune', 'USMES', '5W4T', '12 Weeks Postpartum', 'TeamZF', 'ZSUNR COWS', 'zsunr','CC', 'coalition', 'SISU', 'ZSUNR Pegasus', 'MTCCSA', 'EVOLVE', 'OTR', 'Njinga CC', 'NZBRO', 'CrushPod', 'AsselinOptimum', 'wcc','HERD', 'DIRT', 'COPZ', 'BEAT', 'Optimum', 'USMeS', 'RAD', 'NZBRO', 'Synergy', 'Artemis RacingVCRCCPatapsco Bikes', 'AGTB', '6AM', 'BOB', 'Polaris', 'GXY', 'DRAFT', 'ZSUNR MERCURY', 'ZSUNR Centaurus', 'LGBTQzZLDRF4CTeamIncorrigible', 'CarpeDiemRacing', 'ZSUNR Pulsars', 'Velocity', 'TEAM VARLO', 'TZR FB', 'Sea Dragons', 'ZsunR', 'Velos', 'HABFRRCLOWAT','COALITION', 'Zsunr', 'Roadrunners', 'ODZ', 'SZUNR', ' TFC', 'USAC 550844', 'RK Rhinos', '(ZSUNR)', 'CC'],
            key=len,
            reverse=True
        )

        for char in unwanted_characters:
            sanitized_value = sanitized_value.replace(char, "")

        return sanitise_string(sanitized_value)
    except Exception as e:
        return sanitized_value

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
    try:
        # Remove invalid Unicode characters (e.g., ?)
        sanitized_value = input.replace("\uFFFD", "")
        # Remove invalid surrogate pairs or other invalid characters
        sanitized_value = sanitized_value.encode("utf-8", errors="ignore").decode("utf-8")
        # Remove unwanted Unicode characters (e.g., emoji, symbols)
        sanitized_value = ''.join(
            char for char in sanitized_value
            if unicodedata.category(char)[0] not in {'C', 'S', 'P', 'M'}  # Remove control, symbol, punctuation, and mark characters
        )
        # Remove specific unwanted characters - this is a kludge - who knows what others out there lurk in European name fields
        unwanted_characters = ['\u0144', '\u1559', '\u21c0', '\u2038', '\u21bc', '\u2036', '\u1557']

        for char in unwanted_characters:
            sanitized_value = sanitized_value.replace(char, "")
        # Reduce multiple spaces (including tabs and newlines) to a single space
        sanitized_value = re.sub(r'\s+', ' ', sanitized_value)
        # Strip leading and trailing spaces
        return sanitized_value.strip()
    except Exception as e:
        raise ValueError(f"Error sanitizing string '{input}'. Details: {e}")
