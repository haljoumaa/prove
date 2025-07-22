# PROVE  
_**Payroll Review & OCR Verification Engine**_

---

## Overview

**PROVE** is an automated payroll validation platform that eliminates manual cross-checking by extracting reported hours directly from scanned documents and emails, then validating them against authoritative internal records. The system uses a modular pipeline, comprising automated email ingestion, OCR-based extraction (EasyOCR with Tesseract fallback), and data validation to deliver a fast, transparent, and fully auditable process. PROVE originated from my role as project manager at ENT3R, where I routinely spent an average of 45 minutes processing and approving payrolls. Designed for extensibility and compliance, PROVE reduces error rates, accelerates payroll cycles, and establishes a new standard for scalable, transparent payroll management.

---

## Features

- **End-to-End Payroll Data Pipeline**: Automates payroll report retrieval, OCR-based extraction, cross-checking, and discrepancy reporting.
- **Automated Email and Attachment Handling**: Scrapes finance emails by period and extracts relevant payroll images and files.
-	**Multi-Engine OCR Extraction**: Uses both EasyOCR and Tesseract to extract names and hours from diverse document formats.
-	**Reference-Based Verification**: Cross-validates extracted results against a trusted CSV dataset, flagging inconsistencies.
-	**Real-Time Discrepancy Reporting**: Immediately identifies approvals, errors, and mismatches via terminal summaries.
-	**Single-Command CLI Operation**: Runs the entire workflow through a streamlined, user-facing command-line interface.

## Architecture

PROVE is structured as a modular pipeline, enforcing separation of concerns for robustness and testability. Each subsystem can be independently maintained or upgraded.
-	**Ingestion Module**: Filters and downloads emails and attachments by configurable rules (date, sender, subject).
-	**Attachment Handler**: Normalizes and stores incoming payroll documents from supported formats (PDF, JPEG, PNG).
-	**OCR Processor**: Integrates EasyOCR and Tesseract for dual-path recognition, addressing layout variability.
-	**Validation Module**: Matches extracted data with reference records and flags all discrepancies or anomalies.
-	**Reporting Engine**: Consolidates results, providing actionable summaries and immediate feedback to the user.
 
## Roadmap

- **PROVE Portal (Coming Soon):** Roadmap
A web-based platform allowing mentors to independently register hours, manage shift changes, review timesheets, and monitor their own payroll data. By shifting data entry and verification to the users themselves, the portal eliminates the need for manual CSV handling and intermediary data processing. This transition enables near-complete automation of the payroll workflow, reduces administrative bottlenecks, and increases transparency and auditability across the system..

---

## Getting Started

The system can be executed via a single CLI command. Configuration, including reference file locations and email access credentials, is handled via environment variables.

>python3 run_prove.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD


