# PROVE  
**Payroll Review & OCR Verification Engine**

---

## Overview

**PROVE** automates payroll validation by extracting reported hours from scanned images or PDF attachments and verifying them against internal reference records. The system combines EasyOCR, Tesseract, and structured validation to ensure fast, repeatable, and auditable payroll checks.

---

## Features

- **Automatic Email Scraping & Image Extraction**: Downloads payroll reports from finance emails within a specified period.  
- **OCR‑Based Data Extraction**: Reads employee names and reported hours directly from images using EasyOCR and Tesseract.  
- **Cross‑Verification with Reference Data**: Compares extracted data to a trusted CSV reference.  
- **Discrepancy Reporting**: Immediate terminal outputs highlighting approvals, discrepancies, or data errors.  
- **Simple CLI Interface**: Single‑command pipeline from email ingestion to verification.  
- **Modular Codebase**: Cleanly separated ingestion and processing logic for maintainability.  

