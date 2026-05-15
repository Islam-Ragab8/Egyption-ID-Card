"""
Application-wide settings and constants.
"""

import os

# ──────────────────────────────────────────────
# Base Paths
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")

# ──────────────────────────────────────────────
# Model Paths  (all inside weights/ folder)
# ──────────────────────────────────────────────
ID_CARD_MODEL_PATH = os.path.join(WEIGHTS_DIR, "detect_id_card.pt")
FIELD_DETECTION_MODEL_PATH = os.path.join(WEIGHTS_DIR, "detect_objects.pt")
NID_DETECTION_MODEL_PATH = os.path.join(WEIGHTS_DIR, "detect_id.pt")

# ──────────────────────────────────────────────
# OCR Settings
# ──────────────────────────────────────────────
OCR_LANGUAGES = ["ar"]
USE_GPU = False

# ──────────────────────────────────────────────
# Image Processing
# ──────────────────────────────────────────────
BBOX_HEIGHT_SCALE = 1.5  # Scale factor for expanding NID bounding box height

# ──────────────────────────────────────────────
# Streamlit Page Config
# ──────────────────────────────────────────────
PAGE_TITLE = "HUWIYA — Egyptian ID Verification"
PAGE_ICON = "🛡️"
PAGE_LAYOUT = "wide"

# ──────────────────────────────────────────────
# Supported Image Formats
# ──────────────────────────────────────────────
SUPPORTED_IMAGE_FORMATS = [
    "webp", "jpg", "tif", "tiff", "png",
    "mpo", "bmp", "jpeg", "dng", "pfm",
]

# ──────────────────────────────────────────────
# Annotated Detection Output
# ──────────────────────────────────────────────
DETECTION_OUTPUT_PATH = os.path.join(BASE_DIR, "d2.jpg")

# ──────────────────────────────────────────────
# LLM Settings (for Fraud Explanation)
# ──────────────────────────────────────────────
# Set your Gemini API key here or via environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"


# ──────────────────────────────────────────────
# Egyptian Governorate Codes
# ──────────────────────────────────────────────
GOVERNORATES = {
    '01': 'Cairo',
    '02': 'Alexandria',
    '03': 'Port Said',
    '04': 'Suez',
    '11': 'Damietta',
    '12': 'Dakahlia',
    '13': 'Ash Sharqia',
    '14': 'Kaliobeya',
    '15': 'Kafr El - Sheikh',
    '16': 'Gharbia',
    '17': 'Monoufia',
    '18': 'El Beheira',
    '19': 'Ismailia',
    '21': 'Giza',
    '22': 'Beni Suef',
    '23': 'Fayoum',
    '24': 'El Menia',
    '25': 'Assiut',
    '26': 'Sohag',
    '27': 'Qena',
    '28': 'Aswan',
    '29': 'Luxor',
    '31': 'Red Sea',
    '32': 'New Valley',
    '33': 'Matrouh',
    '34': 'North Sinai',
    '35': 'South Sinai',
    '88': 'Foreign',
}
