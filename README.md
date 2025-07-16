# PROVE

**Payroll Review & OCR Verification Engine**

---

## What is PROVE?

PROVE automates payroll document review using OCR. It extracts values from scanned payslips or payroll reports and checks them against internal records, making it easier to spot errors and inconsistencies in payroll processing.

---

## Features

- OCR data extraction from PDF/image payroll documents
- Configurable validation against CSV/system exports
- Discrepancy reporting (CSV/JSON)
- Audit logging for compliance and traceability
- Modular architecture: ingestion, extraction, validation, reporting

---

## Getting Started

### Requirements

- Python >= 3.9
- Tesseract OCR installed and in PATH
- See `requirements.txt` for Python dependencies

### Setup

```sh
git clone https://github.com/your-org/PROVE.git
cd PROVE
pip install -r requirements.txt