"""
OCR service – Hybrid: EasyOCR for Arabic + PaddleOCR for English/Serial.
"""

import cv2

from config.settings import OCR_LANGUAGES, USE_GPU
from services.image_processing import preprocess_image


# ── EasyOCR (for Arabic text) ────────────────────────────


_easyocr_reader = None


def _get_easyocr_reader():
    """Lazily initialize the EasyOCR reader (heavy download on first use)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
        except ImportError:
            raise ImportError(
                "easyocr is not installed. Run:\n"
                "  pip install easyocr"
            )
        _easyocr_reader = easyocr.Reader(OCR_LANGUAGES, gpu=USE_GPU)
    return _easyocr_reader


def _extract_arabic(image, bbox) -> str:
    """Extract Arabic text using EasyOCR."""
    x1, y1, x2, y2 = bbox
    cropped = image[y1:y2, x1:x2]
    preprocessed = preprocess_image(cropped)
    results = _get_easyocr_reader().readtext(preprocessed, detail=0, paragraph=True)
    return " ".join(results).strip()


# ── PaddleOCR (for English/Serial text) ──────────────────

_paddle_reader = None


def _get_paddle_reader():
    """Lazily initialize the PaddleOCR reader."""
    global _paddle_reader
    if _paddle_reader is None:
        try:
            from paddleocr import PaddleOCR
        except ImportError:
            raise ImportError(
                "paddleocr is not installed. Run:\n"
                "  pip install paddlepaddle paddleocr"
            )
        _paddle_reader = PaddleOCR(
            use_textline_orientation=True,
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
        )
    return _paddle_reader


def _extract_english(image, bbox) -> str:
    """Extract English/Serial text using PaddleOCR."""
    x1, y1, x2, y2 = bbox
    cropped = image[y1:y2, x1:x2]

    result = _get_paddle_reader().ocr(cropped)

    # PaddleOCR 3.x returns: [OCRResult({..., 'rec_texts': [...], ...})]
    lines = []
    if result and len(result) > 0:
        ocr_result = result[0]  # OCRResult (dict-like)
        rec_texts = ocr_result.get("rec_texts", [])
        lines = list(rec_texts)

    return " ".join(lines).strip()


# ── Public API (routes to the right engine) ──────────────


def _pad_bbox(bbox, image_shape, pad: int = 10):
    """Expand bbox by `pad` pixels on each side, clamped to image bounds.

    Prevents YOLO's tight bounding boxes from cutting off edge characters.
    """
    h, w = image_shape[:2]
    x1, y1, x2, y2 = bbox
    return [
        max(x1 - pad, 0),
        max(y1 - pad, 0),
        min(x2 + pad, w),
        min(y2 + pad, h),
    ]


def extract_text(image, bbox, lang: str = "ara") -> str:
    """
    Crop a region from *image* using *bbox* [x1, y1, x2, y2]
    and extract text using the appropriate OCR engine.

    A small padding is added to the bbox to avoid cutting off
    edge characters from YOLO's tight detections.

    Args:
        image: Full card image (numpy BGR).
        bbox:  [x1, y1, x2, y2] bounding box.
        lang:  "ara" → EasyOCR (Arabic)
               "eng" → PaddleOCR (English/Serial)

    Returns:
        The recognized text as a single stripped string.
    """
    padded = _pad_bbox(bbox, image.shape)

    if lang == "eng":
        return _extract_english(image, padded)
    else:
        return _extract_arabic(image, padded)
