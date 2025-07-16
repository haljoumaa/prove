import imaplib
import email
import os
import logging
from email.header import decode_header
from dotenv import load_dotenv 
import os

load_dotenv()
import os

print("IMAP_HOST:", os.getenv("IMAP_HOST"))
print("IMAP_USER:", os.getenv("IMAP_USER"))
print("IMAP_PASSWORD:", os.getenv("IMAP_PASSWORD"))
print("FINANCE_SENDER:", os.getenv("FINANCE_SENDER"))

# --- Configuration ---
IMAP_HOST = os.getenv('webmail.ent3r.no')
IMAP_USER = os.getenv('Bergen.hvl@ent3r.no')
IMAP_PASSWORD = os.getenv('5YqfKwvPlHU')
FINANCE_SENDER = os.getenv('FINANCE_SENDER', 'may.sandsta@hvl.no')
DOWNLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'pictures')
)

logging.basicConfig(
    format='%(levelname)s | %(asctime)s | %(funcName)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def download_finance_attachments():
    """
    Connects to IMAP, fetches unread emails from the finance sender,
    downloads image/PDF attachments to DOWNLOAD_FOLDER, marks as read.
    """
    # Sanity check for required credentials
    if not (IMAP_HOST and IMAP_USER and IMAP_PASSWORD):
        logger.error("Missing IMAP_HOST, IMAP_USER, or IMAP_PASSWORD. Export as env variables.")
        return

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(IMAP_USER, IMAP_PASSWORD)
    except Exception as e:
        logger.error(f"IMAP login failed: {e}")
        return

    try:
        mail.select('INBOX')
        search_criterion = f'(UNSEEN FROM "{FINANCE_SENDER}")'
        status, messages = mail.search(None, search_criterion)
        if status != 'OK':
            logger.error("Email search failed")
            return

        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                logger.warning(f"Failed to fetch email {num}")
                continue

            msg = email.message_from_bytes(data[0][1])
            subject = _decode_header_field(msg.get('Subject', 'no-subject'))
            date = msg.get('Date', '').replace(':', '-').replace(' ', '_')

            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                if not filename:
                    continue

                lower = filename.lower()
                if not lower.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    continue

                # Build unique filename
                unique = f"{date}__{subject}__{filename}".replace('/', '_').replace('\\', '_')
                path = os.path.join(DOWNLOAD_FOLDER, unique)
                if os.path.exists(path):
                    logger.info(f"Skipping existing: {unique}")
                    continue

                try:
                    with open(path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    logger.info(f"Downloaded: {unique}")
                except Exception as e:
                    logger.error(f"Write failed for {unique}: {e}")

            # Mark email as read/seen
            mail.store(num, '+FLAGS', '\\Seen')
        mail.expunge()

    except Exception as e:
        logger.error(f"IMAP processing error: {e}")
    finally:
        try:
            mail.logout()
        except Exception:
            pass

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

if __name__ == "__main__":
    download_finance_attachments()