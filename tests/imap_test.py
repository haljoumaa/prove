import imaplib
import email
import os
from dotenv import load_dotenv
from email.header import decode_header

load_dotenv()

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')

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

    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()

    latest_date = None
    latest_email_id = None

    for eid in email_ids[-50:]:  # only check last 50 to speed up
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
        print(f"✅ Latest by date subject: {subject}")
        print(f"✅ From: {sender}")
        print(f"✅ Date: {latest_date}")
    else:
        print("❌ No valid emails found.")

    mail.logout()

except Exception as e:
    print(f"❌ Error: {e}")
