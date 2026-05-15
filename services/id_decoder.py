"""
Decoder for the 14-digit Egyptian National ID number.
Extracts birth date, governorate, and gender.
"""

import re
from config.settings import GOVERNORATES

def remove_numbers(text: str) -> str:
    """Strip all digits from *text*."""
    return re.sub(r"\d+", "", text)


def decode_national_id(id_number: str) -> dict:
    """
    Decode a 14-digit Egyptian National ID.

    Returns:
        A dict with keys: Birth Date, Governorate, Gender.

    Raises:
        ValueError: If the century digit is not 2 or 3, or if the ID
                     is shorter than expected.
    """
    if len(id_number) < 13:
        raise ValueError(f"National ID too short ({len(id_number)} digits).")

    century_digit = int(id_number[0])
    year = int(id_number[1:3])
    month = int(id_number[3:5])
    day = int(id_number[5:7])
    governorate_code = id_number[7:9]
    gender_code = int(id_number[12]) 

    if century_digit == 2:
        full_year = 1900 + year
    elif century_digit == 3:
        full_year = 2000 + year
    else:
        raise ValueError(f"Invalid century digit: {century_digit}")

    gender = "Male" if gender_code % 2 != 0 else "Female"
    governorate = GOVERNORATES.get(governorate_code, "Unknown")
    birth_date = f"{full_year:04d}-{month:02d}-{day:02d}"

    return {
        "Birth Date": birth_date,
        "Governorate": governorate,
        "Gender": gender,
    }
