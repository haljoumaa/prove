# PROVE  
_**Payroll Review & OCR Verification Engine**_

---

## Overview

**PROVE** is an automated payroll validation platform that eliminates manual cross-checking by extracting reported hours directly from scanned documents and emails, then validating them against authoritative internal records. The system uses a modular pipeline, comprising automated email ingestion, OCR-based extraction (EasyOCR with Tesseract fallback), and data validation to deliver a fast, transparent, and fully auditable process. PROVE originated from my role as project manager at ENT3R, where I routinely spent an average of 45 minutes processing and approving payrolls. Designed for extensibility and compliance, PROVE reduces error rates, accelerates payroll cycles, and establishes a new standard for scalable, transparent payroll management.

---

## System Overview

The architecture is designed for robustness, maintainability, and clear separation of concerns; each subsystem can be independently maintained or upgraded.
- **End-to-End Payroll Data Pipeline**: Automates retrieval of payroll reports from finance emails and processes all steps from ingestion to verification in a single command-line operation.
- **Configurable Ingestion Module**: Filters and downloads emails and attachments based on specified criteria (date, sender, subject).
-	**Attachment Handler**: Normalizes and stores incoming documents in supported formats (PDF, JPEG, PNG).
-	**Dual-Engine OCR Processor**: Integrates EasyOCR and Tesseract for reliable extraction of names and hours across varied document layouts.
-	**Reporting Engine**: Provides immediate, actionable feedback via terminal summaries, clearly identifying approvals, errors, and mismatches.
-	**Reference-Based Validation**: Cross-checks extracted data against a trusted CSV dataset, systematically flagging discrepancies or anomalies.
-	**Fully Modular Design**: Each stage, ingestion, attachment handling, OCR, validation, and reporting operates independently, allowing targeted improvements and reliable maintenance.

 
## Roadmap

- **PROVE Portal (Coming Soon):** Roadmap
A web-based platform allowing mentors to independently register hours, manage shift changes, review timesheets, and monitor their own payroll data. By shifting data entry and verification to the users themselves, the portal eliminates the need for manual CSV handling and intermediary data processing. This transition enables near-complete automation of the payroll workflow, reduces administrative bottlenecks, and increases transparency and auditability across the system..



>The system can be executed via a single CLI command. Configuration, including reference file locations and email access credentials, is handled via environment variables;
> python3 run_prove.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD



