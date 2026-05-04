"""
Image pre-processing utilities (grayscale conversion, bbox expansion, etc.).
"""

import cv2


def preprocess_image(cropped_image):
    """Convert a BGR image to grayscale for OCR.

    Used by EasyOCR path (Arabic text).
    PaddleOCR path uses raw BGR images directly.
    """
    gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    return gray_image


def expand_bbox_height(bbox, scale: float = 1.2, image_shape=None):
    """
    Expand only the *height* of a bounding box while keeping it inside the image.

    Args:
        bbox: [x1, y1, x2, y2] coordinates.
        scale: Multiplicative factor for height expansion.
        image_shape: (H, W, ...) of the source image – used for clamping.

    Returns:
        A new [x1, new_y1, x2, new_y2] list.
    """
    x1, y1, x2, y2 = bbox
    height = y2 - y1
    center_y = y1 + height // 2
    new_height = int(height * scale)
    new_y1 = max(center_y - new_height // 2, 0)
    new_y2 = min(center_y + new_height // 2, image_shape[0]) if image_shape else center_y + new_height // 2
    return [x1, new_y1, x2, new_y2]
