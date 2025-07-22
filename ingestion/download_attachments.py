import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from ingestion.fetch_emails import get_finance_emails_in_period

import logging
from email.header import decode_header

# Destination folder
PICTURE_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'raw_pictures')
)

# Logging setup
logging.basicConfig(
    format='%(levelname)s | %(asctime)s | %(funcName)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def _decode_header_field(value):
    if not value:
        return ''
    decoded = decode_header(value)
    header = ''
    for part, enc in decoded:
        if isinstance(part, bytes):
            header += part.decode(enc or 'utf-8', errors='ignore')
        else:
            header += part
    return header

def extract_attachments(email_msg):
    os.makedirs(PICTURE_FOLDER, exist_ok=True)

    subject = _decode_header_field(email_msg.get('Subject', 'no-subject'))
    date = email_msg.get('Date', '').replace(':', '-').replace(' ', '_')

    attachments = []
    for part in email_msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue

        filename = part.get_filename()
        if not filename:
            continue

        filename = _decode_header_field(filename).replace('/', '_').replace('\\', '_')
        ext = filename.lower().split('.')[-1]

        if ext not in ['png', 'jpg', 'jpeg', 'pdf']:
            logger.info(f"Skipping non-image attachment: {filename}")
            continue

        payload = part.get_payload(decode=True)
        if not payload:
            logger.info(f"Skipping empty attachment: {filename}")
            continue

        attachments.append((filename, payload))

    if len(attachments) > 1:
        logger.info("Skipping last attachment (likely logo/footer).")
        attachments = attachments[:-1]

    count = 0
    for filename, payload in attachments:
        unique_name = f"{date}__{subject}__{filename}".replace(' ', '_')
        full_path = os.path.join(PICTURE_FOLDER, unique_name)

        if os.path.exists(full_path):
            logger.info(f"Already exists, skipping: {unique_name}")
            continue

        try:
            with open(full_path, 'wb') as f:
                f.write(payload)
            logger.info(f"✅ Downloaded: {unique_name}")
            count += 1
        except Exception as e:
            logger.error(f"❌ Failed to save {unique_name}: {e}")

    logger.info(f"✅ Finished email ({subject}): {count} file(s) downloaded.")
    return count


def download_pics_main(start_date: str, end_date: str):
    emails = get_finance_emails_in_period(start_date, end_date)
    if not emails:
        logger.warning("❌ No valid finance emails found in period.")
        return
    total_downloaded = 0
    for idx, email_msg in enumerate(emails, 1):
        logger.info(f"📧 Processing email {idx}/{len(emails)}...")
        count = extract_attachments(email_msg)
        total_downloaded += count
    logger.info(f"\n✅ All done. Total files downloaded: {total_downloaded}")

if __name__ == "__main__":
    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()
    download_pics_main(start_date, end_date)


































































































# if __name__ == "__main__":
#     start_date = input("Start date (YYYY-MM-DD): ").strip()
#     end_date = input("End date (YYYY-MM-DD): ").strip()

#     emails = get_finance_emails_in_period(start_date, end_date)
#     if not emails:
#         print("❌ No valid finance emails found in period.")
#         exit(0)

#     total_downloaded = 0
#     for idx, email_msg in enumerate(emails, 1):
#         logger.info(f"📧 Processing email {idx}/{len(emails)}...")
#         count = extract_attachments(email_msg)
#         total_downloaded += count

#     print(f"\n✅ All done. Total files downloaded: {total_downloaded}")
