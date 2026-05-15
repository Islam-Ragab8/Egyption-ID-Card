# Egyptian National ID Card Verification System

An end-to-end AI pipeline that detects, reads, and verifies Egyptian National ID cards from a single photograph using **YOLOv8 + Hybrid OCR (EasyOCR + PaddleOCR) + Rule-Based Validation + LLM Explainability**.

```bash
streamlit run APP.py
```

---

## Pipeline Overview

```
  Input Image
       |
       v
  [1] Card Detection ────────> No card found ──> REJECT
       |
       v
  [2] Crop Card Region
       |
       v
  [3] Field Detection (5 fields: name, lastName, address, serial, NID)
       |
       v
  [4] Hybrid OCR
       |─── Arabic fields  ──> EasyOCR
       |─── English fields ──> PaddleOCR (PP-OCRv5)
       |─── NID digits     ──> YOLO digit-level detection
       |
       v
  [5] Parsing (raw text ──> structured JSON)
       |
       v
  [6] NID Decoding (14-digit ──> birth date, governorate, gender)
       |
       v
  [7] Validation Engine (7 automated checks)
       |
       v
  [8] LLM Explanation (Gemini 2.0 Flash / rule-based fallback)
       |
       v
  Final Verdict:  VERIFIED  |  REJECTED
```

---

## Module Breakdown

Each module is described below in dependency order — earlier modules are prerequisites for later ones.

### Step 0 — `config/settings.py`

Central configuration file. Contains:
- Model paths (all weights under `weights/`)
- OCR settings and language config
- Egyptian governorate code lookup table (27 governorates)
- Gemini LLM settings
- Streamlit page configuration

### Step 1 — `services/image_processing.py`

Low-level image utilities with no dependency on YOLO or OCR.

| Function | Purpose |
|----------|---------|
| `preprocess_image()` | Convert to grayscale for EasyOCR |
| `expand_bbox_height()` | Expand bounding box height to avoid clipping |

### Step 2a — `services/ocr_service.py`

Hybrid OCR engine with language-aware routing:

| Language | Engine | Use Case |
|----------|--------|----------|
| Arabic (`ara`) | EasyOCR | First name, last name, address |
| English (`eng`) | PaddleOCR v5 | Serial number |

A 10px padding is applied to all bounding boxes before cropping to prevent edge-character clipping from YOLO's tight detections.

### Step 2b — `services/detection_service.py`

All YOLO inference logic. Three detection functions:

| Function | Model | Output |
|----------|-------|--------|
| `detect_id_card()` | `detect egypt card.pt` | Cropped card image |
| `detect_and_extract_fields()` | `detect_odjects.pt` | 5 field bounding boxes + OCR text |
| `detect_national_id_digits()` | `detect_id.pt` | 14-digit string (left-to-right sorted) |

### Step 2c — `services/id_decoder.py`

Pure-Python decoder for the 14-digit Egyptian National ID:

```
Position [0]      --> Century (2 = 1900s, 3 = 2000s)
Position [1-2]    --> Year of birth
Position [3-4]    --> Month of birth
Position [5-6]    --> Day of birth
Position [7-8]    --> Governorate code
Position [12]     --> Gender (odd = Male, even = Female)
```

### Step 3 — `services/parsing_service.py`

Transforms raw OCR output into a clean, structured dictionary:
- Normalizes Arabic whitespace
- Strips non-digit characters from NID
- Adds metadata flags (`has_first_name`, `nid_length`, etc.)
- Reconstructs `full_name` from parts if missing

### Step 4 — `services/validation_service.py`

Runs **7 independent checks** on the parsed data:

| # | Check | Rule |
|---|-------|------|
| 1 | `required_fields` | All 4 essential fields must be present |
| 2 | `nid_format` | NID must be exactly 14 digits |
| 3 | `century_digit` | First digit must be 2 or 3 |
| 4 | `birth_date` | Date must be real and age ≤ 120 years |
| 5 | `governorate` | Governorate code must exist in lookup table |
| 6 | `gender` | Gender digit must be a valid digit |
| 7 | `name_consistency` | First name must match start of full name |

**Verdict:** All pass → `VERIFIED` | Any failure → `REJECTED` with violation details.

### Step 5 — `services/llm_explainer.py`

Generates a human-readable Arabic explanation for the verdict:
- **Primary:** Gemini 2.0 Flash API (requires `GEMINI_API_KEY` env variable)
- **Fallback:** Rule-based explanation (no external dependency)

### Step 6 — `services/pipeline.py`

The orchestrator. Chains all services into a single function call:

```python
result = process_id_card("photo.jpg")
print(result.verdict)       # "VERIFIED" or "REJECTED"
print(result.failed_count)  # 0, 1, 2, ...
print(result.explanation)   # Arabic explanation
```

### Step 7 — `pages/home.py` + `pages/guide.py`

Streamlit UI with 3 tabs:
1. **Extracted Data** — All OCR-extracted fields
2. **NID Decoded** — Birth date, governorate, gender
3. **Checks & Verdict** — All 7 checks, violations, and LLM explanation

### Step 8 — `APP.py`

Entry point. Configures Streamlit and routes between Home and Guide pages.

---

## Project Structure

```
HUWIYA/
│
├── APP.py                           # Entry point
│
├── config/
│   ├── __init__.py
│   └── settings.py                  # All constants & model paths
│
├── services/
│   ├── __init__.py
│   ├── image_processing.py          # Image preprocessing
│   ├── ocr_service.py               # Hybrid OCR (EasyOCR + PaddleOCR)
│   ├── detection_service.py         # YOLO detection (3 models)
│   ├── id_decoder.py                # NID decoder
│   ├── parsing_service.py           # Raw text --> structured JSON
│   ├── validation_service.py        # 7 checks + verdict
│   ├── llm_explainer.py             # LLM / rule-based explanation
│   └── pipeline.py                  # Full orchestrator
│
├── pages/
│   ├── __init__.py
│   ├── home.py                      # Main verification UI
│   └── guide.py                     # Documentation UI
│
├── weights/
│   ├── detect egypt card.pt         # YOLO — card detection     (6.2 MB)
│   ├── detect_odjects.pt            # YOLO — field detection    (6.3 MB)
│   └── detect_id.pt                 # YOLO — digit detection   (22.5 MB)
│
└── requirements.txt
```

---

## Quick Reference

| # | Module | File | Depends On |
|---|--------|------|------------|
| 0 | Configuration | `config/settings.py` | — |
| 1 | Image Processing | `services/image_processing.py` | OpenCV |
| 2a | OCR Engine | `services/ocr_service.py` | Step 1 |
| 2b | YOLO Detection | `services/detection_service.py` | Steps 1, 2a |
| 2c | NID Decoder | `services/id_decoder.py` | Step 0 (governorate codes) |
| 3 | Data Parsing | `services/parsing_service.py` | — |
| 4 | Validation | `services/validation_service.py` | Step 0 (governorate codes) |
| 5 | LLM Explainer | `services/llm_explainer.py` | Step 0 (Gemini config) |
| 6 | Pipeline | `services/pipeline.py` | All above |
| 7 | UI | `pages/home.py`, `pages/guide.py` | Step 6 |
| 8 | Entry Point | `APP.py` | Step 7 |

---

## Dependencies

```bash
pip install streamlit ultralytics easyocr paddlepaddle paddleocr opencv-python numpy pillow google-generativeai
```

| Package | Purpose |
|---------|---------|
| `ultralytics` | YOLOv8 object detection |
| `easyocr` | Arabic OCR |
| `paddlepaddle` + `paddleocr` | English OCR (PP-OCRv5) |
| `streamlit` | Web UI |
| `opencv-python` | Image processing |
| `google-generativeai` | LLM explanation (optional) |

---

## LLM Setup (Optional)

To enable Gemini-powered explanations:

```bash
pip install google-generativeai
set GEMINI_API_KEY=your_key_here
```

If no API key is set, the system automatically uses rule-based explanations — no functionality is lost.
