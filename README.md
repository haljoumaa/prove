# PROVE  
**Payroll Review & OCR Verification Engine**

---

## Overview

**PROVE** is an automated payroll validation platform that eliminates manual cross-checking by extracting reported hours directly from scanned documents and emails, then validating them against authoritative internal records. The system uses a modular pipeline—comprising automated email ingestion, OCR-based extraction (EasyOCR with Tesseract fallback), and multi-stage data validation—to deliver a fast, transparent, and fully auditable process. PROVE’s ongoing refactor introduces self-service digital logging for mentors, further removing human bottlenecks and enabling real-time payroll oversight. Designed for extensibility and compliance, PROVE reduces error rates, accelerates payroll cycles, and establishes a new standard for scalable, transparent payroll management.
---

## Features

- **Automatic Email Scraping & Image Extraction**: Downloads payroll reports from finance emails within a specified period.  
- **OCR‑Based Data Extraction**: Reads employee names and reported hours directly from images using EasyOCR and Tesseract.  
- **Cross‑Verification with Reference Data**: Compares extracted data to a trusted CSV reference.  
- **Discrepancy Reporting**: Immediate terminal outputs highlighting approvals, discrepancies, or data errors.  
- **Simple CLI Interface**: Single‑command pipeline from email ingestion to verification.  
- **Modular Codebase**: Cleanly separated ingestion and processing logic for maintainability.  

## Architecture

PROVE’s architecture is fully modular, separating email ingestion, attachment extraction, OCR processing, and data validation into independent components. This ensures that each part of the pipeline can be tested, improved, or replaced without impacting the rest of the system.

- **Email Ingestion:** Downloads relevant messages and attachments based on date, sender, and subject filters.
- **Attachment Processing:** Extracts and stores scanned payroll reports from multiple formats (PDF, JPEG, PNG, etc).
- **OCR Engine:** Utilizes both EasyOCR and Tesseract for robust recognition across varied document layouts.
- **Validation Engine:** Compares extracted names/hours to a reference CSV, flags mismatches, and outputs results.
- **Reporting:** Summarizes findings in the terminal, highlighting both approvals and any discrepancies for further review.

## Roadmap

- **PROVE Portal (Coming Soon):** A self-service web platform enabling mentors and employees to log their own hours, review submissions, and manage corrections directly. The portal will integrate with the backend for real-time validation and auditability.
- Integration with cloud storage and scalable databases.
- Enhanced anomaly detection and pattern analysis.
- Automated escalation for unresolved discrepancies.

---

## Getting Started

The system can be executed via a single CLI command. Configuration, including reference file locations and email access credentials, is handled via environment variables.

Instructions and usage details will follow in upcoming sections.

---

## License

PROVE is released under an MIT license. See `LICENSE` for details.

