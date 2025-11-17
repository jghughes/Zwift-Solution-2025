# -*- coding: utf-8 -*-

import re
import shutil
import unicodedata
from typing import Set, Tuple

# Mapping of common problematic Unicode characters to ASCII equivalents
REPLACEMENTS: dict[str, str] = {
    '\u201c': '"', '\u201d': '"',  # “ ”
    '\u2018': "'", '\u2019': "'",  # ‘ ’
    '\u2013': '-', '\u2014': '-',  # – —
    '\u2026': '...',               # …
    '\u00A0': ' ',                 # Non-breaking space
    '\u00A9': '(c)',               # ©
    '\u00AE': '(R)',               # ®
    '\u2122': '(TM)',              # ™
}

def replace_non_ascii(text: str) -> Tuple[str, int]:
    """
    Replace non-ASCII characters in text with safe ASCII equivalents.
    Returns the cleaned text and the count of replacements made.
    """
    count: int = 0
    cleaned_chars = []
    # Normalize text to NFC form for consistent character representation
    text = unicodedata.normalize('NFC', text)
    for c in text:
        if c in REPLACEMENTS:
            count += 1
            cleaned_chars.append(REPLACEMENTS[c])
        elif ord(c) < 128:
            cleaned_chars.append(c)
        else:
            count += 1
            cleaned_chars.append('')  # Remove unknown non-ASCII
    cleaned = ''.join(cleaned_chars)
    return cleaned, count

def backup_file(filepath: str) -> None:
    """
    Create a backup of the file with a .bak extension.
    """
    backup_path: str = filepath + '.bak'
    shutil.copy2(filepath, backup_path)
    print(f"Backup created: {backup_path}")

def clean_file(filepath: str) -> None:
    """
    Backup the file, clean non-ASCII characters, and save the result.
    Prints the number of replacements made.
    """
    backup_file(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        content: str = f.read()

    non_ascii: Set[str] = set(re.findall(r'[^\x00-\x7F]', content))
    if non_ascii:
        print("Non-ASCII characters found:", non_ascii)

    cleaned, replacement_count = replace_non_ascii(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"File '{filepath}' cleaned and saved.")
    print(f"Total problematic replacements made: {replacement_count}")

if __name__ == "__main__":
    # Hard-coded file path variable
    filepath: str = "C:\\Users\\johng\\source\\repos\\Zwift-Solution-2025\\Zsun01\\scripts - brute amenities\\brute09_experiment_with_rider_eligibility.py"
    clean_file(filepath)