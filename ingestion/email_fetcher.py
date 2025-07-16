import imaplib
import email
import logging
import os
from email.header import decode_header
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
FINANCE_SENDER = os.getenv('FINANCE_SENDER')

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

def get_finance_emails_in_period(start_date, end_date):
    """
    Returns a list of email.message.Message objects from FINANCE_SENDER within the date range.
    Input dates: YYYY-MM-DD (ISO format).
    """
    if not all([IMAP_HOST, IMAP_USER, IMAP_PASSWORD, FINANCE_SENDER]):
        logger.error("Missing IMAP configuration or finance sender address.")
        return []

    try:
        # Convert input dates to IMAP-compatible format (e.g., 16-Jul-2025)
        since_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d-%b-%Y')
        before_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d-%b-%Y')

        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(IMAP_USER, IMAP_PASSWORD)
        mail.select('INBOX')

        logger.info(f"Fetching emails from {FINANCE_SENDER} between {since_date} and {before_date}")

        search_query = f'(FROM "{FINANCE_SENDER}" SINCE {since_date} BEFORE {before_date})'
        status, messages = mail.search(None, search_query)

        email_ids = messages[0].split()
        logger.info(f"✅ Found {len(email_ids)} matching email(s).")

        all_emails = []
        for eid in email_ids:
            status, data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                logger.warning(f"Failed to fetch email ID {eid.decode()}")
                continue
            msg = email.message_from_bytes(data[0][1])
            all_emails.append(msg)

        mail.logout()
        logger.info(f"✅ Completed fetching {len(all_emails)} emails.")
        return all_emails

    except Exception as e:
        logger.error(f"❌ IMAP error: {e}")
        return []

if __name__ == "__main__":
    # Example interactive use
    start = input("Start date (YYYY-MM-DD): ").strip()
    end = input("End date (YYYY-MM-DD): ").strip()

    emails = get_finance_emails_in_period(start, end)
    if emails:
        for idx, msg in enumerate(emails):
            subject = _decode_header_field(msg.get('Subject', 'no-subject'))
            sender = msg.get('From')
            date = msg.get('Date')
            print(f"\n📧 Email #{idx+1}:\nSubject: {subject}\nFrom: {sender}\nDate: {date}")
        print(f"\n✅ Total emails fetched: {len(emails)}")
    else:
        print("❌ No valid finance emails found in the given period.")
