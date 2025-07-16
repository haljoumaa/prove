import os
import re
import logging
import cv2
import numpy as np
import pandas as pd
from difflib import get_close_matches, SequenceMatcher
import pytesseract
import easyocr
from glob import glob 
import matplotlib.pylab as plt


MODEL_STORAGE_PATH = '~/.EasyOCR/model/'
LANGS = ['en', 'no']  
TOLERANCE = 0.1       
FUZZY_THRESHOLD = 0.6 


logging.basicConfig(
    format='%(levelname)s | %(asctime)s | %(funcName)s | %(message)s',
    level=logging.INFO  
)


def fuzzy_contains(haystack: str, needle: str, threshold: float = FUZZY_THRESHOLD) -> bool:
   
    haystack_tokens = haystack.lower().split()
    needle_lower = needle.lower()
    for token in haystack_tokens:
        ratio = SequenceMatcher(None, token, needle_lower).ratio()
        if ratio >= threshold:
            return True
    return False


def preprocess_image(image_path: str):
   
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        logging.warning(f"Unable to read image at: {image_path}")
        return None
    image = cv2.GaussianBlur(image, (3, 3), 0)
   
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_total_hours(image_path: str, reader: easyocr.Reader):
   
    try:
       
        processed_image = preprocess_image(image_path)
        if processed_image is None:
            return "⚠️ Could not extract hours"

        # EasyOCR detail=0 returns just the text lines
        extracted_lines = reader.readtext(processed_image, detail=0)
        extracted_lines = [line.strip() for line in extracted_lines if line.strip()]

        logging.debug(f"OCR extracted (EasyOCR) from {image_path}: {extracted_lines}")

     
        target_phrase = "sum timer til utbetaling"
        for i, text_line in enumerate(extracted_lines):
            if fuzzy_contains(text_line, target_phrase):
                # Scan subsequent lines for a numeric pattern
                for j in range(i, len(extracted_lines)):
                    # Pattern that captures integer or decimal (e.g., 9 or 9.00 or 9,00)
                    num_match = re.search(r"(\d{1,3}([.,]\d{1,2})?)", extracted_lines[j])
                    if num_match:
                        hours_str = num_match.group(1).replace(",", ".")
                        try:
                            return float(hours_str)
                        except ValueError:
                            return "⚠️ Could not extract hours"
        
        return "⚠️ Could not extract hours"

    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return "⚠️ Could not extract hours"


def get_best_match(name: str, df: pd.DataFrame):
    
    normalized_name = name.lower().strip()
    csv_names = df["Name"].tolist()
    matches = get_close_matches(normalized_name, csv_names, n=1, cutoff=FUZZY_THRESHOLD)
    return matches[0] if matches else None


def get_agreed_hours(matched_name: str, df: pd.DataFrame):
   
    row = df[df["Name"] == matched_name]
    if not row.empty:
        agreed_hours = float(row["agreed hours"].values[0])
        extra_hours = float(row["extra hours"].values[0])
        given_away_hours = float(row["hours given away"].values[0])
        return agreed_hours + extra_hours - given_away_hours
    return None


def extract_name_with_tesseract(image_path: str) -> str:
   
    raw_text = pytesseract.image_to_string(image_path, lang="eng", config="--oem 1 --psm 6")
   
    name_pattern = re.compile(r"(?:Navn|Name)\s*:\s*([A-Za-zÆØÅæøå \-]+)", re.IGNORECASE)
    match = name_pattern.search(raw_text)
    if match:
        return match.group(1).strip()

    return "Ukjent"



def main():

  
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_folder = os.path.join(script_dir, "pictures")
    csv_path = os.path.join(script_dir, "csv", "mars.csv")

    if not os.path.exists(csv_path):
        logging.error(f"CSV file not found at: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df["Name"] = df["Name"].astype(str).str.lower().str.strip()

    
    try:
        reader = easyocr.Reader(LANGS, model_storage_directory=MODEL_STORAGE_PATH, gpu=False)
    except Exception as e:
        logging.error(f"Failed to initialize EasyOCR Reader: {e}")
        return

    
    if not os.path.exists(image_folder):
        logging.error(f"Image folder not found at {image_folder}")
        return

    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        logging.warning("No images found in 'pictures' folder.")
        return

  
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        logging.info(f"Processing image: {image_path}")

        reported_hours = extract_total_hours(image_path, reader)

        extracted_name = extract_name_with_tesseract(image_path)
        matched_name = get_best_match(extracted_name, df)

        
        if matched_name:
            agreed_hours = get_agreed_hours(matched_name, df)
            if isinstance(reported_hours, float) and agreed_hours is not None:
                
                hour_difference = abs(reported_hours - agreed_hours)
                if hour_difference <= TOLERANCE:
                    approval_status = "✅ Godkjent"
                else:
                    approval_status = (
                        f"❌ Ikke godkjent "
                        f"(Avtalt: {agreed_hours}, Rapportert: {reported_hours}, "
                        f"Diff: {hour_difference:.2f})"
                    )
            else:
                approval_status = (
                    "❌ Ikke godkjent "
                    "(Kunne ikke hente timer eller avtalt tid fra CSV)"
                )
        else:
            approval_status = "⚠️ Name not found in database"

        
        logging.info("\n--- TIMELISTE GODKJENNING ---")
        logging.info(f"📂 File: {image_file}")
        logging.info(f"👤 Name: {extracted_name} (Matched: {matched_name})")
        logging.info("📅 Date: Extracted from image")
        logging.info(f"⏳ Reported Hours: {reported_hours}")
        logging.info(
            f"📋 Agreed Hours: {agreed_hours if matched_name and agreed_hours is not None else '⚠️ Not found'}"
        )
        logging.info(f"📌 Status: {approval_status}")
        logging.info("----------------------------\n")

if __name__ == "__main__":
    main()
