import argparse
import imaplib
import os
import sys
from pathlib import Path

from .utils import fetch_attachments, load_accounts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download PDF attachments from one or more Gmail accounts."
    )
    parser.add_argument(
        "--email",
        # required=True,
        default=None,
        help="Gmail address to process (must exist in the accounts file)",
    )
    parser.add_argument(
        "--accounts-file",
        type=Path,
        default=None,
        help="Path to JSON accounts file (or set GMAIL_ACCOUNTS_FILE env var)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Local directory to save PDFs",
    )
    parser.add_argument(
        "--imap-host",
        default="imap.gmail.com",
        help="IMAP server (default: imap.gmail.com)",
    )
    args = parser.parse_args()

    accounts_file = args.accounts_file or os.environ.get("GMAIL_ACCOUNTS_FILE")
    if not accounts_file:
        sys.stderr.write(
            "Error: provide --accounts-file or set GMAIL_ACCOUNTS_FILE env var.\n"
        )
        sys.exit(1)
    accounts_file = Path(accounts_file)
    accounts = load_accounts(accounts_file)

    if args.email:
        accounts = [next((a for a in accounts if a["email"] == args.email), None)]
        if not [accounts]:
            sys.stderr.write(
                f"Error: '{args.email}' not found in {accounts_file}\n.",
            )
            sys.exit(1)

    total = 0
    for account in accounts:
        sys.stdout.write(f"{account['email']} ...\n")
        try:
            saved = fetch_attachments(
                account["email"],
                account["password"],
                args.output_dir,
                imap_host=args.imap_host,
            )
        except imaplib.IMAP4.error as e:
            sys.stderr.write(f"IMAP error: {e}\n")
            sys.exit(1)
        total += saved
        sys.stdout.write(
            f"  {account['email']} done. {saved} PDF(s) saved to {args.output_dir}\n"
        )

    sys.stdout.write(f"All done. {total} PDF(s) saved to {args.output_dir}\n")
