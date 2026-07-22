import email
import sys

from .file_utils import decode_header_value, get_filename_from_message_part, get_or_rename_path
from .manifest import load_manifest, make_manifest_key, save_manifest


def walk_message_parts(
    msg_id, msg_data, output_dir, saved: int, skipped: int
) -> tuple[int, int]:
    manifest = load_manifest(output_dir)
    msg = email.message_from_bytes(msg_data[0][1])
    message_id = msg.get("Message-ID", f"unknown-{msg_id.decode()}")
    filename_occurrences: dict[str, int] = {}
    for part in msg.walk():
        if (result := get_filename_from_message_part(part)) is None:
            continue
        filename, original_filename = result

        occurrence = filename_occurrences.get(original_filename, 0)
        filename_occurrences[original_filename] = occurrence + 1
        key = make_manifest_key(message_id, original_filename, occurrence)
        if key in manifest:
            skipped += 1
            continue

        dest = get_or_rename_path(output_dir, filename)

        payload = part.get_payload(decode=True)
        if not isinstance(payload, bytes):
            raise TypeError("decode failed or part was multipart")
        dest.write_bytes(payload)

        subject = decode_header_value(msg.get("Subject", "(no subject)"))
        date = msg.get("Date", "(no date)")

        manifest[key] = {
            "saved_as": dest.name,
            "subject": subject,
            "date": date,
        }
        save_manifest(output_dir, manifest)

        sys.stdout.write(
            f'  [{saved + 1}] {dest.name}  (subject: "{subject}", date: {date})\n'
        )
        saved += 1
    return saved, skipped
