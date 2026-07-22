import contextlib
import imaplib
import sys
from pathlib import Path

from .connect import connect, reconnect_with_retry
from .message import walk_message_parts

STATUS_OK = "OK"


def fetch_attachments(
    email_address: str,
    password: str,
    output_dir: Path,
    *,
    imap_host: str = "imap.gmail.com",
) -> int:
    """Fetch mail message and download the PDF attachments"""
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.stdout.write(f"Connecting to {imap_host} as {email_address} ...\n")
    mail = connect(email_address, password, imap_host)

    sys.stdout.write("Searching for messages ...\n")
    status, data = mail.search(None, "ALL")
    if status != STATUS_OK:
        sys.stdout.write("Search failed.\n")
        mail.logout()
        return 0

    message_ids = data[0].split()
    sys.stdout.write(f"Found {len(message_ids)} messages. Scanning for PDF attachments ...\n")

    saved = 0
    skipped = 0
    i = 0
    while i < len(message_ids):
        msg_id = message_ids[i]
        i += 1

        # get message data
        try:
            status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as e:
            mail = reconnect_with_retry(e, email_address, password, imap_host, msg_index=i)
            status, data = mail.search(None, "ALL")
            if status != STATUS_OK:
                sys.stdout.write("Search failed after reconnect.\n")
                break
            message_ids = data[0].split()
            i -= 1
            continue
        if status != STATUS_OK:
            continue

        # walk through message data
        saved, skipped = walk_message_parts(msg_id, msg_data, output_dir, saved, skipped)

        if i % 100 == 0:
            sys.stdout.write(f"  ... scanned {i}/{len(message_ids)} messages\n")

    with contextlib.suppress(imaplib.IMAP4.error, OSError):
        mail.logout()

    sys.stdout.write(
        f"Done with {email_address}. {saved} PDF(s) saved, {skipped} skipped.\n\n"
    )
    return saved
