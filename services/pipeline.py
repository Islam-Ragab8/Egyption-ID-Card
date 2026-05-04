"""
Full Pipeline — المايسترو اللي بيربط كل حاجة ببعض
===================================================

الفلو الكامل:
  1. Input           →  صورة البطاقة
  2. Card Detection  →  YOLO: هل في بطاقة؟
  3. Crop Card       →  قص البطاقة من الصورة
  4. Fields Detection→  YOLO: تحديد كل field
  5. Crop Fields     →  قص كل field لوحده
  6. OCR             →  قراءة النص من كل crop
  7. Parsing         →  تحويل لـ structured JSON
  8. Decode NID      →  فك تشفير الرقم القومي
  9. Validation      →  7 فحوصات + القرار النهائي
  10. LLM Explanation→  شرح القرار بالعربي
"""

from services.detection_service import detect_id_card, detect_and_extract_fields
from services.id_decoder import decode_national_id
from services.parsing_service import parse_extracted_fields
from services.validation_service import run_all_validations
from services.llm_explainer import generate_explanation


class PipelineResult:
    """Container for the full pipeline output — easy to pass around."""

    def __init__(self, raw_steps: dict):
        self.raw_steps = raw_steps

        # ── Quick access shortcuts ──
        validation = raw_steps["validation_result"]
        self.verdict = validation["verdict"]
        self.is_valid = validation["is_valid"]
        self.failed_count = validation["failed_count"]
        self.violations = validation["violations"]
        self.checks = validation["checks"]

        self.explanation = raw_steps["explanation"]
        self.extracted = raw_steps["parsed_data"]
        self.decoded = {
            "birth_date": raw_steps["decoded_data"].get("Birth Date", "N/A"),
            "governorate": raw_steps["decoded_data"].get("Governorate", "N/A"),
            "gender": raw_steps["decoded_data"].get("Gender", "N/A"),
        }
        self.validation = validation


def process_id_card(image_path: str) -> PipelineResult:
    """
    End-to-end pipeline.

    Args:
        image_path: Path to the uploaded ID card photograph.

    Returns:
        PipelineResult with all intermediate steps.

    Raises:
        ValueError: If no ID card is detected in the image.
    """
    steps = {}

    # ── Step 1-3: Card Detection & Crop ──────────────
    cropped_card = detect_id_card(image_path)
    steps["cropped_card"] = cropped_card

    # ── Step 4-6: Fields Detection + OCR ─────────────
    raw_fields = detect_and_extract_fields(cropped_card)
    steps["raw_fields"] = raw_fields

    # ── Step 7: Parsing ──────────────────────────────
    parsed_data = parse_extracted_fields(raw_fields)
    steps["parsed_data"] = parsed_data

    # ── Step 8: Decode NID ───────────────────────────
    nid = parsed_data["national_id"]
    try:
        decoded_data = decode_national_id(nid)
    except ValueError:
        decoded_data = {
            "Birth Date": "N/A",
            "Governorate": "N/A",
            "Gender": "N/A",
        }
    steps["decoded_data"] = decoded_data

    # ── Step 9: Validation (7 checks + verdict) ─────
    validation_result = run_all_validations(parsed_data)
    steps["validation_result"] = validation_result

    # ── Step 10: LLM Explanation ─────────────────────
    explanation = generate_explanation(parsed_data, decoded_data, validation_result)
    steps["explanation"] = explanation

    return PipelineResult(raw_steps=steps)
