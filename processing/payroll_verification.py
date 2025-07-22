import os
import re
import logging
import pandas as pd
import pytesseract
import easyocr
from difflib import get_close_matches, SequenceMatcher
from typing import Union 

MODEL_STORAGE_PATH = '~/.EasyOCR/model/'
LANGS = ['no', 'en']  # Norwegian + English OCR
TOLERANCE = 0.1       # Allowed difference between reported & agreed hours
FUZZY_THRESHOLD = 0.6 # Fuzzy matching threshold for name lookups
LOG_LEVEL = logging.INFO

logging.basicConfig(
    format='%(levelname)s | %(asctime)s | %(funcName)s | %(message)s',
    level=LOG_LEVEL
)



def fuzzy_match(str1, str2, threshold=FUZZY_THRESHOLD):
    """
    Returns True if str1 is sufficiently similar to str2 based on a ratio.
    Used for 'Sum timer til utbetaling' matches, etc.
    """
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold


def bbox_center(bbox):
    """
    EasyOCR bounding box: [top-left, top-right, bottom-right, bottom-left].
    Return (x_center, y_center).
    """
    (x1, y1) = bbox[0]  # top-left
    (x2, y2) = bbox[2]  # bottom-right
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    return (cx, cy)



class TimesheetProcessor:
    """
    Encapsulates:
      1) Loading CSV reference data
      2) Initializing EasyOCR
      3) Extracting name (Tesseract)
      4) Extracting sum timer (bounding-box approach)
      5) Approving or rejecting timesheet
    """

    def __init__(self, csv_path: str, gpu: bool = False):
        """
        :param csv_path: Path to CSV with columns [Name, agreed hours, extra hours, hours given away].
        :param gpu: True if you have a GPU and want to enable it in EasyOCR.
        """
        # Load CSV
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found at {csv_path}")
        self.df = pd.read_csv(csv_path)
        self.df.columns = self.df.columns.str.strip()
        # Normalize "Name" column
        self.df["Name"] = self.df["Name"].astype(str).str.lower().str.strip()

        # Initialize EasyOCR
        logging.info("Initializing EasyOCR Reader...")
        self.reader = easyocr.Reader(LANGS, model_storage_directory=MODEL_STORAGE_PATH, gpu=gpu)

    def extract_name(self, image_path: str) -> str:
        """
        Simple Tesseract-based approach to read 'Navn: ...' from the image.
        :returns: Extracted name (or 'Ukjent' if not found).
        """
        if not os.path.exists(image_path):
            logging.warning(f"Image not found: {image_path}")
            return "Ukjent"

        raw_text = pytesseract.image_to_string(
            image_path, lang="eng", config="--oem 1 --psm 6"
        )
        pattern = re.compile(r"(?:Navn|Name)\s*:\s*([A-Za-zÆØÅæøå \-]+)", re.IGNORECASE)
        match = pattern.search(raw_text)
        if match:
            return match.group(1).strip()
        return "Ukjent"

    def extract_sum_timer(self, image_path: str) -> Union [float , str]:
        """
        Finds "Sum timer til utbetaling" bounding box, then
        locates the nearest numeric bounding box to the right
        in the same row. Returns the numeric value or a warning string.
        """
        if not os.path.exists(image_path):
            return "⚠️ Could not extract hours"

        try:
            # 1) Perform OCR in detail mode => list of (bbox, text, confidence)
            ocr_results = self.reader.readtext(image_path, detail=1)

            # 2) Locate bounding box for "Sum timer til utbetaling"
            target_phrase = "sum timer til utbetaling"
            sum_timer_bbox = None
            sum_timer_center_x = None
            sum_timer_center_y = None

            for (bbox, text, confidence) in ocr_results:
                if fuzzy_match(text, target_phrase):
                    sum_timer_bbox = bbox
                    (sum_timer_center_x, sum_timer_center_y) = bbox_center(bbox)
                    logging.debug(f"Found phrase '{text}' @ {bbox} (conf={confidence:.2f})")
                    break

            if not sum_timer_bbox:
                return "⚠️ Could not extract hours"

            # 3) Search numeric bounding boxes in the same row (within ~20px) and to the right
            row_threshold = 30.0
            numeric_pattern = re.compile(r"^\d{1,3}([.,]\d+)?$")  # e.g. 10,00 or 10.00 or 10
            candidates = []

            for (bbox, text, conf) in ocr_results:
                text_clean = text.strip()
                if numeric_pattern.match(text_clean):
                    (cx, cy) = bbox_center(bbox)
                    if (cx > sum_timer_center_x) and (abs(cy - sum_timer_center_y) < row_threshold):
                        dx = cx - sum_timer_center_x
                        candidates.append((dx, text_clean))

            if not candidates:
                return "⚠️ Could not extract hours"

            # 4) Pick the bounding box that is horizontally closest to the phrase
            candidates.sort(key=lambda c: c[0])
            numeric_text = candidates[0][1]  # text of nearest candidate
            # 5) Convert e.g. "10,00" -> float 10.00
            numeric_value_str = numeric_text.replace(",", ".")
            return float(numeric_value_str)

        except Exception as e:
            logging.error(f"Error extracting sum timer from {image_path}: {e}")
            return "⚠️ Could not extract hours"

    def get_best_match(self, name: str) -> Union [str , None]:
        """
        Finds best fuzzy match for a given name in self.df["Name"].
        """
        normalized = name.lower().strip()
        csv_names = self.df["Name"].tolist()
        matches = get_close_matches(normalized, csv_names, n=1, cutoff=FUZZY_THRESHOLD)
        return matches[0] if matches else None

    def get_agreed_hours(self, matched_name: str) -> Union [float , None]:
        """
        Return total agreed hours = (agreed + extra - given away).
        """
        row = self.df[self.df["Name"] == matched_name]
        if row.empty:
            return None
        agreed_hours = float(row["agreed hours"].values[0])
        extra_hours = float(row["extra hours"].values[0])
        given_away = float(row["hours given away"].values[0])
        return agreed_hours + extra_hours - given_away

    def process_image(self, image_path: str):
        """
        Main routine to:
         1) Extract employee name
         2) Extract reported hours
         3) Compare to CSV
         4) Print an approval result
        """
        extracted_name = self.extract_name(image_path)
        reported_hours = self.extract_sum_timer(image_path)

        # Attempt to match the extracted name in our CSV
        matched_name = self.get_best_match(extracted_name)
        if matched_name:
            agreed_hours = self.get_agreed_hours(matched_name)
        else:
            agreed_hours = None

        # Determine status
        if isinstance(reported_hours, float) and (agreed_hours is not None):
            diff = abs(reported_hours - agreed_hours)
            if diff <= TOLERANCE:
                status = "✅ Godkjent"
            else:
                status = (f"❌ Ikke godkjent (Avtalt: {agreed_hours}, "
                          f"Rapportert: {reported_hours}, Diff: {diff:.2f})")
        elif matched_name is None:
            status = "⚠️ Name not found in database"
        else:
            status = "❌ Ikke godkjent (Kunne ikke hente timer eller avtalt tid)"

        # Log final
        logging.info("\n--- TIMELISTE GODKJENNING ---")
        logging.info(f"📂 File: {os.path.basename(image_path)}")
        logging.info(f"👤 Name: {extracted_name} (Matched: {matched_name})")
        logging.info("📅 Date: Extracted from image")
        logging.info(f"⏳ Reported Hours: {reported_hours}")
        logging.info(f"📋 Agreed Hours: {agreed_hours if agreed_hours is not None else '⚠️ Not found'}")
        logging.info(f"📌 Status: {status}")
        logging.info("----------------------------\n")


def verify_payroll(reference_csv: str = None, image_folder: str = None):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if reference_csv is None:
        reference_csv = os.path.join(script_dir, "..", "reference_data", "mars.csv")
    if image_folder is None:
        image_folder = os.path.join(script_dir, "..", "raw_pictures")

    try:
        processor = TimesheetProcessor(csv_path=reference_csv, gpu=False)
    except Exception as e:
        logging.error(f"Failed to initialize TimesheetProcessor: {e}")
        return

    if not os.path.isdir(image_folder):
        logging.error(f"Image folder not found: {image_folder}")
        return

    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        logging.warning("No image files found.")
        return

    for filename in image_files:
        image_path = os.path.join(image_folder, filename)
        logging.info(f"Processing: {image_path}")
        processor.process_image(image_path)


def main():
    verify_payroll()

if __name__ == "__main__":
    main()













































































# def main():
#     script_dir = os.path.dirname(os.path.abspath(__file__))

#     # 1) Setup paths
#     csv_path = os.path.join(script_dir, "..", "reference_data", "mars.csv")
#     image_folder = os.path.join(script_dir,".." ,"raw_pictures")

#     # 2) Initialize the TimesheetProcessor
#     try:
#         processor = TimesheetProcessor(csv_path=csv_path, gpu=False)
#     except FileNotFoundError as e:
#         logging.error(f"CSV file error: {e}")
#         return
#     except Exception as e:
#         logging.error(f"Failed to initialize TimesheetProcessor: {e}")
#         return

#     # 3) Get all .png, .jpg, or .jpeg from 'pictures' folder
#     if not os.path.isdir(image_folder):
#         logging.error(f"Image folder not found: {image_folder}")
#         return

#     image_files = [f for f in os.listdir(image_folder) 
#                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

#     if not image_files:
#         logging.warning("No .png, .jpg, or .jpeg files found in 'pictures' folder.")
#         return

#     # 4) Process each image
#     for filename in image_files:
#         image_path = os.path.join(image_folder, filename)
#         logging.info(f"Processing: {image_path}")
#         processor.process_image(image_path)


# if __name__ == "__main__":
#     main()
