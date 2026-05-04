"""
YOLO-based detection service for:
  1. Detecting the ID card in a photo.
  2. Detecting fields (firstName, lastName, address, serial, nid) inside the card.
  3. Detecting individual digits of the national ID number.
"""

import cv2
from ultralytics import YOLO

from config.settings import (
    BBOX_HEIGHT_SCALE,
    DETECTION_OUTPUT_PATH,
    FIELD_DETECTION_MODEL_PATH,
    ID_CARD_MODEL_PATH,
    NID_DETECTION_MODEL_PATH,
)

from services.image_processing import expand_bbox_height
from services.ocr_service import extract_text


# ──────────────────────────────────────────────
# ID Card Detection 
# ──────────────────────────────────────────────
def detect_id_card(image_path: str):
    """
    Detect and crop the ID card region from the full photograph.

    Returns:
        The cropped numpy image of the ID card.
    """
    model = YOLO(ID_CARD_MODEL_PATH)
    results = model(image_path)
    image = cv2.imread(image_path)

    cropped_image = None
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped_image = image[y1:y2, x1:x2]

    if cropped_image is None:
        raise ValueError("No ID card detected in the image.")

    return cropped_image


# ──────────────────────────────────────────────
# National-ID Digit Detection
# ──────────────────────────────────────────────
def detect_national_id_digits(cropped_nid_image) -> str:
    """
    Run digit detection on the cropped national-ID region.

    Returns:
        A string of 14 digits representing the national ID.
    """
    model = YOLO(NID_DETECTION_MODEL_PATH)
    results = model(cropped_nid_image)

    detected_info = []
    for result in results:
        for box in result.boxes:
            cls = int(box.cls)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detected_info.append((cls, x1))
            cv2.rectangle(cropped_nid_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                cropped_nid_image, str(cls),
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2,
            )

    # Sort left→right to form the correct digit sequence
    detected_info.sort(key=lambda x: x[1])
    return "".join(str(cls) for cls, _ in detected_info)


# ──────────────────────────────────────────────
# Field Detection & Extraction
# ──────────────────────────────────────────────
def detect_and_extract_fields(cropped_card_image) -> dict:
    """
    Detect the individual fields on the ID card (name, address, NID, …)
    and extract their text via OCR.

    Returns:
        A dict with keys: first_name, second_name, full_name, national_id,
        address, serial.
    """
    model = YOLO(FIELD_DETECTION_MODEL_PATH)
    results = model(cropped_card_image)

    first_name = ""
    second_name = ""
    nid = ""
    address = ""
    serial = ""

    for result in results:
        # Save annotated image for display in the UI
        result.save(DETECTION_OUTPUT_PATH)

        for box in result.boxes:
            bbox = [int(c) for c in box.xyxy[0].tolist()]
            class_id = int(box.cls[0].item())
            class_name = result.names[class_id]

            if class_name == "firstName":
                first_name = extract_text(cropped_card_image, bbox, lang="ara")
            elif class_name == "lastName":
                second_name = extract_text(cropped_card_image, bbox, lang="ara")
            elif class_name == "serial":
                serial = extract_text(cropped_card_image, bbox, lang="eng")
            elif class_name == "address":
                address = extract_text(cropped_card_image, bbox, lang="ara")
            elif class_name == "nid":
                expanded = expand_bbox_height(
                    bbox, scale=BBOX_HEIGHT_SCALE, image_shape=cropped_card_image.shape
                )
                cropped_nid = cropped_card_image[expanded[1]:expanded[3], expanded[0]:expanded[2]]
                nid = detect_national_id_digits(cropped_nid)

    return {
        "first_name": first_name,
        "second_name": second_name,
        "full_name": f"{first_name} {second_name}",
        "national_id": nid,
        "address": address,
        "serial": serial,
    }
