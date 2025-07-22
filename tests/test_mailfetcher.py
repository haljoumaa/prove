import imaplib
import email
import os
from dotenv import load_dotenv
from email.header import decode_header

load_dotenv()

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
FINANCE_SENDER = os.getenv('FINANCE_SENDER')

def decode_subject(subject):
    decoded = decode_header(subject)
    result = ''
    for part, encoding in decoded:
        if isinstance(part, bytes):
            result += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            result += part
    return result

try:
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    mail.select('INBOX')

    search_criterion = f'(FROM "{FINANCE_SENDER}")'
    status, messages = mail.search(None, search_criterion)
    email_ids = messages[0].split()

    if not email_ids:
        print(f"❌ No emails found from {FINANCE_SENDER}")
        mail.logout()
        exit(0)

    latest_date = None
    latest_email_id = None

    for eid in email_ids[-50:]:
        status, data = mail.fetch(eid, '(BODY.PEEK[HEADER.FIELDS (DATE)])')
        if status != 'OK':
            continue
        msg = email.message_from_bytes(data[0][1])
        date_str = msg.get("Date")
        try:
            date_parsed = email.utils.parsedate_to_datetime(date_str)
            if latest_date is None or date_parsed > latest_date:
                latest_date = date_parsed
                latest_email_id = eid
        except Exception:
            continue

    if latest_email_id:
        status, data = mail.fetch(latest_email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        subject = decode_subject(msg.get("Subject", "No Subject"))
        sender = msg.get("From")
        print(f"✅ Latest Finance Email Subject: {subject}")
        print(f"✅ From: {sender}")
        print(f"✅ Date: {latest_date}")
    else:
        print(f"❌ Found emails from {FINANCE_SENDER} but none with valid dates.")

    mail.logout()

except Exception as e:
    print(f"❌ Error: {e}")
