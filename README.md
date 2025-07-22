# PROVE  
**Payroll Review & OCR Verification Engine**

---

## Overview

**PROVE** automates payroll validation by extracting reported hours from scanned images or PDF attachments and verifying them against internal reference records. The system combines EasyOCR, Tesseract, and structured validation to ensure fast, repeatable, and auditable payroll checks.

---

## 📌 Features

- ✅ **Automatic Email Scraping & Image Extraction**: Downloads payroll reports from finance emails within a specified period.
- ✅ **OCR-Based Data Extraction**: Reads employee names and reported hours directly from images using EasyOCR and Tesseract.
- ✅ **Cross-Verification with Reference Data**: Compares extracted data to a trusted CSV reference.
- ✅ **Discrepancy Reporting**: Immediate terminal outputs highlighting approvals, discrepancies, or data errors.
- ✅ **Simple CLI Interface**: Single-command pipeline from email ingestion to verification.
- ✅ **Modular Codebase**: Cleanly separated ingestion and processing logic for maintainability.

---

## 🚀 Quickstart

### Requirements

- Python ≥ 3.9
- Tesseract OCR installed and accessible via PATH
- Install Python packages:
    ```bash
    pip install -r requirements.txt
    ```

---

### Folder Structure

reference_data/ # Contains the internal reference CSV (e.g., mars.csv)
raw_pictures/ # Stores downloaded payroll report images
ingestion/ # Email fetching and image extraction modules
processing/ # Verification and analysis modules

how to run 

python run_prove.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD
