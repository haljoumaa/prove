import os
import re
import logging
import easyocr
from difflib import SequenceMatcher

LANGS = ['no', 'en']  # Norwegian + English
MODEL_DIR = '~/.EasyOCR/model/'
LOG_LEVEL = logging.DEBUG
logging.basicConfig(
    format='%(levelname)s | %(asctime)s | %(funcName)s | %(message)s',
    level=LOG_LEVEL
)

# Fuzzy matching threshold
FUZZY_THRESHOLD = 0.6

def fuzzy_match(str1, str2, threshold=FUZZY_THRESHOLD):
    """
    Returns True if str1 is sufficiently similar to str2 based on a ratio.
    """
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold

def bbox_center(bbox):
    """
    Given an EasyOCR bounding box [top-left, top-right, bottom-right, bottom-left],
    returns the (x_center, y_center).
    """
    (x1, y1) = bbox[0]  # top-left
    (x2, y2) = bbox[2]  # bottom-right
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    return (cx, cy)

def main():
    # 1) Locate the image
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "uknoa.png")
    if not os.path.exists(image_path):
        logging.error(f"Image not found: {image_path}")
        return

    # 2) Initialize EasyOCR Reader
    try:
        # If you have torch w/ CUDA, set gpu=True for speed
        reader = easyocr.Reader(LANGS, model_storage_directory=MODEL_DIR, gpu=False)
    except Exception as e:
        logging.error(f"Failed to initialize EasyOCR Reader: {e}")
        return

    # 3) Run OCR in detail mode => list of (bbox, text, confidence)
    ocr_results = reader.readtext(image_path, detail=1)
    logging.info("OCR complete, analyzing bounding boxes...")

    # 4) Find “Sum timer til utbetaling” bounding box
    target_phrase = "sum timer til utbetaling"
    sum_timer_bbox = None
    sum_timer_center = None

    for (bbox, text, confidence) in ocr_results:
        if fuzzy_match(text, target_phrase):
            sum_timer_bbox = bbox
            sum_timer_center = bbox_center(bbox)
            logging.debug(f"Matched phrase '{text}' at {bbox} (conf={confidence:.2f})")
            break

    if not sum_timer_bbox:
        logging.warning("Did not find 'Sum timer til utbetaling' in the image.")
        return

    (sum_x, sum_y) = sum_timer_center
    logging.info(f"'Sum timer til utbetaling' center: ({sum_x:.2f}, {sum_y:.2f})")

    # 5) Look for numeric text in the same row and to the right.
    #    We'll define a row threshold to limit how far vertically text can be from sum_timer_y.
    row_threshold = 20.0  # Adjust if lines are more widely spaced

    # Use a pattern that requires at least one decimal or comma to avoid capturing pure integers like '17'
    numeric_pattern = re.compile(r"^\d{1,3}([.,]\d+)?$")

    candidates = []
    for (bbox, text, conf) in ocr_results:
        text_clean = text.strip()

        # Check if text matches the numeric pattern (with decimal or comma).
        if numeric_pattern.match(text_clean):
            (cx, cy) = bbox_center(bbox)
            # Must be close in the vertical direction AND to the right
            if abs(cy - sum_y) < row_threshold and (cx > sum_x):
                dx = cx - sum_x  # horizontal distance from the sum_timer center
                candidates.append((dx, text_clean, bbox, conf))

    if not candidates:
        logging.warning("Found 'Sum timer til utbetaling' but no suitable numeric text to its right.")
        return

    # Sort by horizontal distance from the target phrase so we pick the closest
    candidates.sort(key=lambda tup: tup[0])
    (closest_dist, numeric_text, numeric_bbox, confidence) = candidates[0]

    logging.info(f"Closest numeric box to the right: '{numeric_text}' @ dist={closest_dist:.2f}, conf={confidence:.2f}")

    # 6) Convert "10,00" -> float if desired
    numeric_value_str = numeric_text.replace(",", ".")
    try:
        numeric_value = float(numeric_value_str)
        logging.info(f"Final float value = {numeric_value}")
    except ValueError:
        logging.warning(f"Could not parse '{numeric_text}' as float")

if __name__ == "__main__":
    main()
