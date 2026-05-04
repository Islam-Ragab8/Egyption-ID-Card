"""
Parsing Service — تحويل النص الخام لـ structured data (JSON)
=============================================================
بياخد الـ raw extracted fields من الـ OCR ويحولهم لـ clean,
structured dictionary جاهز للـ validation.
"""

import re
from datetime import datetime


def clean_arabic_text(text: str) -> str:
    """Remove extra whitespace and normalize Arabic text."""
    if not text:
        return ""
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    # Remove any stray non-Arabic/non-space characters that OCR might add
    return text


def clean_national_id(nid: str) -> str:
    """Ensure NID contains only digits."""
    if not nid:
        return ""
    return re.sub(r"[^\d]", "", nid)


def parse_extracted_fields(raw_fields: dict) -> dict:
    """
    Transform raw OCR output into a clean, structured record.

    Input (from detection_service):
        {
            "first_name": "محمد",
            "second_name": "أحمد علي",
            "full_name": "محمد أحمد علي",
            "national_id": "29901011234567",
            "address": "12 شارع التحرير القاهرة",
            "serial": "ABC123",
        }

    Output:
        {
            "first_name": "محمد",
            "second_name": "أحمد علي",
            "full_name": "محمد أحمد علي",
            "national_id": "29901011234567",
            "address": "12 شارع التحرير القاهرة",
            "serial": "ABC123",
            "nid_length": 14,
            "has_first_name": True,
            "has_second_name": True,
            "has_address": True,
            "has_national_id": True,
        }
    """
    # Clean all fields
    first_name = clean_arabic_text(raw_fields.get("first_name", ""))
    second_name = clean_arabic_text(raw_fields.get("second_name", ""))
    full_name = clean_arabic_text(raw_fields.get("full_name", ""))
    national_id = clean_national_id(raw_fields.get("national_id", ""))
    address = clean_arabic_text(raw_fields.get("address", ""))
    serial = raw_fields.get("serial", "").strip()

    # If full_name is empty but we have parts, reconstruct
    if not full_name and (first_name or second_name):
        full_name = f"{first_name} {second_name}".strip()

    return {
        # ── Cleaned fields ──
        "first_name": first_name,
        "second_name": second_name,
        "full_name": full_name,
        "national_id": national_id,
        "address": address,
        "serial": serial,

        # ── Metadata ──
        "nid_length": len(national_id),
        "has_first_name": bool(first_name),
        "has_second_name": bool(second_name),
        "has_address": bool(address),
        "has_national_id": bool(national_id),
    }
