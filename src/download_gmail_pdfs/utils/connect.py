import imaplib
import sys
import time

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10


def connect(
    email_address: str,
    password: str,
    imap_host: str,
) -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(email_address, password)
    mail.select('"[Gmail]/All Mail"')
    return mail


def reconnect_with_retry(
    original_error: Exception,
    email_address: str,
    password: str,
    imap_host: str,
    *,
    msg_index: int,
) -> imaplib.IMAP4_SSL:
    for attempt in range(1, MAX_RETRIES + 1):
        sys.stdout.write(
            f"\n  Connection lost at message {msg_index} ({original_error}). "
            f"Retrying in {RETRY_DELAY_SECONDS}s (attempt {attempt}/{MAX_RETRIES}) ...\n"
        )
        time.sleep(RETRY_DELAY_SECONDS)
        try:
            mail = connect(email_address, password, imap_host)
        except (imaplib.IMAP4.error, OSError) as e:
            original_error = e
        else:
            sys.stdout.write("  Reconnected.\n\n")
            return mail

    sys.stderr.write(f"Failed to reconnect after {MAX_RETRIES} attempts.\n")
    sys.exit(1)
